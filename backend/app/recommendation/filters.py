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



def apply_filters(
    places: list[dict[str, Any]],
    max_distance_km: float | None = None,
    allowed_types: list[str] | None = None,
    require_open_now: bool = False,
    min_rating: float | None = None,
    budget_level: str | None = None,
) -> list[dict[str, Any]]:
    """Filter candidate places using simple rules.

    Owner:
    - TV4.

    Input:
    - places: candidate place dicts. Expected optional fields include
      distance_km, primary_type, open_now, rating, price_level, price_range.
    - max_distance_km: keep places inside this radius when distance_km exists.
    - allowed_types: accepted primary_type values.
    - require_open_now: keep only places with open_now is True.
    - min_rating: minimum rating from 0 to 5.
    - budget_level: low/medium/high budget filter.

    Output:
    - list of place dicts that match available filters.
    - If a place lacks optional metadata, the current rule should avoid crashing
      and only filter it out when the filter can be applied safely.

    Current implementation:
    - supports distance/type/open filters when fields are present

    TODO TV4:
    - add budget filtering
    - add schedule compatibility filtering based on intended start time
    - add event/festival availability filtering from internal database
    """
    filtered = places

    if max_distance_km is not None:
        filtered = [p for p in filtered if p.get("distance_km") is None or p.get("distance_km") <= max_distance_km]

    if allowed_types:
        allowed = set(allowed_types)
        filtered = [p for p in filtered if p.get("primary_type") in allowed]

    if require_open_now:
        filtered = [p for p in filtered if p.get("open_now") is True]

    if min_rating is not None:
        filtered = [p for p in filtered if p.get("rating") is None or p.get("rating") >= min_rating]

    if budget_level:
        budget_filtered = apply_budget_filter(filtered, budget_level=budget_level)
        if budget_filtered is not None:
            filtered = budget_filtered

    return filtered


def build_filter_plan(nlp_fields: dict[str, Any], ui_filters: dict[str, Any]) -> dict[str, Any]:
    """TODO TV4: merge NLP fields and UI filters into one filter plan.

    Owner:
    - TV4.
    - Coordinate field names with TV2 and TV3 before changing keys.

    Input:
    - nlp_fields: output from TV3 parse_recommendation_language_contract:
      entertainment_type, budget_level, companion_type, time_slot,
      distance_hint_km, require_open_now, min_rating, preferred_types.
    - ui_filters: explicit frontend filter values from TV2 FilterPanel:
      entertainment_type, budget_level, companion_type, start_time,
      max_distance_km, require_open_now, min_rating, latitude, longitude.

    Output:
    - dict accepted by apply_filters and recommender:
      - max_distance_km
      - allowed_types
      - require_open_now
      - min_rating
      - budget_level
      - start_time
      - companion_type
      - source_map: optional dict showing source per field, for example
        {"budget_level": "ui", "max_distance_km": "nlp"}.

    Rule:
    - explicit UI filters override NLP-derived filters.
    """
    pass


def apply_budget_filter(places: list[dict[str, Any]], *, budget_level: str) -> list[dict[str, Any]]:
    """TODO TV4: filter by budget.

    Owner:
    - TV4.

    Input:
    - places: candidate place dicts containing price_level and/or price_range
    - budget_level: low, medium, high. Accept aliases only after normalizing them
      in build_filter_plan.

    Output:
    - filtered places matching user budget.
    - unchanged places if price metadata is not available enough to filter.

    Suggested mapping:
    - low: price_level 0..1
    - medium: price_level 2
    - high: price_level 3..4
    """
    pass


def apply_companion_filter(places: list[dict[str, Any]], *, companion_type: str) -> list[dict[str, Any]]:
    """TODO TV4: filter or boost places by companion type.

    Owner:
    - TV4.
    - Use TV3 output values for companion_type.

    Input:
    - places: candidate place dicts
    - companion_type: solo, couple, family, friends, kids

    Output:
    - filtered places or unchanged list when there is not enough metadata.
    - If implemented as soft preference instead of hard filter, add
      filter_reasons or companion_match fields for TV5 ranking.
    """
    pass
