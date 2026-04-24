from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_completed_profile
from app.db.session import get_db
from app.schemas.route_schema import RoutePoint, RouteResponse, RouteStep
from app.services.routing_service import plan_route as plan_local_route

router = APIRouter()


@router.get("/plan", response_model=RouteResponse)
def plan_route(
    origin: str = "",
    destination: str = "",
    travel_mode: str = "driving",
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> RouteResponse:
    """Plan route between origin and destination.

    Input:
    - origin: user current position or manual start address
    - destination: selected place address or name

    Output:
    - distance, duration, path, and route steps
    """
    _ = current_user
    data = plan_local_route(
        origin_text=origin,
        destination_text=destination,
        travel_mode=travel_mode,
        db=db,
    )
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="We could not resolve the start point or destination for route planning.",
        )

    return RouteResponse(
        origin=data["origin"],
        destination=data["destination"],
        distance_text=data["distance_text"],
        distance_km=data.get("distance_km"),
        duration_text=data["duration_text"],
        duration_seconds=data.get("duration_seconds"),
        path=[RoutePoint(**point) for point in data.get("path", [])],
        steps=[RouteStep(**step) for step in data.get("steps", [])],
    )
