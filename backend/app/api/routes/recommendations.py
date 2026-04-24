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


@router.get("")
def get_recommendations(
    query: str = "",
    latitude: float | None = None,
    longitude: float | None = None,
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> dict:
    """Recommendation list endpoint.

    Input:
    - query: free-text search string from frontend

    Output:
    - list of recommended places

    Future extension:
    - replace simple query params with structured recommendation payload
    - add browser GPS coordinates and filter params
    """
    user = UserRepository(db).get_by_id(current_user["id"])
    effective_latitude = latitude
    effective_longitude = longitude

    if (effective_latitude is None or effective_longitude is None) and user and user.address:
        geocoded_address = geocode_address(user.address, db=db)
        effective_latitude = geocoded_address.get("latitude")
        effective_longitude = geocoded_address.get("longitude")

    if query.strip():
        SearchHistoryRepository(db).record_search(
            user_id=current_user["id"],
            query=query,
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
    )
    return {"items": items}


@router.post("/picks/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def record_place_pick(
    place_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Store a place pick so future suggestions can learn from it."""
    place = PlaceRepository(db).get_by_id(place_id)
    if place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found.")
    PickRepository(db).add_pick(current_user["id"], place_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
