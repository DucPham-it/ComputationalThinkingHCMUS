"""Admin management and place request approval routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.repositories.admin_repo import AdminRepository
from app.repositories.place_repo import PlaceRepository
from app.repositories.place_request_repo import PlaceRequestRepository
from app.repositories.review_repo import ReviewRepository
from app.schemas.admin_schema import (
    AdminDecisionRequest,
    AdminMemberResponse,
    AdminProfileResponse,
    PlaceChangeRequestResponse,
)

router = APIRouter()


@router.get("/me", response_model=AdminProfileResponse)
def get_my_admin_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdminProfileResponse:
    profile = AdminRepository(db).get_profile(current_user["id"])
    if profile is None:
        return AdminProfileResponse(user_id=current_user["id"])
    return AdminProfileResponse(**profile)


@router.post("/apply", response_model=AdminProfileResponse)
def apply_for_admin_access(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdminProfileResponse:
    profile = AdminRepository(db).request_access(current_user["id"])
    return AdminProfileResponse(**profile)


@router.get("/members", response_model=list[AdminMemberResponse])
def list_admin_members(
    current_admin: dict = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminMemberResponse]:
    del current_admin
    return [AdminMemberResponse(**item) for item in AdminRepository(db).list_members()]


@router.post("/members/{user_id}/approve", response_model=AdminProfileResponse)
def approve_admin_member(
    user_id: int,
    current_admin: dict = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminProfileResponse:
    profile = AdminRepository(db).approve_member(user_id=user_id, approved_by=current_admin["id"])
    return AdminProfileResponse(**profile)


@router.post("/members/{user_id}/reject", response_model=AdminProfileResponse)
def reject_admin_member(
    user_id: int,
    current_admin: dict = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminProfileResponse:
    profile = AdminRepository(db).reject_member(user_id=user_id, approved_by=current_admin["id"])
    return AdminProfileResponse(**profile)


@router.get("/place-requests", response_model=list[PlaceChangeRequestResponse])
def list_place_requests(
    status_filter: str | None = None,
    current_admin: dict = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[PlaceChangeRequestResponse]:
    del current_admin
    normalized_status = status_filter if status_filter in {"pending", "approved", "rejected"} else None
    items = PlaceRequestRepository(db).list_all(status=normalized_status)
    return [PlaceChangeRequestResponse(**item) for item in items]


@router.post("/place-requests/{request_id}/approve", response_model=PlaceChangeRequestResponse)
def approve_place_request(
    request_id: int,
    payload: AdminDecisionRequest,
    current_admin: dict = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PlaceChangeRequestResponse:
    request_repo = PlaceRequestRepository(db)
    place_repo = PlaceRepository(db)
    request_item = request_repo.get_by_id(request_id)
    if request_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place request not found.")
    if request_item["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Place request is already reviewed.")

    target_place_id = request_item.get("target_place_id")
    request_type = request_item["request_type"]

    if request_type == "create":
        created_place = place_repo.create_local_place(
            name=request_item["title"],
            address=request_item["address_text"],
            latitude=request_item.get("latitude"),
            longitude=request_item.get("longitude"),
            price_level=request_item.get("price_level"),
            photo_url=(request_item.get("place_image_urls") or [None])[0],
            contact_phone=request_item.get("phone"),
            primary_type=request_item.get("category"),
        )
        target_place_id = created_place.id
        place_repo.update_catalog_place(
            target_place_id,
            price_range=request_item.get("price_range"),
            website=request_item.get("website"),
            descriptions=request_item.get("descriptions"),
            image_urls=request_item.get("place_image_urls") or [],
        )
    elif request_type == "update":
        if target_place_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Missing target place.")
        place_repo.update_catalog_place(
            target_place_id,
            title=request_item.get("title"),
            category=request_item.get("category"),
            address_text=request_item.get("address_text"),
            latitude=request_item.get("latitude"),
            longitude=request_item.get("longitude"),
            price_range=request_item.get("price_range"),
            price_level=request_item.get("price_level"),
            website=request_item.get("website"),
            phone=request_item.get("phone"),
            descriptions=request_item.get("descriptions"),
            image_urls=request_item.get("place_image_urls") or None,
        )
    elif request_type == "delete":
        if target_place_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Missing target place.")
        place_repo.soft_delete_place(target_place_id)

    if target_place_id and request_item.get("review_content") and request_item.get("review_rating"):
        latest_review = ReviewRepository(db).create_review(
            user_id=request_item["requester_user_id"],
            place_id=target_place_id,
            content=request_item["review_content"],
            rating=request_item["review_rating"],
            image_urls=request_item.get("review_image_urls") or [],
        )
        place_repo.append_review_summary(latest_review.place_id, latest_review.rating)

    updated_item = request_repo.mark_reviewed(
        request_id=request_id,
        status="approved",
        admin_user_id=current_admin["id"],
        admin_note=payload.note,
        target_place_id=target_place_id,
    )
    return PlaceChangeRequestResponse(**updated_item)


@router.post("/place-requests/{request_id}/reject", response_model=PlaceChangeRequestResponse)
def reject_place_request(
    request_id: int,
    payload: AdminDecisionRequest,
    current_admin: dict = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PlaceChangeRequestResponse:
    request_repo = PlaceRequestRepository(db)
    request_item = request_repo.get_by_id(request_id)
    if request_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place request not found.")
    if request_item["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Place request is already reviewed.")

    updated_item = request_repo.mark_reviewed(
        request_id=request_id,
        status="rejected",
        admin_user_id=current_admin["id"],
        admin_note=payload.note,
    )
    return PlaceChangeRequestResponse(**updated_item)

