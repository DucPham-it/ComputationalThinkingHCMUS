"""Ranking stage for recommendation pipeline.

Owner:
- TV5: Ranking + Personalization.

File input:
- Filtered place candidates from TV4.
- User preferences and contextual signals from picks, favorites, and search
  history.

File output:
- Sorted candidates with computed score.
- Later: score_parts and explanation for the frontend.
"""

from datetime import date
import hashlib
import re
from typing import Any


def _tokenize(text: str | None) -> list[str]:
    if not text:
        return []

    tokens = [
        token
        for token in re.split(r"[^\w]+", text.lower(), flags=re.UNICODE)
        if len(token) >= 3
    ]
    stop_words = {
        "quan",
        "quận",
        "tinh",
        "tỉnh",
        "thanh",
        "thành",
        "phuong",
        "phường",
        "street",
        "road",
        "district",
        "city",
        "near",
        "gần",
        "toi",
        "tôi",
    }
    return [token for token in tokens if token not in stop_words]


def _match_bonus(text: str, terms: list[str], weight: float, cap: float) -> float:
    matches = sum(1 for term in terms if term and term in text)
    return min(cap, matches * weight)


def _daily_variation(place_id: int | None) -> float:
    if place_id is None:
        return 0.0

    seed = f"{place_id}-{date.today().isoformat()}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()
    return (int(digest[:4], 16) / 65535) * 0.8


def compute_score(
    place: dict[str, Any],
    *,
    query: str = "",
    user_address: str | None = None,
    recent_queries: list[str] | None = None,
    saved_ids: list[int] | None = None,
    picked_ids: list[int] | None = None,
    preferred_types: list[str] | None = None,
) -> float:
    """Compute recommendation score for a single place.

    Owner:
    - TV5 maintains ranking formula.

    Input:
    - place: candidate place dict with rating, distance_km, review_count,
      primary_type, id, name, address, open_now when available.
    - query: raw recommendation query.
    - user_address: profile address text for fallback matching.
    - recent_queries: newest search-history queries, at most 80 in final flow.
    - saved_ids: favorite place ids.
    - picked_ids: place ids picked from map/route.
    - preferred_types: preferred place types from history or filter context.

    Output:
    - numeric score rounded to 2 decimals. Larger means better recommendation.

    Current placeholder formula:
    - higher rating increases score
    - shorter distance increases score
    - currently no user-history or weather bonus yet

    TODO TV5:
    - add favorites similarity score
    - add weather bonus
    - add time-of-day habit bonus
    - add price compatibility score
    - add local review confidence score
    """
    rating = float(place.get("rating") or 0)
    distance_km = float(place.get("distance_km") or 0)
    distance_bonus = max(0.0, 5.0 - distance_km)
    review_count = float(place.get("review_count") or 0)
    primary_type = str(place.get("primary_type") or "").lower()
    place_id = place.get("id")
    text_blob = " ".join(
        [
            str(place.get("name") or "").lower(),
            str(place.get("address") or "").lower(),
            primary_type,
        ]
    )

    score = rating * 2 + distance_bonus
    score += min(review_count / 25.0, 1.5)

    query_terms = _tokenize(query)
    address_terms = _tokenize(user_address)
    history_terms = _tokenize(" ".join(recent_queries or []))

    if query_terms:
        score += _match_bonus(text_blob, query_terms, 0.8, 3.0)
    else:
        score += _match_bonus(text_blob, address_terms, 0.6, 2.4)
        score += _daily_variation(place_id)

    score += _match_bonus(text_blob, history_terms, 0.35, 1.8)

    if place_id in set(saved_ids or []):
        score += 2.6

    if place_id in set(picked_ids or []):
        score += 2.2

    if primary_type and primary_type in {item.lower() for item in (preferred_types or [])}:
        score += 1.5

    if place.get("open_now") is True:
        score += 0.4

    return round(score, 2)



def rank_places(
    places: list[dict[str, Any]],
    *,
    query: str = "",
    user_address: str | None = None,
    recent_queries: list[str] | None = None,
    saved_ids: list[int] | None = None,
    picked_ids: list[int] | None = None,
    preferred_types: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Attach score and sort descending.

    Owner:
    - TV5.

    Input:
    - places: filtered place dicts from TV4.
    - query/user_address/recent_queries/saved_ids/picked_ids/preferred_types:
      context forwarded from recommender.

    Output:
    - list sorted by recommendation score descending.
    - each item includes score.
    """
    ranked = []
    for item in places:
        enriched = dict(item)
        enriched["score"] = compute_score(
            enriched,
            query=query,
            user_address=user_address,
            recent_queries=recent_queries,
            saved_ids=saved_ids,
            picked_ids=picked_ids,
            preferred_types=preferred_types,
        )
        ranked.append(enriched)
    return sorted(ranked, key=lambda item: item.get("score", 0), reverse=True)


def score_random_baseline(place: dict[str, Any], *, seed_text: str = "") -> float:
    """TODO TV5: default random suggestion score when user has no useful history.

    Owner:
    - TV5.

    Input:
    - place: candidate place dict
    - seed_text: stable daily/user seed so suggestions feel fresh but reproducible

    Output:
    - float score contribution used before history-based ranking exists.

    Requirement:
    - Use this when query is empty and user has no picked places/search history.
    """
    pass


def score_from_user_pick_history(place: dict[str, Any], picked_places: list[dict[str, Any]]) -> float:
    """TODO TV5: score a place using map/route pick history.

    Owner:
    - TV5.

    Input:
    - place: candidate place dict
    - picked_places: most recent user picks from PickRepository

    Output:
    - float score contribution based on matching category, distance cluster, price, and rating.
    """
    pass


def score_from_search_history(place: dict[str, Any], recent_queries: list[str]) -> float:
    """TODO TV5: score a place using at most 80 stored search-history items.

    Owner:
    - TV5.

    Input:
    - place: candidate place dict
    - recent_queries: deduplicated text queries, newest first

    Output:
    - float score contribution based on keyword/category overlap.
    """
    pass


def explain_score(place: dict[str, Any]) -> dict[str, Any]:
    """TODO TV5: provide user-facing ranking explanation.

    Owner:
    - TV5 creates explanation data.
    - TV2 only renders the explanation if present.

    Input:
    - place: ranked place dict with score and score factor fields

    Output:
    - dict:
      - summary: short Vietnamese explanation
      - factors: list of {name, value, weight}
    """
    pass
