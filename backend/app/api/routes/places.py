from fastapi import APIRouter

from app.schemas.place_schema import PlaceDetailResponse

router = APIRouter()


@router.get("/{place_id}", response_model=PlaceDetailResponse)
def get_place_detail(place_id: int) -> PlaceDetailResponse:
    """Return detailed information for a selected place.

    Input:
    - place_id from frontend route `/places/:id`

    Output:
    - detail payload for detail page including address, rating, images, hours, contact

    TODO:
    - fetch Google Place Details
    - merge internal description and internal reviews summary
    """
    return PlaceDetailResponse(
        id=place_id,
        name="Sample Place",
        address="123 Demo Street",
        rating=4.5,
        distance_km=1.2,
        price_level=2,
        open_now=True,
        photo_url=None,
        contact_phone=None,
        primary_type="restaurant",
        score=9.0,
        description="Placeholder detail description.",
        review_count=0,
        opening_hours=[],
        images=[],
    )
