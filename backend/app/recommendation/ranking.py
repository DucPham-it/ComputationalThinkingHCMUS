"""Ranking stage for recommendation pipeline.

Owner:
- TV5: Ranking + Personalization.

File input:
- Filtered place candidates from TV4.
- User preferences and contextual signals from picks, favorites, and search
  history.

File output:
- Sorted candidates with computed score.
- score_parts and explanation for the frontend.

Change from original (dynamic weight learning):
- Hardcoded bonus constants (saved_bonus=2.6, picked_bonus=2.2, etc.) are
  replaced by _compute_dynamic_weights(), which learns weight multipliers
  from the actual distribution of the user's interaction history.
- When a user has rich history, weights are tuned toward their dominant
  behaviour pattern (e.g. heavy pick-history user → higher pick weight).
- When history is sparse, weights fall back to the original defaults so
  cold-start users are not penalised.
- All score_parts keys and the explain_score contract are unchanged so the
  frontend needs no modification.
"""

from datetime import date
import hashlib
import math
import re
from collections import Counter
from typing import Any


# ============================================================
# DEFAULT WEIGHTS  (original hardcoded values kept as fallback)
# ============================================================

_DEFAULT_WEIGHTS: dict[str, float] = {
    "saved_bonus": 2.6,
    "picked_bonus": 2.2,
    "preferred_type_bonus": 1.5,
    "open_bonus": 0.4,
    "query_weight": 0.75,
    "query_cap": 3.0,
    "address_weight": 0.6,
    "address_cap": 2.0,
    "search_history_weight": 0.45,
    "search_history_cap": 2.2,
    "pick_history_type_weight": 1.2,
    "pick_history_addr_weight": 0.25,
    "pick_history_near2km": 1.0,
    "pick_history_near5km": 0.45,
    "pick_history_cap": 3.5,
    "distance_coeff": 0.4,
    "rating_coeff": 1.5,
    "review_cap": 1.6,
}

# Maximum multiplier allowed when adapting weights from history
_MAX_WEIGHT_MULTIPLIER = 2.0
_MIN_WEIGHT_MULTIPLIER = 0.5


# ============================================================
# DYNAMIC WEIGHT LEARNING
# ============================================================

def _compute_dynamic_weights(
    recent_queries: list[str],
    saved_ids: list[int],
    picked_ids: list[int],
    picked_places: list[dict[str, Any]],
) -> dict[str, float]:
    """Learn per-user weight multipliers from interaction history.

    Input:
    - recent_queries: list of recent search strings (up to 80).
    - saved_ids: list of place ids the user has saved as favourites.
    - picked_ids: list of place ids the user has picked on the map.
    - picked_places: full place dicts for picked locations.

    Output:
    - dict of weight names → float values ready to use in compute_score.
      Falls back to _DEFAULT_WEIGHTS when history is too sparse.

    Algorithm:
    1. Count signals: n_saved, n_picked, n_queries.
    2. Compute a raw signal_ratio = each signal / total_signals.
    3. Scale the corresponding bonus by a multiplier in
       [_MIN_WEIGHT_MULTIPLIER, _MAX_WEIGHT_MULTIPLIER] proportional to
       how dominant that signal is relative to the average.
    4. If total interaction count < MIN_HISTORY_THRESHOLD, return defaults
       unchanged (cold-start protection).
    """
    weights = dict(_DEFAULT_WEIGHTS)

    n_saved = len(saved_ids)
    n_picked = len(picked_ids)
    n_queries = len(recent_queries)
    total = n_saved + n_picked + n_queries

    MIN_HISTORY_THRESHOLD = 3
    if total < MIN_HISTORY_THRESHOLD:
        return weights  # cold-start: use defaults

    avg = total / 3.0  # expected equal share per signal type

    def _scale(default: float, count: int) -> float:
        """Scale a default weight up/down based on signal dominance."""
        ratio = count / avg if avg > 0 else 1.0
        multiplier = max(_MIN_WEIGHT_MULTIPLIER, min(_MAX_WEIGHT_MULTIPLIER, ratio))
        return round(default * multiplier, 4)

    weights["saved_bonus"] = _scale(_DEFAULT_WEIGHTS["saved_bonus"], n_saved)
    weights["picked_bonus"] = _scale(_DEFAULT_WEIGHTS["picked_bonus"], n_picked)

    # If the user picks many places they always seem to pick the same category,
    # boost preferred_type_bonus proportionally.
    if picked_places:
        type_counter = Counter(
            str(p.get("primary_type") or "").lower()
            for p in picked_places
            if p.get("primary_type")
        )
        dominant_count = type_counter.most_common(1)[0][1] if type_counter else 0
        type_concentration = dominant_count / len(picked_places)  # 0..1
        # boost preferred_type_bonus when user consistently picks one category
        type_mult = 1.0 + type_concentration  # 1.0 → 2.0
        type_mult = min(_MAX_WEIGHT_MULTIPLIER, type_mult)
        weights["preferred_type_bonus"] = round(
            _DEFAULT_WEIGHTS["preferred_type_bonus"] * type_mult, 4
        )

    # If user searches a lot, trust text matching more.
    if n_queries > 0:
        query_mult = max(_MIN_WEIGHT_MULTIPLIER, min(_MAX_WEIGHT_MULTIPLIER, n_queries / avg))
        weights["query_weight"] = round(_DEFAULT_WEIGHTS["query_weight"] * query_mult, 4)
        weights["search_history_weight"] = round(
            _DEFAULT_WEIGHTS["search_history_weight"] * query_mult, 4
        )

    return weights


