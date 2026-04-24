from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    place_id: int
    content: str = Field(min_length=1)
    rating: int = Field(ge=1, le=5)
    image_urls: list[str] = Field(default_factory=list)


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: str | None = None
    user_avatar_url: str | None = None
    place_id: int
    content: str
    rating: int
    reviewed_at: str | None = None
    image_urls: list[str] = Field(default_factory=list)
    is_virtual_user: bool = False


class ReviewSubmitResponse(BaseModel):
    message: str
    average_rating: float
    review_count: int
    latest_review: ReviewResponse
