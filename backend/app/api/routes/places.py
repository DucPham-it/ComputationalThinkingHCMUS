from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.place_repo import PlaceRepository
from app.repositories.review_repo import ReviewRepository
from app.schemas.place_schema import PlaceDetailResponse
from app.services.google_places_service import get_place_detail as get_google_place_detail

router = APIRouter()


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
        place_rating = average_rating if average_rating is not None else (4.5 if place_id == 1 else None)
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
        place_rating = average_rating if average_rating is not None else place.rating
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
