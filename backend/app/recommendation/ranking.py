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
import math
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


def _haversine_distance_km(
    latitude_a: float | None,
    longitude_a: float | None,
    latitude_b: float | None,
    longitude_b: float | None,
) -> float:
    if latitude_a is None or longitude_a is None or latitude_b is None or longitude_b is None:
        return float("inf")

    radius = 6371.0
    lat1 = math.radians(latitude_a)
    lon1 = math.radians(longitude_a)
    lat2 = math.radians(latitude_b)
    lon2 = math.radians(longitude_b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def compute_score(
    place: dict[str, Any],
    *,
    query: str = "",
    user_address: str | None = None,
    recent_queries: list[str] | None = None,
    saved_ids: list[int] | None = None,
    picked_ids: list[int] | None = None,
    picked_places: list[dict[str, Any]] | None = None,
    preferred_types: list[str] | None = None,
) -> tuple[float, dict[str, float]]:
    """Compute recommendation score and detailed score parts for a single place.

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
    - picked_places: places previously picked by the current user.
    - preferred_types: preferred place types from history or filter context.

    Output:
    - tuple(score, score_parts).
    - score_parts is used by explain_score and the frontend explanation UI.
    """
    rating = float(place.get("rating") or 0)
    distance_km = float(place.get("distance_km") or 0)
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

    base_rating = rating * 1.5
    distance_bonus = max(0.0, 6.0 - distance_km) * 0.4
    review_bonus = min(review_count / 20.0, 1.6)
    query_terms = _tokenize(query)
    address_terms = _tokenize(user_address)

    query_bonus = _match_bonus(text_blob, query_terms, 0.75, 3.0) if query_terms else 0.0
    address_bonus = _match_bonus(text_blob, address_terms, 0.6, 2.0) if not query_terms else 0.0
    search_history_bonus = score_from_search_history(place, recent_queries or [])
    pick_history_bonus = score_from_user_pick_history(place, picked_places or [])
    saved_bonus = 2.6 if place_id in set(saved_ids or []) else 0.0
    picked_bonus = 2.2 if place_id in set(picked_ids or []) else 0.0
    preferred_type_bonus = (
        1.5
        if primary_type and primary_type in {item.lower() for item in (preferred_types or [])}
        else 0.0
    )
    open_bonus = 0.4 if place.get("open_now") is True else 0.0

    has_history = bool(recent_queries) or bool(picked_ids) or bool(saved_ids) or bool(picked_places)
    random_bonus = 0.0
    if not query_terms and not has_history:
        random_bonus = score_random_baseline(place, seed_text=user_address or "default")

    score = (
        base_rating
        + distance_bonus
        + review_bonus
        + query_bonus
        + address_bonus
        + search_history_bonus
        + pick_history_bonus
        + saved_bonus
        + picked_bonus
        + preferred_type_bonus
        + open_bonus
        + random_bonus
    )
    score_parts = {
        "base_rating": round(base_rating, 2),
        "distance": round(distance_bonus, 2),
        "review": round(review_bonus, 2),
        "query": round(query_bonus, 2),
        "address_match": round(address_bonus, 2),
        "search_history": round(search_history_bonus, 2),
        "pick_history": round(pick_history_bonus, 2),
        "favorite": round(saved_bonus, 2),
        "picked": round(picked_bonus, 2),
        "preferred_type": round(preferred_type_bonus, 2),
        "open_now": round(open_bonus, 2),
        "random_baseline": round(random_bonus, 2),
    }
    return round(score, 2), score_parts



def rank_places(
    places: list[dict[str, Any]],
    *,
    query: str = "",
    user_address: str | None = None,
    recent_queries: list[str] | None = None,
    saved_ids: list[int] | None = None,
    picked_ids: list[int] | None = None,
    picked_places: list[dict[str, Any]] | None = None,
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
    - each item includes score, score_parts, and explanation.
    """
    ranked = []
    for item in places:
        enriched = dict(item)
        score, score_parts = compute_score(
            enriched,
            query=query,
            user_address=user_address,
            recent_queries=recent_queries,
            saved_ids=saved_ids,
            picked_ids=picked_ids,
            picked_places=picked_places,
            preferred_types=preferred_types,
        )
        enriched["score"] = score
        enriched["score_parts"] = score_parts
        enriched["explanation"] = explain_score({"score": score, **score_parts})
        ranked.append(enriched)
    return sorted(ranked, key=lambda item: item.get("score", 0), reverse=True)


def score_random_baseline(place: dict[str, Any], *, seed_text: str = "") -> float:
    """Calculate default suggestion score when user has no useful history.

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
    if place.get("id") is None:
        return 0.25

    seed = f"{place.get('id')}|{seed_text}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()
    value = int(digest[:8], 16) / 0xFFFFFFFF
    return round(0.45 + value * 0.45, 3)


def score_from_user_pick_history(place: dict[str, Any], picked_places: list[dict[str, Any]]) -> float:
    """Score a place using map/route pick history.

    Owner:
    - TV5.

    Input:
    - place: candidate place dict
    - picked_places: most recent user picks from PickRepository

    Output:
    - float score contribution based on matching category, distance cluster, price, and rating.
    """
    if not picked_places:
        return 0.0

    primary_type = str(place.get("primary_type") or "").lower()
    place_blob = " ".join(
        [
            str(place.get("name") or "").lower(),
            str(place.get("address") or "").lower(),
            primary_type,
        ]
    )
    total_bonus = 0.0
    for index, picked in enumerate(picked_places[:8]):
        weight = 1.0 if index == 0 else 0.6 if index < 3 else 0.35
        picked_type = str(picked.get("primary_type") or "").lower()
        if picked_type and picked_type == primary_type:
            total_bonus += 1.2 * weight

        picked_address = str(picked.get("address") or "").lower()
        if picked_address:
            total_bonus += _match_bonus(place_blob, _tokenize(picked_address), 0.25 * weight, 0.8 * weight)

        distance_km = _haversine_distance_km(
            place.get("latitude"),
            place.get("longitude"),
            picked.get("latitude"),
            picked.get("longitude"),
        )
        if distance_km <= 2.0:
            total_bonus += 1.0 * weight
        elif distance_km <= 5.0:
            total_bonus += 0.45 * weight

    return min(total_bonus, 3.5)


def score_from_search_history(place: dict[str, Any], recent_queries: list[str]) -> float:
    """Score a place using at most 80 stored search-history items.

    Owner:
    - TV5.

    Input:
    - place: candidate place dict
    - recent_queries: deduplicated text queries, newest first

    Output:
    - float score contribution based on keyword/category overlap.
    """
    if not recent_queries:
        return 0.0

    text_blob = " ".join(
        [
            str(place.get("name") or "").lower(),
            str(place.get("address") or "").lower(),
            str(place.get("primary_type") or "").lower(),
        ]
    )
    total_bonus = 0.0
    for recent_query in recent_queries[:12]:
        total_bonus += _match_bonus(text_blob, _tokenize(recent_query), 0.45, 1.1)

    return min(total_bonus, 2.2)


def explain_score(place: dict[str, Any]) -> dict[str, Any]:
    """Provide user-facing ranking explanation.

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
    score_parts = {
        key: float(value)
        for key, value in place.items()
        if key
        in {
            "query",
            "search_history",
            "pick_history",
            "favorite",
            "picked",
            "preferred_type",
            "open_now",
            "random_baseline",
            "address_match",
            "distance",
            "review",
        }
        and value
    }
    factors = sorted(
        (
            {"name": name, "value": value, "weight": value}
            for name, value in score_parts.items()
            if value > 0
        ),
        key=lambda factor: factor["weight"],
        reverse=True,
    )

    summary = "Gợi ý phù hợp dựa trên điểm đánh giá và lịch sử của bạn."
    if any(factor["name"] == "pick_history" for factor in factors):
        summary = "Phù hợp với địa điểm bạn đã chọn trước đó."
    elif any(factor["name"] == "search_history" for factor in factors):
        summary = "Khớp với lịch sử tìm kiếm gần đây của bạn."
    elif any(factor["name"] == "favorite" for factor in factors):
        summary = "Ưu tiên theo nơi bạn đã yêu thích."
    elif any(factor["name"] == "random_baseline" for factor in factors):
        summary = "Gợi ý hôm nay dựa trên lựa chọn ngẫu nhiên ổn định."
    elif any(factor["name"] == "query" for factor in factors):
        summary = "Khớp với nhu cầu tìm kiếm của bạn."

    return {
        "summary": summary,
        "factors": factors,
    }
