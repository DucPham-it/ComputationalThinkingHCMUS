"""User-facing place change request routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.repositories.place_repo import PlaceRepository
from app.repositories.place_request_repo import PlaceRequestRepository
from app.schemas.admin_schema import PlaceChangeRequestCreate, PlaceChangeRequestResponse

router = APIRouter()


def _validate_request_payload(payload: PlaceChangeRequestCreate, db: Session) -> None:
    if payload.request_type == "create":
        if not payload.title or not payload.address_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="New place requests require title and address.",
            )
        return

    if payload.place_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Update/delete requests require an existing place_id.",
        )

    if PlaceRepository(db).get_by_id(payload.place_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target place was not found in the local catalog.",
        )


@router.post("", response_model=PlaceChangeRequestResponse, status_code=status.HTTP_201_CREATED)
def create_place_change_request(
    payload: PlaceChangeRequestCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlaceChangeRequestResponse:
    """Create a user request to add, edit, or delete a place."""
    _validate_request_payload(payload, db)
    item = PlaceRequestRepository(db).create_request(
        requester_user_id=current_user["id"],
        payload=payload,
    )
    return PlaceChangeRequestResponse(**item)


@router.get("/my", response_model=list[PlaceChangeRequestResponse])
def list_my_place_change_requests(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PlaceChangeRequestResponse]:
    items = PlaceRequestRepository(db).list_for_user(current_user["id"])
    return [PlaceChangeRequestResponse(**item) for item in items]

