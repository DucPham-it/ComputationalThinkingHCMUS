"""Recommendation API routes.

Owners:
- TV1: GET /recommendations request/response and search-history side effect.
- TV6: POST /recommendations/picks/{place_id} for map/route pick history.

File input:
- Query params from frontend recommendation search/filter UI.
- Authenticated user from dependency.
- Place id from map/route pick action.

File output:
- Top 10 recommendation response for frontend.
- Persisted search history and place pick history for personalization.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_completed_profile
from app.db.session import get_db
from app.repositories.pick_repo import PickRepository
from app.repositories.search_history_repo import SearchHistoryRepository
from app.repositories.user_repo import UserRepository
from app.repositories.place_repo import PlaceRepository
from app.recommendation.recommender import recommend_places
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
    max_distance_km: float | None = 5,
    require_open_now: bool = False,
    min_rating: float | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
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
    - max_distance_km: maximum distance radius
    - require_open_now: when true, only return currently-open candidates
    - min_rating: minimum rating 0..5
    - latitude/longitude: GPS or map context
    - current_user: authenticated user with completed profile
    - db: SQLAlchemy session

    Output:
    - {"items": top 10 recommended place dicts}.
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

    history_query = _build_history_query(
        query,
        {
            "entertainment_type": entertainment_type,
            "budget_level": budget_level,
            "companion_type": companion_type,
            "start_time": start_time,
            "max_distance_km": max_distance_km if max_distance_km != 5 else None,
            "require_open_now": require_open_now,
            "min_rating": min_rating,
        },
    )
    if history_query:
        SearchHistoryRepository(db).record_search(
            user_id=current_user["id"],
            query=history_query,
            latitude=effective_latitude,
            longitude=effective_longitude,
        )

    items = recommend_places(
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
        limit=10,
    )
    return {"items": items}


@router.post("/picks/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def record_place_pick(
    place_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Store a place pick so future suggestions can learn from it.

    Owner:
    - TV6.

    Input:
    - place_id: database place id selected from map marker or route destination.
    - current_user: authenticated user from access token.
    - db: SQLAlchemy session.

    Output:
    - HTTP 204 when pick is recorded.
    - HTTP 404 when place_id does not exist.

    Side effect:
    - upserts user_place_picks and refreshes picked_at timestamp.
    """
    place = PlaceRepository(db).get_by_id(place_id)
    if place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found.")
    PickRepository(db).add_pick(current_user["id"], place_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
