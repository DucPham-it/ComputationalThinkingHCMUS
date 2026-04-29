"""Top-level recommendation pipeline.

Owners:
- TV1: API request contract and search-history context.
- TV4: filtering integration.
- TV5: ranking/personalization integration.

File input:
- Natural-language query, UI filters, optional coordinates, and authenticated
  user context.

File output:
- Top 10 place dictionaries consumed by frontend RecommendationList.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.recommendation.filters import apply_filters
from app.recommendation.nlp_parser import parse_search_text
from app.recommendation.ranking import rank_places
from app.repositories.favorite_repo import FavoriteRepository
from app.repositories.pick_repo import PickRepository
from app.repositories.search_history_repo import SearchHistoryRepository
from app.services.place_search_service import search_places


def _place_to_dict(place) -> dict[str, Any]:
    return {
        "id": place.id,
        "name": place.name,
        "address": place.address,
        "external_place_id": place.external_place_id,
        "rating": place.rating,
        "review_count": place.review_count,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "distance_km": None,
        "price_level": place.price_level,
        "price_range": getattr(place, "price_range", None),
        "open_now": place.open_now,
        "photo_url": place.photo_url,
        "contact_phone": place.contact_phone,
        "primary_type": place.primary_type,
        "score": None,
    }


def _dedupe_places(places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []

    for item in places:
        key = (
            f"external:{item.get('external_place_id')}"
            if item.get("external_place_id")
            else f"id:{item.get('id')}"
            if item.get("id") is not None
            else f"text:{(item.get('name') or '').strip().lower()}|{(item.get('address') or '').strip().lower()}"
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped


def recommend_places(
    query: str = "",
    latitude: float | None = None,
    longitude: float | None = None,
    db: Session | None = None,
    user_id: int | None = None,
    user_address: str | None = None,
    entertainment_type: str | None = None,
    budget_level: str | None = None,
    companion_type: str | None = None,
    start_time: str | None = None,
    max_distance_km: float | None = None,
    preferred_types: list[str] | None = None,
    require_open_now: bool = False,
    min_rating: float | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Return top place recommendations.

    Owners:
    - TV1 keeps request parameters compatible with the API route.
    - TV4 owns filter-related arguments.
    - TV5 owns ranking-related output.

    Input:
    - query: natural-language request. Can be empty for default suggestions.
    - latitude/longitude: browser GPS, profile address geocode, or map point.
    - db: SQLAlchemy session. Optional so tests can call without database.
    - user_id: authenticated user id. Optional for guest/default suggestions.
    - user_address: profile address text for ranking fallback.
    - entertainment_type: explicit category filter from UI.
    - budget_level: low/medium/high.
    - companion_type: solo/couple/family/friends/kids.
    - start_time: intended visit time or time slot.
    - max_distance_km: maximum distance radius.
    - preferred_types: explicit category list from UI/history.
    - require_open_now: only keep currently-open places when true.
    - min_rating: minimum rating 0..5.
    - limit: output count, default 10 per project requirement.

    Output:
    - list[dict] of top places sorted by score, length <= limit.
    - Each place should contain id, name, address, latitude, longitude, rating,
      review_count, primary_type, photo_url, open_now, and score when available.
    """
    parsed = parse_search_text(query)
    resolved_type = entertainment_type or parsed.get("entertainment_type")
    resolved_budget = budget_level or parsed.get("budget_level")
    resolved_companion = companion_type or parsed.get("companion_type")
    resolved_time = start_time or parsed.get("time_slot")
    resolved_allowed_types = list(preferred_types or [])
    if resolved_type and resolved_type not in resolved_allowed_types:
        resolved_allowed_types.append(resolved_type)

    places = search_places(
        query=parsed.get("local_query") or query,
        external_query="",
        latitude=latitude,
        longitude=longitude,
        db=db,
    )
    recent_queries: list[str] = []
    saved_ids: list[int] = []
    picked_ids: list[int] = []
    picked_places: list[dict[str, Any]] = []
    preferred_types: list[str] = []

    if db is not None and user_id is not None:
        favorite_repo = FavoriteRepository(db)
        pick_repo = PickRepository(db)
        favorite_places = favorite_repo.list_by_user(user_id, limit=12)
        raw_picked_places = pick_repo.list_by_user(user_id, limit=12)
        recent_queries = SearchHistoryRepository(db).list_recent_queries(user_id, limit=12)
        saved_ids = [place.id for place in favorite_places]
        picked_ids = [place.id for place in raw_picked_places]
        picked_places = [_place_to_dict(place) for place in raw_picked_places]
        history_preferred_types = [
            place.primary_type
            for place in [*favorite_places, *raw_picked_places]
            if place.primary_type
        ]
        preferred_types = [*(preferred_types or []), *history_preferred_types]
        places = _dedupe_places(
            places + [_place_to_dict(place) for place in favorite_places] + picked_places
        )

    filtered = apply_filters(
        places=places,
        max_distance_km=max_distance_km,
        allowed_types=resolved_allowed_types or None,
        require_open_now=require_open_now,
        min_rating=min_rating,
        budget_level=resolved_budget,
    )
    ranked = rank_places(
        filtered,
        query=query,
        user_address=user_address,
        recent_queries=recent_queries,
        saved_ids=saved_ids,
        picked_ids=picked_ids,
        picked_places=picked_places,
        preferred_types=preferred_types,
    )
    return ranked[: max(1, int(limit or 10))]


def build_recommendation_context(
    *,
    user_id: int,
    db: Session,
    query: str,
    ui_filters: dict[str, Any],
) -> dict[str, Any]:
    """TODO TV1/TV5: collect all context for one recommendation request.

    Owners:
    - TV1 collects API/user/history context.
    - TV5 consumes this context for personalization.

    Input:
    - user_id: authenticated user id
    - db: SQLAlchemy session
    - query: raw natural-language request
    - ui_filters: filter controls submitted by frontend:
      entertainment_type, budget_level, companion_type, start_time,
      max_distance_km, require_open_now, min_rating, latitude, longitude

    Output:
    - dict containing:
      - parsed_nlp
      - effective_filters
      - picked_places
      - saved_places
      - recent_queries, max 80
      - candidate_seed_strategy: random, picks, history, query
    """
    pass


def recommend_top_10_contract(context: dict[str, Any]) -> list[dict[str, Any]]:
    """TODO TV5: final top-10 recommendation orchestration contract.

    Owner:
    - TV5.

    Input:
    - context: output from build_recommendation_context

    Output:
    - list with at most 10 items.
    - exactly the shape consumed by PlaceResponse/RecommendationList:
      id, name, address, category, rating, review_count, distance_km, latitude,
      longitude, price_level, price_range, open_now, photo_url, contact_phone,
      primary_type, score, score_parts, explanation.
    """
    pass
