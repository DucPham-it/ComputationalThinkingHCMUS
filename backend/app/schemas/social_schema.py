"""Social feed request and response schemas."""

from pydantic import BaseModel, Field


class VisitedPlaceCreateRequest(BaseModel):
    place_id: int
    route_origin: str | None = Field(default=None, max_length=1000)
    route_destination: str | None = Field(default=None, max_length=1000)
    distance_text: str | None = Field(default=None, max_length=100)
    duration_text: str | None = Field(default=None, max_length=100)
    distance_km: float | None = None
    duration_seconds: int | None = None
    travel_mode: str | None = Field(default=None, max_length=50)


RouteCompletionRequest = VisitedPlaceCreateRequest


class VisitedPlaceResponse(BaseModel):
    id: int
    user_id: int
    place_id: int
    place_name: str
    place_address: str
    place_photo_url: str | None = None
    place_rating: float | None = None
    route_origin: str | None = None
    route_destination: str | None = None
    distance_text: str | None = None
    duration_text: str | None = None
    distance_km: float | None = None
    duration_seconds: int | None = None
    travel_mode: str | None = None
    visited_at: str | None = None


class SocialPostCreateRequest(BaseModel):
    visited_place_id: int
    content: str = Field(min_length=1, max_length=4000)
    rating: int = Field(ge=1, le=5)


class SocialPostUpdateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    rating: int = Field(ge=1, le=5)


class SocialCommentCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class SocialCommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    user_name: str | None = None
    user_avatar_url: str | None = None
    content: str
    created_at: str | None = None
    updated_at: str | None = None
    is_owner: bool = False


class SocialPostResponse(BaseModel):
    id: int
    user_id: int
    user_name: str | None = None
    user_avatar_url: str | None = None
    place_id: int
    place_name: str | None = None
    place_address: str | None = None
    place_photo_url: str | None = None
    visited_place_id: int | None = None
    visited_at: str | None = None
    content: str
    rating: int
    created_at: str | None = None
    updated_at: str | None = None
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    viewer_has_liked: bool = False
    viewer_has_shared: bool = False
    is_owner: bool = False
    timeline_type: str = "post"
    shared_at: str | None = None
    comments: list[SocialCommentResponse] = Field(default_factory=list)


class SocialFeedResponse(BaseModel):
    items: list[SocialPostResponse] = Field(default_factory=list)


class SocialProfileUserResponse(BaseModel):
    id: int
    user_name: str
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    address: str | None = None


class SocialProfileStatsResponse(BaseModel):
    post_count: int = 0
    shared_count: int = 0
    visited_count: int = 0


class SocialProfileResponse(BaseModel):
    user: SocialProfileUserResponse
    is_self: bool = False
    stats: SocialProfileStatsResponse
    items: list[SocialPostResponse] = Field(default_factory=list)
