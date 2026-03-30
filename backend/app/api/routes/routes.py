from fastapi import APIRouter

from app.schemas.route_schema import RouteResponse, RouteStep
from app.services.directions_service import get_directions

router = APIRouter()


@router.get("/plan", response_model=RouteResponse)
def plan_route(origin: str = "", destination: str = "") -> RouteResponse:
    """Plan route between origin and destination.

    Input:
    - origin: user current position or manual start address
    - destination: selected place address or name

    Output:
    - distance, duration, polyline, and route steps
    """
    data = get_directions(origin=origin, destination=destination)
    return RouteResponse(
        origin=data["origin"],
        destination=data["destination"],
        polyline=data.get("polyline"),
        distance_text=data["distance_text"],
        duration_text=data["duration_text"],
        steps=[RouteStep(**step) for step in data.get("steps", [])],
    )
