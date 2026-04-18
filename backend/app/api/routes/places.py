from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.place_repo import PlaceRepository
from app.repositories.review_repo import ReviewRepository
from app.schemas.place_schema import PlaceDetailResponse, PlaceResponse, ResolvePlacePointRequest
from app.services.google_places_service import (
    get_place_detail as get_google_place_detail,
    resolve_place_from_coordinates,
)

router = APIRouter()


@router.post("/resolve-point", response_model=PlaceResponse)
def resolve_point_to_place(
    payload: ResolvePlacePointRequest,
    db: Session = Depends(get_db),
) -> PlaceResponse:
    """Resolve a clicked map coordinate into a place that can be viewed and reviewed."""
    item = resolve_place_from_coordinates(payload.latitude, payload.longitude, db=db)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No place information was found for the selected point.",
        )

    average_rating, review_count = ReviewRepository(db).get_place_summary(int(item["id"]))
    effective_rating = average_rating if average_rating is not None else item.get("google_rating") or item.get("rating")

    return PlaceResponse(
        id=int(item["id"]),
        name=item["name"],
        address=item["address"],
        rating=effective_rating,
        review_count=review_count,
        google_rating=item.get("google_rating") or item.get("rating"),
        google_review_count=item.get("google_review_count"),
        web_rating=average_rating,
        web_review_count=review_count,
        distance_km=item.get("distance_km"),
        latitude=item.get("latitude"),
        longitude=item.get("longitude"),
        price_level=item.get("price_level"),
        open_now=item.get("open_now"),
        photo_url=item.get("photo_url"),
        contact_phone=item.get("contact_phone"),
        primary_type=item.get("primary_type"),
        score=item.get("score"),
    )


@router.get("/{place_id}", response_model=PlaceDetailResponse)
def get_place_detail(place_id: int, db: Session = Depends(get_db)) -> PlaceDetailResponse:
    """Return detailed information for a selected place."""
    place_repo = PlaceRepository(db)
    review_repo = ReviewRepository(db)

    place = place_repo.get_by_id(place_id)
    average_rating, review_count = review_repo.get_place_summary(place_id)
    google_detail = None

    if place is not None and place.external_place_id:
        google_detail = get_google_place_detail(place.external_place_id)

    if place is None:
        place_name = "Sample Place" if place_id == 1 else f"Place #{place_id}"
        place_address = "123 Demo Street" if place_id == 1 else "Unknown address"
        google_rating = 4.5 if place_id == 1 else None
        google_review_count = None
        place_rating = average_rating if average_rating is not None else google_rating
        distance_km = 1.2 if place_id == 1 else None
        price_level = 2 if place_id == 1 else None
        open_now = True if place_id == 1 else None
        photo_url = None
        contact_phone = None
        primary_type = "restaurant" if place_id == 1 else None
        score = 9.0 if place_id == 1 else None
        description = "Placeholder detail description." if place_id == 1 else "No description yet."
        opening_hours: list[str] = []
        images: list[str] = []
    else:
        place_name = google_detail.get("name") if google_detail else place.name
        place_address = google_detail.get("address") if google_detail else place.address
        google_rating = (
            google_detail.get("google_rating")
            if google_detail and google_detail.get("google_rating") is not None
            else google_detail.get("rating")
            if google_detail
            else place.rating
        )
        google_review_count = google_detail.get("google_review_count") if google_detail else None
        place_rating = average_rating if average_rating is not None else google_rating
        distance_km = None
        price_level = google_detail.get("price_level") if google_detail else place.price_level
        open_now = google_detail.get("open_now") if google_detail else place.open_now
        photo_url = google_detail.get("photo_url") if google_detail else place.photo_url
        contact_phone = google_detail.get("contact_phone") if google_detail else place.contact_phone
        primary_type = google_detail.get("primary_type") if google_detail else place.primary_type
        score = None
        description = google_detail.get("description") if google_detail else "No description yet."
        opening_hours = google_detail.get("opening_hours") if google_detail else []
        images = google_detail.get("images") if google_detail else []

    return PlaceDetailResponse(
        id=place_id,
        name=place_name,
        address=place_address,
        rating=place_rating,
        google_rating=google_rating,
        google_review_count=google_review_count,
        web_rating=average_rating,
        web_review_count=review_count,
        distance_km=distance_km,
        price_level=price_level,
        open_now=open_now,
        photo_url=photo_url,
        contact_phone=contact_phone,
        primary_type=primary_type,
        score=score,
        description=description,
        review_count=review_count,
        opening_hours=opening_hours,
        images=images,
    )
