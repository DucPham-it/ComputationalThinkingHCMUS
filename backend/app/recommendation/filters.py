"""Filtering stage for recommendation pipeline.

Input:
- candidate places from external APIs and/or local database
- user constraints such as budget, distance, open status, category

Output:
- narrowed candidate list before ranking
"""

from typing import Any



def apply_filters(
    places: list[dict[str, Any]],
    max_distance_km: float | None = None,
    allowed_types: list[str] | None = None,
    require_open_now: bool = False,
) -> list[dict[str, Any]]:
    """Filter candidate places using simple rules.

    Current implementation:
    - supports distance/type/open filters when fields are present

    TODO:
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

    return filtered
