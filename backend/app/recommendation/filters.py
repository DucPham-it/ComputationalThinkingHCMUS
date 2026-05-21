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
      budget_level, companion_type, time_slot, entertainment_type, source_map.

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
        "entertainment_type": ("entertainment_type",),
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

    Combines Vietnamese filter reasons, synonym mapping, and a looping
    fallback filter relaxation mechanism to guarantee at least 10 candidates.
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
    effective_ent_type = plan.get("entertainment_type")

    # Define fallback relaxation stages
    fallback_stages = [
        [],  # Round 1: Strict - apply all
        ["preferred_types", "time_slot"],  # Round 2: Relax types and time slot
        ["preferred_types", "time_slot", "budget_level", "companion_type", "min_rating"]  # Round 3: Only hard filters
    ]

    final_results = []

    for drop_keys in fallback_stages:
        current_candidates = [dict(place) for place in places]
        for p in current_candidates:
            p["filter_reasons"] = []

        # Flexible filters
        if effective_budget and "budget_level" not in drop_keys:
            current_candidates = apply_budget_filter(current_candidates, budget_level=effective_budget)

        if effective_companion and "companion_type" not in drop_keys:
            current_candidates = apply_companion_filter(current_candidates, companion_type=effective_companion)

        if effective_min_rating is not None and "min_rating" not in drop_keys:
            current_candidates = apply_rating_filter(current_candidates, min_rating=effective_min_rating)

        if effective_time_slot and "time_slot" not in drop_keys:
            current_candidates = apply_time_slot_filter(current_candidates, time_slot=effective_time_slot)

        if effective_types and "preferred_types" not in drop_keys:
            current_candidates = apply_preferred_types_filter(current_candidates, preferred_types=effective_types)

        # Hard filters
        if effective_ent_type:
            current_candidates = apply_type_filter(current_candidates, expected_type=effective_ent_type)

        if effective_distance is not None:
            current_candidates = apply_distance_filter(
                current_candidates,
                max_distance_km=effective_distance,
                user_location=user_location,
            )

        if effective_open_now:
            current_candidates = apply_open_now_filter(current_candidates, require_open_now=True)

        if len(current_candidates) >= 10:
            final_results = current_candidates
            break

        if len(current_candidates) > len(final_results):
            final_results = current_candidates

    return final_results


