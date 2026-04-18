from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.repositories.favorite_repo import FavoriteRepository
from app.repositories.place_repo import PlaceRepository
from app.repositories.review_repo import ReviewRepository

router = APIRouter()


@router.get("")
def list_favorites(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return favorite places of current user."""
    favorite_repo = FavoriteRepository(db)
    items = favorite_repo.list_by_user(current_user["id"])
    review_summaries = ReviewRepository(db).get_place_summaries([place.id for place in items])

    serialized_items = []
    for place in items:
        summary = review_summaries.get(place.id, {})
        serialized_items.append(
            {
                "id": place.id,
                "name": place.name,
                "address": place.address,
                "rating": summary.get("average_rating", place.rating),
                "review_count": summary.get("review_count", 0),
                "latitude": place.latitude,
                "longitude": place.longitude,
                "price_level": place.price_level,
                "open_now": place.open_now,
                "photo_url": place.photo_url,
                "contact_phone": place.contact_phone,
                "primary_type": place.primary_type,
            }
        )

    return {"items": serialized_items}


@router.post("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def save_favorite(
    place_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Save a place to the current user's saved list."""
    PlaceRepository(db).ensure_exists(place_id)
    FavoriteRepository(db).add_favorite(current_user["id"], place_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    place_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Remove a place from the current user's saved list."""
    FavoriteRepository(db).remove_favorite(current_user["id"], place_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
