from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_completed_profile
from app.db.session import get_db
from app.repositories.pick_repo import PickRepository
from app.repositories.review_repo import ReviewRepository
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
        geocoded_address = geocode_address(user.address)
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
    place_ids = [
        int(item["id"])
        for item in items
        if item.get("id") is not None and str(item.get("id")).isdigit()
    ]
    review_summaries = ReviewRepository(db).get_place_summaries(place_ids)

    enriched_items = []
    for item in items:
        normalized_item = dict(item)
        normalized_item.setdefault("google_rating", normalized_item.get("rating"))
        normalized_item.setdefault("google_review_count", None)
        place_id = normalized_item.get("id")
        if isinstance(place_id, int) and place_id in review_summaries:
            summary = review_summaries[place_id]
            normalized_item["web_rating"] = summary.get("average_rating")
            normalized_item["web_review_count"] = summary.get("review_count", 0)
            if summary.get("average_rating") is not None:
                normalized_item["rating"] = summary["average_rating"]
            normalized_item["review_count"] = summary.get("review_count", 0)
        else:
            normalized_item.setdefault("web_rating", None)
            normalized_item.setdefault("web_review_count", 0)
            normalized_item.setdefault("review_count", 0)
        enriched_items.append(normalized_item)
    return {"items": enriched_items}


@router.post("/picks/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def record_place_pick(
    place_id: int,
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> Response:
    """Store a place pick so future suggestions can learn from it."""
    PlaceRepository(db).ensure_exists(place_id)
    PickRepository(db).add_pick(current_user["id"], place_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