def apply_budget_filter(places: list[dict[str, Any]], *, budget_level: str) -> list[dict[str, Any]]:
    """Filter by normalized budget level, appending reasons."""
    normalized_budget = normalize_budget_level(budget_level)
    if normalized_budget is None:
        return places

    price_level_ranges = {
        "low": range(0, 2),
        "medium": range(0, 3),
        "high": range(2, 5),
    }
    
    price_text_aliases = {
        "low": {"low", "cheap", "budget", "rẻ", "re"},
        "medium": {"low", "cheap", "budget", "rẻ", "re", "medium", "moderate", "average", "tầm trung", "tam trung", "bình dân", "binh dan"},
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

        matches_numeric = False
        is_cheaper = False
        
        if price_level is not None:
            val = int(price_level)
            if val in price_level_ranges[normalized_budget]:
                matches_numeric = True
                if normalized_budget == "medium" and val in price_level_ranges["low"]:
                    is_cheaper = True
                elif normalized_budget == "high" and val in price_level_ranges["medium"] and val not in price_level_ranges["high"]:
                    is_cheaper = True

        matches_text = False
        if raw_price_range:
            cleaned_range = raw_price_range.lower()
            if cleaned_range in price_text_aliases[normalized_budget]:
                matches_text = True
                if normalized_budget == "medium" and cleaned_range in price_text_aliases["low"]:
                    is_cheaper = True
                elif normalized_budget == "high" and (cleaned_range in price_text_aliases["low"] or cleaned_range in price_text_aliases["medium"]):
                    is_cheaper = True

        matches_str_level = False
        if isinstance(raw_price_level, str) and not raw_price_level.replace('.', '', 1).isdigit():
            cleaned_level = raw_price_level.strip().lower()
            if cleaned_level in price_text_aliases[normalized_budget]:
                matches_str_level = True
                if normalized_budget == "medium" and cleaned_level in price_text_aliases["low"]:
                    is_cheaper = True
                elif normalized_budget == "high" and (cleaned_level in price_text_aliases["low"] or cleaned_level in price_text_aliases["medium"]):
                    is_cheaper = True

        if matches_numeric or matches_text or matches_str_level:
            if "filter_reasons" not in place:
                place["filter_reasons"] = []
            
            if is_cheaper:
                reason = "Lựa chọn tiết kiệm hơn so với ngân sách dự kiến"
            else:
                reason = f"Phù hợp với tiêu chí giá {budget_level}"
            place["filter_reasons"].append(reason)
            filtered.append(place)

    return filtered


def apply_companion_filter(places: list[dict[str, Any]], *, companion_type: str) -> list[dict[str, Any]]:
    """Filter by companion type, utilizing Vietnamese/English synonyms and appending reasons."""
    if not companion_type:
        return places

    target = str(companion_type).lower()
    
    synonym_mapping = {
        "người yêu": {"couple", "romantic", "dating"},
        "bạn gái": {"couple", "romantic", "dating"},
        "bạn trai": {"couple", "romantic", "dating"},
        "cặp đôi": {"couple", "romantic", "dating"},
        "trẻ em": {"family", "kids", "children"},
        "trẻ nhỏ": {"family", "kids", "children"},
        "con nít": {"family", "kids", "children"},
        "gia đình": {"family", "kids", "children"},
        "nhóm bạn": {"friends", "group", "party", "team"},
        "bạn bè": {"friends", "group", "party", "team"},
        "một mình": {"solo", "quiet", "alone", "workspace"},
        "solo": {"solo", "quiet", "alone", "workspace"},
        "couple": {"couple", "romantic", "dating"},
        "family": {"family", "kids", "children"},
        "friends": {"friends", "group", "party", "team"},
        "kids": {"family", "kids", "children"},
    }
    
    aliases = synonym_mapping.get(target, {target})

    filtered: list[dict[str, Any]] = []
    for place in places:
        place_tags = _as_list(place.get("types")) + _as_list(place.get("tags")) + _as_list(place.get("companion_types"))
        
        if not place_tags:
            filtered.append(place)
            continue

        normalized_tags = {tag.lower() for tag in place_tags}
        if normalized_tags.intersection(aliases):
            if "filter_reasons" not in place:
                place["filter_reasons"] = []
            place["filter_reasons"].append(f"Không gian tuyệt vời để đi cùng {companion_type}")
            filtered.append(place)

    return filtered


def apply_rating_filter(places: list[dict[str, Any]], *, min_rating: float, min_reviews: int = 5) -> list[dict[str, Any]]:
    """Keep places with rating >= min_rating, checking review_count when available."""
    if min_rating is None:
        return places
        
    filtered: list[dict[str, Any]] = []
    for place in places:
        rating = _as_float(place.get("rating"))
        review_count = place.get("review_count")
        
        if rating is None:
            filtered.append(place)
            continue
            
        try:
            is_rating_passed = float(rating) >= float(min_rating)
            is_trustworthy = True
            if review_count is not None:
                is_trustworthy = int(review_count) >= min_reviews
                
            if is_rating_passed and is_trustworthy:
                if "filter_reasons" not in place:
                    place["filter_reasons"] = []
                place["filter_reasons"].append(f"Chất lượng được cộng đồng bảo chứng ({rating} sao)")
                filtered.append(place)
        except (ValueError, TypeError):
            filtered.append(place)
            
    return filtered


def apply_open_now_filter(places: list[dict[str, Any]], *, require_open_now: bool) -> list[dict[str, Any]]:
    """Keep currently-open places when requested."""
    if not require_open_now:
        return places
        
    filtered: list[dict[str, Any]] = []
    for place in places:
        is_open = place.get("open_now")
        if is_open is None or is_open is True:
            if is_open is True:
                if "filter_reasons" not in place:
                    place["filter_reasons"] = []
                place["filter_reasons"].append("Địa điểm đang mở cửa phục vụ")
            filtered.append(place)
            
    return filtered


def apply_type_filter(places: list[dict[str, Any]], *, expected_type: str) -> list[dict[str, Any]]:
    """Filter by primary/category/types, utilizing synonyms for common Vietnamese type descriptions."""
    if not expected_type:
        return places
        
    synonym_mapping = {
        "quán nước": ["cafe", "tea", "boba", "coffee"],
        "trà sữa": ["boba", "cafe", "tea"],
        "chỗ nhậu": ["bar", "pub", "beer", "nightclub"],
        "quán ăn": ["restaurant", "food", "eatery", "diner"],
        "sống ảo": ["cafe", "studio", "gallery", "park"]
    }
    
    desired_type = expected_type.lower()
    target_types = synonym_mapping.get(desired_type, [desired_type])
        
    filtered_places = []
    for place in places:
        primary = place.get("primary_type", "")
        place_types = place.get("types", [])
        category = place.get("category", "")
        
        if not primary and not place_types and not category:
            filtered_places.append(place)
            continue
            
        all_types = []
        if primary:
            all_types.append(primary.lower())
        if category:
            all_types.extend([c.lower() for c in _as_list(category)])
        all_types.extend([t.lower() for t in place_types])
        
        if any(t in all_types for t in target_types):
            if "filter_reasons" not in place:
                place["filter_reasons"] = []
            place["filter_reasons"].append(f"Đúng loại hình '{expected_type}' bạn mong muốn")
            filtered_places.append(place)
            
    return filtered_places


def apply_distance_filter(
    places: list[dict[str, Any]],
    *,
    max_distance_km: float,
    user_location: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Filter by distance_km or compute distance from user_location when available, appending reasons."""
    if not max_distance_km:
        return places

    filtered: list[dict[str, Any]] = []
    for place in places:
        distance = _as_float(place.get("distance_km"))
        if distance is None and user_location:
            distance = get_distance_between_points(user_location, place)

        if distance is None:
            filtered.append(place)
            continue

        try:
            if float(distance) <= float(max_distance_km):
                if "filter_reasons" not in place:
                    place["filter_reasons"] = []
                place["filter_reasons"].append(f"Khoảng cách thuận lợi (cách {round(float(distance), 1)} km)")
                filtered.append(place)
        except (ValueError, TypeError):
            filtered.append(place)

    return filtered


def apply_time_slot_filter(places: list[dict[str, Any]], *, time_slot: str) -> list[dict[str, Any]]:
    """Filter by suitable_time_slots when that metadata exists, appending reasons."""
    if not time_slot:
        return places

    target = str(time_slot).lower()
    filtered: list[dict[str, Any]] = []
    for place in places:
        slots = {slot.lower() for slot in _as_list(place.get("suitable_time_slots"))}
        if not slots or target in slots:
            if "filter_reasons" not in place:
                place["filter_reasons"] = []
            place["filter_reasons"].append(f"Không gian và dịch vụ lý tưởng cho buổi {time_slot}")
            filtered.append(place)

    return filtered


def apply_preferred_types_filter(places: list[dict[str, Any]], *, preferred_types: list[str]) -> list[dict[str, Any]]:
    """Filter by primary/category/types, preserving places with missing type metadata, and appending reasons."""
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

        if not place_types:
            filtered.append(place)
            continue

        matched_prefs = place_types.intersection(allowed)
        if matched_prefs:
            if "filter_reasons" not in place:
                place["filter_reasons"] = []
            matched_str = ", ".join(sorted(list(matched_prefs)))
            place["filter_reasons"].append(f"Thỏa mãn sở thích cá nhân của bạn ({matched_str})")
            filtered.append(place)

    
