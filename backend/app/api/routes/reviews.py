from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.repositories.favorite_repo import FavoriteRepository
from app.repositories.place_repo import PlaceRepository
from app.repositories.review_repo import ReviewRepository
from app.schemas.review_schema import ReviewCreateRequest, ReviewResponse, ReviewSubmitResponse

router = APIRouter()


@router.get("")
def list_reviews(place_id: int | None = None, db: Session = Depends(get_db)) -> dict:
    """List reviews for a place."""
    if place_id is None:
        return {"place_id": None, "items": []}

    review_repo = ReviewRepository(db)
    items = [
        ReviewResponse(
            id=review.id,
            place_id=review.place_id,
            content=review.content,
            rating=review.rating,
        )
        for review in review_repo.list_by_place(place_id)
    ]
    return {"place_id": place_id, "items": items}


@router.post("", response_model=ReviewSubmitResponse)
def create_review(
    payload: ReviewCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReviewSubmitResponse:
    """Submit a new review."""
    place_repo = PlaceRepository(db)
    review_repo = ReviewRepository(db)
    favorite_repo = FavoriteRepository(db)

    place_repo.ensure_exists(payload.place_id)
    latest_review = review_repo.create_review(
        user_id=current_user["id"],
        place_id=payload.place_id,
        content=payload.content,
        rating=payload.rating,
    )
    average_rating, review_count = review_repo.get_place_summary(payload.place_id)
    place_repo.update_rating(payload.place_id, average_rating)

    if payload.rating == 5:
        favorite_repo.add_favorite(current_user["id"], payload.place_id)

    return ReviewSubmitResponse(
        message="Review submitted successfully.",
        average_rating=float(average_rating or 0),
        review_count=review_count,
        latest_review=ReviewResponse(
            id=latest_review.id,
            place_id=latest_review.place_id,
            content=latest_review.content,
            rating=latest_review.rating,
        ),
    )
