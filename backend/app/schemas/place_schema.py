"""Place-related request and response schemas."""

from pydantic import BaseModel, Field


class RecommendationQuery(BaseModel):
    """Structured recommendation input.

    Owner:
    - TV1 owns this request schema contract.
    - TV2 mirrors these fields in the frontend filter payload.

    Input:
    - query: natural-language request, for example "toi muon di cafe yen tinh gan day"
    - destination/manual_address: optional location context typed by user
    - entertainment_type: category filter extracted by NLP or selected by UI
    - budget_level: low, medium, high
    - start_time: user intended visit time/time slot
    - companion_type: solo, couple, family, friends
    - latitude/longitude: browser GPS or map-selected point
    - max_distance_km: optional radius constraint. Defaults to no hard
      distance filter so suggestions can still return 10 places.
    - preferred_types: explicit UI category list
    - require_open_now: only suggest currently-open places when true
    - min_rating: minimum average rating filter
    - limit/offset: recommendation pagination for loading more results

    Output:
    - used by routes/recommendations.py to produce top 10 PlaceResponse-like dicts.
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
    max_distance_km: float | None = Field(default=None, ge=0)
    preferred_types: list[str] = Field(default_factory=list)
    require_open_now: bool = False
    min_rating: float | None = Field(default=None, ge=0, le=5)
    limit: int = Field(default=10, ge=1, le=30)
    offset: int = Field(default=0, ge=0)


class ResolvePlacePointRequest(BaseModel):
    latitude: float
    longitude: float


class PlaceResponse(BaseModel):
    """Shared place response shape.

    Owner:
    - TV1 keeps API shape stable.
    - TV5 may add score/explanation-related fields after ranking work.

    Input:
    - place data from local database, external search, or recommendation pipeline.

    Output:
    - JSON-safe place payload consumed by RecommendationList, MapView, and
      PlaceDetail.
    """

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
