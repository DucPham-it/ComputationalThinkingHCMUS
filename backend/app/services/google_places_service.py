"""Google Places API wrapper."""

from __future__ import annotations

from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.place_repo import PlaceRepository
from app.services.maps_helper import build_google_photo_url
from app.utils.distance import haversine_km

TEXT_SEARCH_ENDPOINT = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACE_DETAILS_ENDPOINT = "https://maps.googleapis.com/maps/api/place/details/json"
REQUEST_TIMEOUT_SECONDS = 10


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


def _normalize_google_search_result(
    raw_place: dict[str, Any],
    *,
    latitude: float | None,
    longitude: float | None,
) -> dict[str, Any]:
    location = raw_place.get("geometry", {}).get("location", {})
    place_latitude = location.get("lat")
    place_longitude = location.get("lng")
    photo_reference = None
    photos = raw_place.get("photos") or []
    if photos:
        photo_reference = photos[0].get("photo_reference")

    types = raw_place.get("types") or []
    primary_type = types[0] if types else None

    return {
        "external_place_id": raw_place.get("place_id"),
        "name": raw_place.get("name") or "Unknown Place",
        "address": raw_place.get("formatted_address") or raw_place.get("vicinity") or "",
        "rating": raw_place.get("rating"),
        "latitude": place_latitude,
        "longitude": place_longitude,
        "distance_km": _extract_distance_km(latitude, longitude, place_latitude, place_longitude),
        "price_level": raw_place.get("price_level"),
        "open_now": (raw_place.get("opening_hours") or {}).get("open_now"),
        "photo_url": build_google_photo_url(photo_reference),
        "contact_phone": None,
        "primary_type": primary_type,
        "score": None,
    }


def _normalize_google_detail_result(raw_place: dict[str, Any]) -> dict[str, Any]:
    result = _normalize_google_search_result(raw_place, latitude=None, longitude=None)
    opening_hours = (raw_place.get("opening_hours") or {}).get("weekday_text") or []
    photos = [
        build_google_photo_url(photo.get("photo_reference"))
        for photo in (raw_place.get("photos") or [])
        if photo.get("photo_reference")
    ]

    result.update(
        {
            "contact_phone": raw_place.get("formatted_phone_number"),
            "description": raw_place.get("editorial_summary", {}).get("overview"),
            "review_count": raw_place.get("user_ratings_total"),
            "opening_hours": opening_hours,
            "images": [photo for photo in photos if photo],
        }
    )
    return result


def _search_google_places(query: str, latitude: float | None, longitude: float | None) -> list[dict[str, Any]]:
    if not settings.google_maps_api_key or not query.strip():
        return []

    params: dict[str, Any] = {
        "query": query.strip(),
        "key": settings.google_maps_api_key,
        "language": "vi",
    }
    if latitude is not None and longitude is not None:
        params["location"] = f"{latitude},{longitude}"
        params["radius"] = 5000

    response = httpx.get(TEXT_SEARCH_ENDPOINT, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    raw_results = payload.get("results") or []

    return [
        _normalize_google_search_result(
            raw_place,
            latitude=latitude,
            longitude=longitude,
        )
        for raw_place in raw_results
    ]


def _search_local_places(query: str, db: Session | None) -> list[dict[str, Any]]:
    if db is None:
        return []

    place_repo = PlaceRepository(db)
    return [
        {
            "id": place.id,
            "external_place_id": place.external_place_id,
            "name": place.name,
            "address": place.address,
            "rating": place.rating,
            "distance_km": None,
            "price_level": place.price_level,
            "open_now": place.open_now,
            "photo_url": place.photo_url,
            "contact_phone": place.contact_phone,
            "primary_type": place.primary_type,
            "score": None,
        }
        for place in place_repo.search_local_places(query)
    ]


def search_places(
    query: str = "",
    latitude: float | None = None,
    longitude: float | None = None,
    db: Session | None = None,
) -> list[dict[str, Any]]:
    """Search candidate places."""
    google_results: list[dict[str, Any]] = []
    try:
        google_results = _search_google_places(query=query, latitude=latitude, longitude=longitude)
    except Exception:
        google_results = []

    if google_results and db is not None:
        place_repo = PlaceRepository(db)
        normalized_results = []
        for item in google_results:
            external_place_id = item.get("external_place_id")
            if not external_place_id:
                continue
            place = place_repo.upsert_external_place(
                external_place_id=external_place_id,
                name=item["name"],
                address=item["address"],
                rating=item.get("rating"),
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
                price_level=item.get("price_level"),
                open_now=item.get("open_now"),
                photo_url=item.get("photo_url"),
                contact_phone=item.get("contact_phone"),
                primary_type=item.get("primary_type"),
            )
            enriched = dict(item)
            enriched["id"] = place.id
            normalized_results.append(enriched)
        if normalized_results:
            return normalized_results

    if google_results:
        for index, item in enumerate(google_results, start=1):
            item["id"] = index
        return google_results

    local_results = _search_local_places(query=query, db=db)
    if local_results:
        return local_results

    return [
        {
            "id": 1,
            "name": "Sample Place",
            "address": "123 Demo Street",
            "rating": 4.5,
            "distance_km": 1.2,
            "price_level": 2,
            "open_now": True,
            "photo_url": None,
            "contact_phone": None,
            "primary_type": "Restaurant",
            "score": None,
        }
    ]


def get_place_detail(external_place_id: str) -> dict[str, Any] | None:
    """Fetch detailed place data from Google Places Details API."""
    if not settings.google_maps_api_key or not external_place_id:
        return None

    try:
        response = httpx.get(
            PLACE_DETAILS_ENDPOINT,
            params={
                "place_id": external_place_id,
                "fields": ",".join(
                    [
                        "place_id",
                        "name",
                        "formatted_address",
                        "rating",
                        "user_ratings_total",
                        "formatted_phone_number",
                        "opening_hours",
                        "photos",
                        "types",
                        "geometry",
                        "price_level",
                        "editorial_summary",
                    ]
                ),
                "key": settings.google_maps_api_key,
                "language": "vi",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return None

    result = payload.get("result")
    if not result:
        return None
    return _normalize_google_detail_result(result)
