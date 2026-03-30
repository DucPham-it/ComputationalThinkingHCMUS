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


class RouteResponse(BaseModel):
    """Output for route guidance screen."""

    origin: str
    destination: str
    distance_text: str
    duration_text: str
    polyline: str | None = None
    steps: list[RouteStep] = []
