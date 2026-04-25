"""Recommendation pick API routes.

Owner:
- TV6: Map Pick To Route.

File input:
- place_id selected from map marker, place card, or route destination.
- Authenticated user from access token.

File output:
- HTTP 204 when the pick is stored.
- HTTP 404 when the selected place does not exist.
- Side effect: user_place_picks is upserted for personalization.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.repositories.pick_repo import PickRepository
from app.repositories.place_repo import PlaceRepository

router = APIRouter()


@router.post("/picks/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def record_place_pick(
    place_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Store a place pick so future suggestions can learn from it.

    Owner:
    - TV6.

    Input:
    - place_id: database place id selected from map marker, place card, or
      route destination.
    - current_user: authenticated user from access token.
    - db: SQLAlchemy session.

    Output:
    - HTTP 204 when pick is recorded.
    - HTTP 404 when place_id does not exist.

    Side effect:
    - upserts user_place_picks and refreshes picked_at timestamp.
    """
    place = PlaceRepository(db).get_by_id(place_id)
    if place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found.")
    PickRepository(db).add_pick(current_user["id"], place_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
