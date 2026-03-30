from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    """Input when a user submits a review.

    Rules expected by system:
    - rating range 1..5
    - content should be non-empty
    - if rating is 5, backend may auto-add place to favorites later
    """

    place_id: int
    content: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)
    image_urls: list[str] = []


class ReviewResponse(BaseModel):
    """Single review returned by API."""

    id: int
    place_id: int
    content: str
    rating: int


class ReviewSubmitResponse(BaseModel):
    """Output after review submission."""

    message: str
    average_rating: float
    review_count: int
    latest_review: ReviewResponse
