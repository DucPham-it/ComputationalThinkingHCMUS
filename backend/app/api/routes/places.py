from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.place_repo import PlaceRepository
from app.schemas.place_schema import PlaceDetailResponse, PlaceResponse, ResolvePlacePointRequest
from app.services.place_search_service import resolve_place_from_coordinates

router = APIRouter()


@router.post("/resolve-point", response_model=PlaceResponse)
def resolve_point_to_place(
    payload: ResolvePlacePointRequest,
    db: Session = Depends(get_db),
) -> PlaceResponse:
    item = resolve_place_from_coordinates(payload.latitude, payload.longitude, db=db)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No local place information was found for the selected point.",
        )

    return PlaceResponse(
        id=item["id"],
        name=item["name"],
        address=item["address"],
        category=item.get("primary_type"),
        rating=item.get("rating"),
        review_count=int(item.get("review_count") or 0),
        distance_km=item.get("distance_km"),
        latitude=item.get("latitude"),
        longitude=item.get("longitude"),
        price_level=item.get("price_level"),
        price_range=item.get("price_range"),
        open_now=item.get("open_now"),
        photo_url=item.get("photo_url"),
        contact_phone=item.get("contact_phone"),
        primary_type=item.get("primary_type"),
        website=item.get("website"),
        score=item.get("score"),
        can_view=bool(item.get("can_view", True)),
        can_save=bool(item.get("can_save", True)),
        is_local_only=bool(item.get("is_local_only", False)),
    )


@router.get("/{place_id}", response_model=PlaceDetailResponse)
def get_place_detail(place_id: int, db: Session = Depends(get_db)) -> PlaceDetailResponse:
    place = PlaceRepository(db).get_by_id(place_id)
    if place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found in the local catalog.",
        )

    return PlaceDetailResponse(
        id=place.id,
        name=place.name,
        address=place.address,
        category=place.category,
        rating=place.rating,
        review_count=place.review_count,
        distance_km=None,
        latitude=place.latitude,
        longitude=place.longitude,
        price_level=place.price_level,
        price_range=place.price_range,
        open_now=place.open_now,
        photo_url=place.photo_url,
        contact_phone=place.contact_phone,
        primary_type=place.primary_type,
        website=place.website,
        score=None,
        can_view=True,
        can_save=True,
        is_local_only=False,
        description=place.description,
        opening_hours=place.opening_hours,
        popular_times=place.popular_times,
        images=place.images,
        about=place.about,
        status=place.status,
        place_id=place.place_id,
        cid=place.cid,
    )
