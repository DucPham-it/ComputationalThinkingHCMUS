from pydantic import BaseModel


class RouteRequest(BaseModel):
    """Input for route planning.

    origin may come from browser GPS or manual address.
    destination usually comes from selected place.
    """

    origin: str
    destination: str
    travel_mode: str = "driving"


class RouteStep(BaseModel):
    instruction: str
    distance_text: str | None = None
    duration_text: str | None = None


class RoutePoint(BaseModel):
    lat: float
    lng: float


class RouteResponse(BaseModel):
    """Output for route guidance screen."""

    origin: str
    destination: str
    distance_text: str
    duration_text: str
    distance_km: float | None = None
    duration_seconds: int | None = None
    path: list[RoutePoint] = []
    steps: list[RouteStep] = []
