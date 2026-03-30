from fastapi import APIRouter

from app.schemas.review_schema import ReviewCreateRequest, ReviewResponse, ReviewSubmitResponse

router = APIRouter()


@router.get("")
def list_reviews(place_id: int | None = None) -> dict:
    """List reviews for a place.

    Input:
    - place_id: optional target place identifier

    Output:
    - review list for selected place
    """
    return {"place_id": place_id, "items": []}


@router.post("", response_model=ReviewSubmitResponse)
def create_review(payload: ReviewCreateRequest) -> ReviewSubmitResponse:
    """Submit a new review.

    TODO:
    - save review
    - recalculate average rating and review count
    - auto-add to favorites if rating is 5 according to business rule
    """
    latest_review = ReviewResponse(id=1, place_id=payload.place_id, content=payload.content, rating=payload.rating)
    return ReviewSubmitResponse(
        message="Review submitted successfully.",
        average_rating=float(payload.rating),
        review_count=1,
        latest_review=latest_review,
    )
