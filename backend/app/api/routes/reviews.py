from fastapi import APIRouter, Depends, HTTPException, status
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
    if place_id is None:
        return {"place_id": None, "items": []}

    review_repo = ReviewRepository(db)
    items = [
        ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            user_name=review.user_name,
            user_avatar_url=review.user_avatar_url,
            place_id=review.place_id,
            content=review.content,
            rating=review.rating,
            reviewed_at=review.reviewed_at,
            image_urls=review.image_urls,
            is_virtual_user=review.is_virtual_user,
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
    place_repo = PlaceRepository(db)
    review_repo = ReviewRepository(db)
    favorite_repo = FavoriteRepository(db)

    place = place_repo.get_by_id(payload.place_id)
    if place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found in the local catalog.",
        )

    latest_review = review_repo.create_review(
        user_id=current_user["id"],
        place_id=payload.place_id,
        content=payload.content,
        rating=payload.rating,
        image_urls=payload.image_urls,
    )
    updated_place = place_repo.append_review_summary(payload.place_id, payload.rating)

    if payload.rating == 5:
        favorite_repo.add_favorite(current_user["id"], payload.place_id)

    return ReviewSubmitResponse(
        message="Review submitted successfully.",
        average_rating=float(updated_place.rating or 0),
        review_count=int(updated_place.review_count or 0),
        latest_review=ReviewResponse(
            id=latest_review.id,
            user_id=latest_review.user_id,
            user_name=latest_review.user_name,
            user_avatar_url=latest_review.user_avatar_url,
            place_id=latest_review.place_id,
            content=latest_review.content,
            rating=latest_review.rating,
            reviewed_at=latest_review.reviewed_at,
            image_urls=latest_review.image_urls,
            is_virtual_user=latest_review.is_virtual_user,
        ),
    )
