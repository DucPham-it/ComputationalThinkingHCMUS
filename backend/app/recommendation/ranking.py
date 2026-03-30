"""Ranking stage for recommendation pipeline.

Input:
- filtered place candidates
- user preferences and contextual signals

Output:
- sorted candidates with computed score
"""

from typing import Any



def compute_score(place: dict[str, Any]) -> float:
    """Compute recommendation score for a single place.

    Current placeholder formula:
    - higher rating increases score
    - shorter distance increases score
    - currently no user-history or weather bonus yet

    TODO:
    - add favorites similarity score
    - add weather bonus
    - add time-of-day habit bonus
    - add price compatibility score
    - add local review confidence score
    """
    rating = float(place.get("rating") or 0)
    distance_km = float(place.get("distance_km") or 0)
    distance_bonus = max(0.0, 5.0 - distance_km)
    return rating * 2 + distance_bonus



def rank_places(places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach score and sort descending.

    Output:
    - list sorted by recommendation score descending
    """
    ranked = []
    for item in places:
        enriched = dict(item)
        enriched["score"] = compute_score(enriched)
        ranked.append(enriched)
    return sorted(ranked, key=lambda item: item.get("score", 0), reverse=True)
