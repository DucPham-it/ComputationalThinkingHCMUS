"""Filtering stage for recommendation pipeline.

Owner:
- TV4: Candidate Filtering.

File input:
- Candidate places from external APIs and/or local database.
- Parsed NLP fields from TV3.
- Explicit UI filters from TV2/F1.
- User location when distance filtering is available.

File output:
- A normalized filter plan.
- Narrowed candidate place list before TV5 ranking.
"""

from typing import Any

from app.utils.distance import get_distance_between_points


def _is_present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    if isinstance(value, (list, tuple, set, dict)) and len(value) == 0:
        return False
    return True


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value if item is not None]


def normalize_budget_level(value: Any) -> str | None:
    """Normalize frontend/NLP budget aliases into one backend contract.

    Input:
    - value: low/medium/high or common aliases such as cheap/premium.

    Output:
    - "low", "medium", "high", or None.
    """
    if not value:
        return None

    normalized = str(value).strip().lower()
    aliases = {
        "cheap": "low",
        "budget": "low",
        "binh dan": "low",
        "bình dân": "low",
        "re": "low",
        "rẻ": "low",
        "mid": "medium",
        "moderate": "medium",
        "average": "medium",
        "premium": "high",
        "expensive": "high",
        "luxury": "high",
        "cao cap": "high",
        "cao cấp": "high",
    }
    normalized = aliases.get(normalized, normalized)
    return normalized if normalized in {"low", "medium", "high"} else None


def build_filter_plan(nlp_fields: dict[str, Any] | None, ui_filters: dict[str, Any] | None) -> dict[str, Any]:
    """Merge NLP fields and UI filters into one filter plan.

    Owner:
    - TV4.

    Input:
    - nlp_fields: output from TV3 parse/extract helpers.
    - ui_filters: explicit frontend values from TV2/F1.

    Output:
    - dict accepted by apply_filters:
      max_distance_km, allowed_types, require_open_now, min_rating,
      budget_level, companion_type, time_slot, source_map.

    Rule:
    - explicit UI filters override NLP-derived filters.
    """
    nlp_fields = nlp_fields or {}
    ui_filters = ui_filters or {}

    field_aliases = {
        "max_distance_km": ("max_distance_km", "distance_hint_km"),
        "allowed_types": ("allowed_types", "preferred_types"),
        "budget_level": ("budget_level",),
        "companion_type": ("companion_type",),
        "time_slot": ("time_slot", "start_time"),
        "require_open_now": ("require_open_now",),
        "min_rating": ("min_rating",),
    }
    plan: dict[str, Any] = {"source_map": {}}

    for output_key, aliases in field_aliases.items():
        chosen_value = None
        chosen_source = None

        for alias in aliases:
            if _is_present(ui_filters.get(alias)):
                chosen_value = ui_filters[alias]
                chosen_source = "ui"
                break

        if chosen_source is None:
            for alias in aliases:
                if _is_present(nlp_fields.get(alias)):
                    chosen_value = nlp_fields[alias]
                    chosen_source = "nlp"
                    break

        if chosen_source is None:
            continue

        if output_key == "budget_level":
            chosen_value = normalize_budget_level(chosen_value)
            if chosen_value is None:
                continue
        elif output_key in {"max_distance_km", "min_rating"}:
            chosen_value = _as_float(chosen_value)
            if chosen_value is None:
                continue
        elif output_key == "allowed_types":
            chosen_value = _as_list(chosen_value)
            if not chosen_value:
                continue

        plan[output_key] = chosen_value
        plan["source_map"][output_key] = chosen_source

    return plan


