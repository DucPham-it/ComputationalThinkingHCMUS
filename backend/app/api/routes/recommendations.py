"""Recommendation API routes.

Owner:
- TV1: GET /recommendations request/response and search-history side effect.

File input:
- Query params from frontend recommendation search/filter UI.
- Authenticated user from dependency.

File output:
- Top 10 recommendation response for frontend.
- Persisted search history for personalization.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_completed_profile
from app.db.session import get_db
from app.recommendation.recommender import recommend_places
from app.repositories.search_history_repo import SearchHistoryRepository
from app.repositories.user_repo import UserRepository
from app.services.geocoding_service import geocode_address

router = APIRouter()


def _build_history_query(query: str, filters: dict) -> str:
    """Build searchable history text from natural-language input and filter-only searches.

    Owner:
    - TV1.

    Input:
    - query: raw text typed by user. Can be empty.
    - filters: explicit filter values from recommendation request, including
      entertainment_type, budget_level, companion_type, start_time,
      max_distance_km, require_open_now, min_rating.

    Output:
    - compact text stored in user_search_history.query.
    - returns query unchanged when user typed text.
    - returns "key:value" pairs when user used only filters.
    - returns empty string when there is nothing meaningful to store.
    """
    normalized_query = query.strip()
    if normalized_query:
        return normalized_query

    filter_parts = [f"{key}:{value}" for key, value in filters.items() if value not in {None, "", False}]
    return " ".join(filter_parts)


@router.get("")
def get_recommendations(
    query: str = "",
    entertainment_type: str | None = None,
    budget_level: str | None = None,
    companion_type: str | None = None,
    start_time: str | None = None,
    max_distance_km: float | None = None,
    require_open_now: bool = False,
    min_rating: float | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    limit: int = Query(default=10, ge=1, le=30),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> dict:
    """Recommendation list endpoint.

    Owner:
    - TV1.

    Input:
    - query: natural-language search string from frontend
    - entertainment_type: explicit UI category filter, overrides NLP category
    - budget_level: low/medium/high filter
    - companion_type: solo/couple/family/friends preference
    - start_time: intended visit time or time slot
    - max_distance_km: optional maximum distance radius. When omitted, default
      suggestions are ranked from the full candidate set instead of being
      limited to 5km.
    - require_open_now: when true, only return currently-open candidates
    - min_rating: minimum rating 0..5
    - latitude/longitude: GPS or map context
    - limit: number of ranked places to return, default 10, max 30
    - offset: number of ranked places to skip for "load more"
    - current_user: authenticated user with completed profile
    - db: SQLAlchemy session

    Output:
    - {"items": ranked place dicts, "has_more", "next_offset", "limit", "offset"}.
    - Each item should be compatible with PlaceResponse/RecommendationList:
      id, name, address, latitude, longitude, rating, review_count,
      primary_type/category, photo_url/thumbnail, score, explanation if present.

    Side effects:
    - stores query/filter text in user_search_history when meaningful.
    - SearchHistoryRepository trims each user to max 80 rows.

    Future extension:
    - replace GET params with POST RecommendationQuery when filter UI is complete
    - include per-place ranking explanation
    """
    user = UserRepository(db).get_by_id(current_user["id"])
    effective_latitude = latitude
    effective_longitude = longitude

    if (effective_latitude is None or effective_longitude is None) and user and user.address:
        geocoded_address = geocode_address(user.address, db=db)
        effective_latitude = geocoded_address.get("latitude")
        effective_longitude = geocoded_address.get("longitude")

    safe_limit = min(max(int(limit or 10), 1), 30)
    safe_offset = max(int(offset or 0), 0)

    history_query = _build_history_query(
        query,
        {
            "entertainment_type": entertainment_type,
            "budget_level": budget_level,
            "companion_type": companion_type,
            "start_time": start_time,
            "max_distance_km": max_distance_km,
            "require_open_now": require_open_now,
            "min_rating": min_rating,
        },
    )
    if history_query and safe_offset == 0:
        SearchHistoryRepository(db).record_search(
            user_id=current_user["id"],
            query=history_query,
            latitude=effective_latitude,
            longitude=effective_longitude,
        )

    page_items = recommend_places(
        query=query,
        latitude=effective_latitude,
        longitude=effective_longitude,
        db=db,
        user_id=current_user["id"],
        user_address=user.address if user else None,
        entertainment_type=entertainment_type,
        budget_level=budget_level,
        companion_type=companion_type,
        start_time=start_time,
        max_distance_km=max_distance_km,
        require_open_now=require_open_now,
        min_rating=min_rating,
        limit=safe_limit + 1,
        offset=safe_offset,
    )
    items = page_items[:safe_limit]
    has_more = len(page_items) > safe_limit
    return {
        "items": items,
        "limit": safe_limit,
        "offset": safe_offset,
        "has_more": has_more,
        "next_offset": safe_offset + len(items) if has_more else None,
    }
