"""Top-level recommendation pipeline."""

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
) -> list[dict[str, Any]]:
    parsed = parse_search_text(query)
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
    preferred_types: list[str] = []

    if db is not None and user_id is not None:
        favorite_repo = FavoriteRepository(db)
        pick_repo = PickRepository(db)
        favorite_places = favorite_repo.list_by_user(user_id, limit=12)
        picked_places = pick_repo.list_by_user(user_id, limit=12)
        recent_queries = SearchHistoryRepository(db).list_recent_queries(user_id, limit=12)
        saved_ids = [place.id for place in favorite_places]
        picked_ids = [place.id for place in picked_places]
        preferred_types = [
            place.primary_type
            for place in [*favorite_places, *picked_places]
            if place.primary_type
        ]
        places = _dedupe_places(
            places + [_place_to_dict(place) for place in favorite_places + picked_places]
        )

    filtered = apply_filters(
        places=places,
        allowed_types=[parsed["entertainment_type"]] if parsed.get("entertainment_type") else None,
    )
    return rank_places(
        filtered,
        query=query,
        user_address=user_address,
        recent_queries=recent_queries,
        saved_ids=saved_ids,
        picked_ids=picked_ids,
        preferred_types=preferred_types,
    )