def apply_filters(
    places: list[dict[str, Any]],
    max_distance_km: float | None = None,
    allowed_types: list[str] | None = None,
    require_open_now: bool = False,
    min_rating: float | None = None,
    budget_level: str | None = None,
    *,
    nlp_fields: dict[str, Any] | None = None,
    ui_filters: dict[str, Any] | None = None,
    user_location: dict[str, Any] | None = None,
    companion_type: str | None = None,
    time_slot: str | None = None,
    preferred_types: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Filter candidate places using stable, backward-compatible arguments.

    Input:
    - places: candidate place dicts.
    - max_distance_km/allowed_types/require_open_now/min_rating/budget_level:
      current recommender.py call contract.
    - nlp_fields/ui_filters/user_location: optional TV4 filter-plan contract.
    - companion_type/time_slot/preferred_types: optional soft filter fields.

    Output:
    - filtered list. Missing optional metadata does not crash the pipeline.
    """
    plan = build_filter_plan(nlp_fields, ui_filters) if nlp_fields or ui_filters else {}

    effective_distance = _as_float(max_distance_km)
    if effective_distance is None:
        effective_distance = plan.get("max_distance_km")

    effective_types = _as_list(allowed_types) or _as_list(preferred_types) or _as_list(plan.get("allowed_types"))
    effective_open_now = bool(require_open_now or plan.get("require_open_now"))

    effective_min_rating = _as_float(min_rating)
    if effective_min_rating is None:
        effective_min_rating = plan.get("min_rating")

    effective_budget = normalize_budget_level(budget_level) or plan.get("budget_level")
    effective_companion = companion_type or plan.get("companion_type")
    effective_time_slot = time_slot or plan.get("time_slot")

    filtered = list(places)

    if effective_distance is not None:
        filtered = apply_distance_filter(
            filtered,
            max_distance_km=effective_distance,
            user_location=user_location,
        )

    if effective_types:
        filtered = apply_preferred_types_filter(filtered, preferred_types=effective_types)

    if effective_open_now:
        filtered = apply_open_now_filter(filtered, require_open_now=True)

    if effective_min_rating is not None:
        filtered = apply_rating_filter(filtered, min_rating=effective_min_rating)

    if effective_budget:
        filtered = apply_budget_filter(filtered, budget_level=effective_budget)

    if effective_companion:
        filtered = apply_companion_filter(filtered, companion_type=effective_companion)

    if effective_time_slot:
        filtered = apply_time_slot_filter(filtered, time_slot=effective_time_slot)

    return filtered


def apply_budget_filter(places: list[dict[str, Any]], *, budget_level: str) -> list[dict[str, Any]]:
    """Filter by normalized budget level.

    Input:
    - places: candidate place dicts containing price_level and/or price_range.
    - budget_level: low, medium, high, or aliases normalized by this function.

    Output:
    - places matching the requested budget.
    - places without price metadata are kept.
    """
    normalized_budget = normalize_budget_level(budget_level)
    if normalized_budget is None:
        return places

    price_level_ranges = {
        "low": range(0, 2),
        "medium": range(0, 3),
        "high": range(2, 5),
    }
    price_text_aliases = {
        "low": {"low", "cheap", "budget", "rẻ", "re", "bình dân", "binh dan"},
        "medium": {"medium", "moderate", "average", "tầm trung", "tam trung"},
        "high": {"high", "premium", "expensive", "luxury", "cao cấp", "cao cap"},
    }

    filtered: list[dict[str, Any]] = []
    for place in places:
        raw_price_level = place.get("price_level")
        raw_price_range = str(place.get("price_range") or "").strip().lower()

        price_level = _as_float(raw_price_level)
        if price_level is None and not raw_price_range:
            filtered.append(place)
            continue

        matches_numeric = price_level is not None and int(price_level) in price_level_ranges[normalized_budget]
        matches_text = raw_price_range in price_text_aliases[normalized_budget]

        if matches_numeric or matches_text:
            filtered.append(place)

    return filtered


def apply_companion_filter(places: list[dict[str, Any]], *, companion_type: str) -> list[dict[str, Any]]:
    """Filter or keep places based on companion metadata when available."""
    if not companion_type:
        return places

    target = str(companion_type).lower()
    aliases = {
        "solo": {"solo", "quiet", "alone", "workspace"},
        "couple": {"couple", "romantic", "dating"},
        "family": {"family", "kids", "children"},
        "friends": {"friends", "group", "party", "team"},
        "kids": {"family", "kids", "children"},
    }.get(target, {target})

    filtered: list[dict[str, Any]] = []
    for place in places:
        place_tags = _as_list(place.get("types")) + _as_list(place.get("tags")) + _as_list(place.get("companion_types"))
        if not place_tags:
            filtered.append(place)
            continue

        normalized_tags = {tag.lower() for tag in place_tags}
        if normalized_tags.intersection(aliases):
            filtered.append(place)

    return filtered


def apply_rating_filter(places: list[dict[str, Any]], *, min_rating: float) -> list[dict[str, Any]]:
    """Keep places with rating >= min_rating, preserving unknown ratings."""
    filtered: list[dict[str, Any]] = []
    for place in places:
        rating = _as_float(place.get("rating"))
        if rating is None or rating >= min_rating:
            filtered.append(place)
    return filtered


def apply_open_now_filter(places: list[dict[str, Any]], *, require_open_now: bool) -> list[dict[str, Any]]:
    """Keep currently-open places when requested."""
    if not require_open_now:
        return places
    return [place for place in places if place.get("open_now") is True]


def apply_preferred_types_filter(places: list[dict[str, Any]], *, preferred_types: list[str]) -> list[dict[str, Any]]:
    """Filter by primary/category/types, preserving places with missing type metadata."""
    allowed = {item.lower() for item in _as_list(preferred_types)}
    if not allowed:
        return places

    filtered: list[dict[str, Any]] = []
    for place in places:
        place_types = {
            *[item.lower() for item in _as_list(place.get("primary_type"))],
            *[item.lower() for item in _as_list(place.get("category"))],
            *[item.lower() for item in _as_list(place.get("types"))],
        }

        if not place_types or place_types.intersection(allowed):
            filtered.append(place)

    return filtered


def apply_distance_filter(
    places: list[dict[str, Any]],
    *,
    max_distance_km: float,
    user_location: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Filter by distance_km or compute distance from user_location when available."""
    filtered: list[dict[str, Any]] = []
    for place in places:
        distance = _as_float(place.get("distance_km"))
        if distance is None and user_location:
            distance = get_distance_between_points(user_location, place)

        if distance is None or distance <= max_distance_km:
            filtered.append(place)

    return filtered


def apply_time_slot_filter(places: list[dict[str, Any]], *, time_slot: str) -> list[dict[str, Any]]:
    """Filter by suitable_time_slots when that metadata exists."""
    if not time_slot:
        return places

    target = str(time_slot).lower()
    filtered: list[dict[str, Any]] = []
    for place in places:
        slots = {slot.lower() for slot in _as_list(place.get("suitable_time_slots"))}
        if not slots or target in slots:
            filtered.append(place)

    return filtered