# ============================================================
# INTERNAL HELPERS  (unchanged from original)
# ============================================================

def _tokenize(text: str | None) -> list[str]:
    if not text:
        return []
    tokens = [
        token
        for token in re.split(r"[^\w]+", text.lower(), flags=re.UNICODE)
        if len(token) >= 3
    ]
    stop_words = {
        "quan", "quận", "tinh", "tỉnh", "thanh", "thành",
        "phuong", "phường", "street", "road", "district",
        "city", "near", "gần", "toi", "tôi",
    }
    return [token for token in tokens if token not in stop_words]


def _match_bonus(text: str, terms: list[str], weight: float, cap: float) -> float:
    matches = sum(1 for term in terms if term and term in text)
    return min(cap, matches * weight)


def _haversine_distance_km(
    latitude_a: float | None,
    longitude_a: float | None,
    latitude_b: float | None,
    longitude_b: float | None,
) -> float:
    if None in (latitude_a, longitude_a, latitude_b, longitude_b):
        return float("inf")
    radius = 6371.0
    lat1, lon1 = math.radians(latitude_a), math.radians(longitude_a)
    lat2, lon2 = math.radians(latitude_b), math.radians(longitude_b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _daily_variation(place_id: int | None) -> float:
    if place_id is None:
        return 0.0
    seed = f"{place_id}-{date.today().isoformat()}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()
    return (int(digest[:4], 16) / 65535) * 0.8


# ============================================================
# CORE SCORING
# ============================================================

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
    - place: candidate place dict.
    - query / user_address / recent_queries / saved_ids / picked_ids /
      picked_places / preferred_types: user context signals.

    Output:
    - tuple(score, score_parts).
      score: numeric score rounded to 2 decimals.
      score_parts: detailed contributions used for explanation (keys unchanged).

    Change from original:
    - All bonus constants are sourced from _compute_dynamic_weights() so they
      adapt to each user's interaction history instead of being fixed.
    """
    # --- dynamic weights for this user ---
    W = _compute_dynamic_weights(
        recent_queries=recent_queries or [],
        saved_ids=saved_ids or [],
        picked_ids=picked_ids or [],
        picked_places=picked_places or [],
    )

    rating = float(place.get("rating") or 0)
    distance_km = float(place.get("distance_km") or 0)
    review_count = float(place.get("review_count") or 0)
    primary_type = str(place.get("primary_type") or "").lower()
    place_id = place.get("id")
    text_blob = " ".join([
        str(place.get("name") or "").lower(),
        str(place.get("address") or "").lower(),
        primary_type,
    ])

    base_rating = rating * W["rating_coeff"]
    distance_bonus = max(0.0, 6.0 - distance_km) * W["distance_coeff"]
    review_bonus = min(review_count / 20.0, W["review_cap"])

    query_terms = _tokenize(query)
    address_terms = _tokenize(user_address)

    query_bonus = (
        _match_bonus(text_blob, query_terms, W["query_weight"], W["query_cap"])
        if query_terms else 0.0
    )
    address_bonus = (
        _match_bonus(text_blob, address_terms, W["address_weight"], W["address_cap"])
        if not query_terms else 0.0
    )
    search_history_bonus = score_from_search_history(place, recent_queries or [], W)
    pick_history_bonus = score_from_user_pick_history(place, picked_places or [], W)

    saved_bonus = W["saved_bonus"] if place_id in set(saved_ids or []) else 0.0
    picked_bonus = W["picked_bonus"] if place_id in set(picked_ids or []) else 0.0
    preferred_type_bonus = (
        W["preferred_type_bonus"]
        if primary_type and primary_type in {t.lower() for t in (preferred_types or [])}
        else 0.0
    )
    open_bonus = W["open_bonus"] if place.get("open_now") is True else 0.0

    has_history = bool(recent_queries) or bool(picked_ids) or bool(saved_ids) or bool(picked_places)
    random_bonus = 0.0
    if not query_terms and not has_history:
        random_bonus = score_random_baseline(place, seed_text=user_address or "default")

    score = round(
        base_rating + distance_bonus + review_bonus
        + query_bonus + address_bonus
        + search_history_bonus + pick_history_bonus
        + saved_bonus + picked_bonus + preferred_type_bonus
        + open_bonus + random_bonus,
        2,
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
    return score, score_parts


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
    """Attach score and sort descending.  (Signature unchanged.)"""
    ranked: list[dict[str, Any]] = []
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


# ============================================================
# COMPONENT SCORERS  (updated to accept W dict)
# ============================================================

def score_random_baseline(place: dict[str, Any], *, seed_text: str = "") -> float:
    """Calculate default suggestion score when user has no useful history.  (Unchanged.)"""
    if place.get("id") is None:
        return 0.25
    seed = f"{place.get('id')}|{seed_text}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()
    value = int(digest[:8], 16) / 0xFFFFFFFF
    return round(0.45 + value * 0.45, 3)


def score_from_user_pick_history(
    place: dict[str, Any],
    picked_places: list[dict[str, Any]],
    W: dict[str, float] | None = None,
) -> float:
    """Score a place using map/route pick history.

    Owner: TV5.

    Change from original:
    - Accepts optional W dict so dynamic weights propagate to sub-scores.
    - Falls back to _DEFAULT_WEIGHTS when W is not provided.
    """
    if not picked_places:
        return 0.0

    if W is None:
        W = _DEFAULT_WEIGHTS

    primary_type = str(place.get("primary_type") or "").lower()
    place_blob = " ".join([
        str(place.get("name") or "").lower(),
        str(place.get("address") or "").lower(),
        primary_type,
    ])
    total_bonus = 0.0
    for index, picked in enumerate(picked_places[:8]):
        weight = 1.0 if index == 0 else 0.6 if index < 3 else 0.35
        picked_type = str(picked.get("primary_type") or "").lower()
        if picked_type and picked_type == primary_type:
            total_bonus += W["pick_history_type_weight"] * weight

        picked_address = str(picked.get("address") or "").lower()
        if picked_address:
            total_bonus += _match_bonus(
                place_blob,
                _tokenize(picked_address),
                W["pick_history_addr_weight"] * weight,
                0.8 * weight,
            )

        distance_km = _haversine_distance_km(
            place.get("latitude"), place.get("longitude"),
            picked.get("latitude"), picked.get("longitude"),
        )
        if distance_km <= 2.0:
            total_bonus += W["pick_history_near2km"] * weight
        elif distance_km <= 5.0:
            total_bonus += W["pick_history_near5km"] * weight

    return min(total_bonus, W["pick_history_cap"])


def score_from_search_history(
    place: dict[str, Any],
    recent_queries: list[str],
    W: dict[str, float] | None = None,
) -> float:
    """Score a place using at most 80 stored search-history items.

    Owner: TV5.

    Change from original:
    - Accepts optional W dict for dynamic weight propagation.
    """
    if not recent_queries:
        return 0.0

    if W is None:
        W = _DEFAULT_WEIGHTS

    text_blob = " ".join([
        str(place.get("name") or "").lower(),
        str(place.get("address") or "").lower(),
        str(place.get("primary_type") or "").lower(),
    ])
    total_bonus = 0.0
    for query in recent_queries[:12]:
        terms = _tokenize(query)
        total_bonus += _match_bonus(
            text_blob, terms,
            W["search_history_weight"],
            1.1,
        )
    return min(total_bonus, W["search_history_cap"])


# ============================================================
# EXPLANATION  (unchanged — frontend contract stable)
# ============================================================

def explain_score(place: dict[str, Any]) -> dict[str, Any]:
    """Provide user-facing ranking explanation.  (Unchanged.)"""
    score_parts = {
        key: float(value)
        for key, value in place.items()
        if key in {
            "query", "search_history", "pick_history", "favorite", "picked",
            "preferred_type", "open_now", "random_baseline", "address_match",
            "distance", "review",
        }
        and value
    }
    factors = sorted(
        ({"name": name, "value": value, "weight": value} for name, value in score_parts.items() if value > 0),
        key=lambda factor: factor["weight"],
        reverse=True,
    )
    summary = "Gợi ý phù hợp dựa trên điểm đánh giá và lịch sử của bạn."
    if any(f["name"] == "pick_history" for f in factors):
        summary = "Phù hợp với địa điểm bạn đã chọn trước đó."
    elif any(f["name"] == "search_history" for f in factors):
        summary = "Khớp với lịch sử tìm kiếm gần đây của bạn."
    elif any(f["name"] == "favorite" for f in factors):
        summary = "Ưu tiên theo nơi bạn đã yêu thích."
    elif any(f["name"] == "random_baseline" for f in factors):
        summary = "Gợi ý cho bạn hôm nay dựa trên lựa chọn ngẫu nhiên ổn định."
    elif any(f["name"] == "query" for f in factors):
        summary = "Khớp với nhu cầu tìm kiếm của bạn."
    return {"summary": summary, "factors": factors}
