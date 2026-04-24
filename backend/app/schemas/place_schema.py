"""Place-related request and response schemas."""

from pydantic import BaseModel, Field


class RecommendationQuery(BaseModel):
    query: str = ""
    destination: str | None = None
    entertainment_type: str | None = None
    budget_level: str | None = None
    start_time: str | None = None
    companion_type: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    manual_address: str | None = None
    max_distance_km: float | None = Field(default=5, ge=0)
    preferred_types: list[str] = Field(default_factory=list)


class ResolvePlacePointRequest(BaseModel):
    latitude: float
    longitude: float


class PlaceResponse(BaseModel):
    id: int | str
    name: str
    address: str
    category: str | None = None
    rating: float | None = None
    review_count: int = 0
    distance_km: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    price_level: int | None = None
    price_range: str | None = None
    open_now: bool | None = None
    photo_url: str | None = None
    contact_phone: str | None = None
    primary_type: str | None = None
    website: str | None = None
    score: float | None = None
    can_view: bool = True
    can_save: bool = True
    is_local_only: bool = False


class PlaceDetailResponse(PlaceResponse):
    description: str | None = None
    opening_hours: dict[str, list[str]] = Field(default_factory=dict)
    popular_times: dict[str, dict[str, int]] = Field(default_factory=dict)
    images: list[str] = Field(default_factory=list)
    about: list[dict] = Field(default_factory=list)
    status: str | None = None
    place_id: str | None = None
    cid: str | None = None
