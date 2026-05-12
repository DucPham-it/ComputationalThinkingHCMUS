"""Place search service backed by Supabase data with OSM map-point fallback."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.place_repo import PlaceRepository
from app.services.geocoding_service import reverse_geocode_coordinates
from app.utils.distance import haversine_km


def _extract_distance_km(
    user_latitude: float | None,
    user_longitude: float | None,
    place_latitude: float | None,
    place_longitude: float | None,
) -> float | None:
    if (
        user_latitude is None
        or user_longitude is None
        or place_latitude is None
        or place_longitude is None
    ):
        return None

    return round(haversine_km(user_latitude, user_longitude, place_latitude, place_longitude), 2)


def _to_result_item(
    place,
    *,
    latitude: float | None,
    longitude: float | None,
) -> dict[str, Any]:
    return {
        "id": place.id,
        "name": place.name,
        "address": place.address,
        "external_place_id": place.place_id,
        "rating": place.rating,
        "review_count": place.review_count,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "distance_km": _extract_distance_km(
            latitude,
            longitude,
            place.latitude,
            place.longitude,
        ),
        "price_level": place.price_level,
        "price_range": place.price_range,
        "open_now": place.open_now,
        "photo_url": place.photo_url,
        "contact_phone": place.contact_phone,
        "primary_type": place.primary_type,
        "website": place.website,
        "description": place.description,
        "score": None,
        "can_view": True,
        "can_save": True,
        "is_local_only": False,
    }


def search_places(
    query: str = "",
    external_query: str = "",
    latitude: float | None = None,
    longitude: float | None = None,
    db: Session | None = None,
    limit: int = 60,
) -> list[dict[str, Any]]:
    del external_query

    if db is None:
        return []

    place_repo = PlaceRepository(db)
    local_places = place_repo.search_local_places(query, limit=limit)
    return [
        _to_result_item(place, latitude=latitude, longitude=longitude)
        for place in local_places
    ]


def resolve_place_from_coordinates(
    latitude: float,
    longitude: float,
    *,
    db: Session | None = None,
) -> dict[str, Any] | None:
    if db is None:
        return None

    place = PlaceRepository(db).find_nearest_place(
        latitude=latitude,
        longitude=longitude,
        max_distance_km=settings.resolve_point_local_match_radius_km,
    )
    if place is None:
        osm_point = reverse_geocode_coordinates(latitude, longitude)
        if osm_point is None:
            return None

        return {
            "id": f"osm:{round(latitude, 6)}:{round(longitude, 6)}",
            "name": osm_point["name"],
            "address": osm_point["address"],
            "external_place_id": None,
            "rating": None,
            "review_count": 0,
            "latitude": osm_point["latitude"],
            "longitude": osm_point["longitude"],
            "distance_km": 0.0,
            "price_level": None,
            "price_range": None,
            "open_now": None,
            "photo_url": None,
            "contact_phone": None,
            "primary_type": "osm_point",
            "website": None,
            "description": None,
            "score": 0.0,
            "can_view": False,
            "can_save": False,
            "is_local_only": True,
        }

    item = _to_result_item(place, latitude=latitude, longitude=longitude)
    item["score"] = round(max(0.0, 10.0 - (item.get("distance_km") or 0.0)), 2)
    return item
