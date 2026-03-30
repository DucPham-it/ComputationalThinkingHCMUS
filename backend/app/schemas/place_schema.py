"""Place-related request and response schemas."""

from pydantic import BaseModel, Field


class RecommendationQuery(BaseModel):
    """Structured recommendation input.

    This schema represents what the frontend should eventually send to the backend
    after combining manual user input, browser location, and NLP-extracted intent.

    Input fields:
    - query: free text search, e.g. "quán ăn tối gần tôi"
    - destination: destination name or area
    - entertainment_type: user target category, e.g. restaurant, movie_theater
    - budget_level: approximate budget bucket
    - start_time: intended time of use
    - companion_type: solo, couple, family, friends
    - latitude/longitude: browser GPS if available
    - manual_address: fallback when GPS is unavailable
    - max_distance_km: filter radius
    - preferred_types: Google Maps place types
    """

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
    preferred_types: list[str] = []


class PlaceResponse(BaseModel):
    """Summary output shown in recommendation list.

    Output fields match your expected UI card:
    - id, name, address, rating
    - fields below are optional until corresponding services are implemented
    """

    id: int
    name: str
    address: str
    rating: float | None = None
    distance_km: float | None = None
    price_level: int | None = None
    open_now: bool | None = None
    photo_url: str | None = None
    contact_phone: str | None = None
    primary_type: str | None = None
    score: float | None = None


class PlaceDetailResponse(PlaceResponse):
    """Detailed place output for place detail page."""

    description: str | None = None
    review_count: int | None = None
    opening_hours: list[str] = []
    images: list[str] = []
