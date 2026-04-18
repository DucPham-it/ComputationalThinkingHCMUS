"""Google Places API wrapper."""

from __future__ import annotations

from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.place_repo import PlaceRepository
from app.repositories.temp_place_cache_repo import TemporaryPlaceCacheRepository
from app.services.directions_service import get_route_distance_km
from app.services.maps_helper import build_google_photo_url
from app.utils.distance import haversine_km

TEXT_SEARCH_ENDPOINT = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACE_DETAILS_ENDPOINT = "https://maps.googleapis.com/maps/api/place/details/json"
NEARBY_SEARCH_ENDPOINT = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
REVERSE_GEOCODING_ENDPOINT = "https://maps.googleapis.com/maps/api/geocode/json"
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
        "google_rating": raw_place.get("rating"),
        "google_review_count": raw_place.get("user_ratings_total"),
        "web_rating": None,
        "web_review_count": 0,
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
            "google_rating": raw_place.get("rating"),
            "google_review_count": raw_place.get("user_ratings_total"),
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


def _nearby_google_place(latitude: float, longitude: float) -> dict[str, Any] | None:
    if not settings.google_maps_api_key:
        return None

    try:
        response = httpx.get(
            NEARBY_SEARCH_ENDPOINT,
            params={
                "location": f"{latitude},{longitude}",
                "rankby": "distance",
                "key": settings.google_maps_api_key,
                "language": "vi",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return None

    results = payload.get("results") or []
    if not results:
        return None

    return _normalize_google_search_result(
        results[0],
        latitude=latitude,
        longitude=longitude,
    )


def _reverse_geocode_coordinates(latitude: float, longitude: float) -> dict[str, Any] | None:
    if not settings.google_maps_api_key:
        return None

    try:
        response = httpx.get(
            REVERSE_GEOCODING_ENDPOINT,
            params={
                "latlng": f"{latitude},{longitude}",
                "key": settings.google_maps_api_key,
                "language": "vi",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return None

    results = payload.get("results") or []
    if not results:
        return None

    best_match = results[0]
    formatted_address = best_match.get("formatted_address") or f"{latitude},{longitude}"
    name = formatted_address.split(",")[0].strip() or formatted_address
    return {
        "external_place_id": None,
        "name": name,
        "address": formatted_address,
        "rating": None,
        "google_rating": None,
        "google_review_count": None,
        "web_rating": None,
        "web_review_count": 0,
        "latitude": latitude,
        "longitude": longitude,
        "distance_km": 0.0,
        "price_level": None,
        "open_now": None,
        "photo_url": None,
        "contact_phone": None,
        "primary_type": "point_of_interest",
        "score": None,
    }


def _persist_place_candidate(
    item: dict[str, Any],
    *,
    db: Session | None,
) -> dict[str, Any]:
    if db is None:
        return item

    place_repo = PlaceRepository(db)
    cache_repo = TemporaryPlaceCacheRepository(db)

    if item.get("external_place_id"):
        place = place_repo.upsert_external_place(
            external_place_id=item["external_place_id"],
            name=item["name"],
            address=item["address"],
            rating=item.get("google_rating") or item.get("rating"),
            latitude=item.get("latitude"),
            longitude=item.get("longitude"),
            price_level=item.get("price_level"),
            open_now=item.get("open_now"),
            photo_url=item.get("photo_url"),
            contact_phone=item.get("contact_phone"),
            primary_type=item.get("primary_type"),
        )
    else:
        place = place_repo.create_local_place(
            name=item["name"],
            address=item["address"],
            rating=item.get("google_rating") or item.get("rating"),
            latitude=item.get("latitude"),
            longitude=item.get("longitude"),
            price_level=item.get("price_level"),
            open_now=item.get("open_now"),
            photo_url=item.get("photo_url"),
            contact_phone=item.get("contact_phone"),
            primary_type=item.get("primary_type"),
        )

    cache_repo.upsert_cached_place(
        place_id=place.id,
        external_place_id=place.external_place_id,
        name=place.name,
        address=place.address,
        rating=place.rating,
        latitude=place.latitude,
        longitude=place.longitude,
        price_level=place.price_level,
        open_now=place.open_now,
        photo_url=place.photo_url,
        contact_phone=place.contact_phone,
        primary_type=place.primary_type,
        ttl_minutes=settings.temporary_place_cache_ttl_minutes,
    )

    normalized_item = dict(item)
    normalized_item["id"] = place.id
    return normalized_item


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
            "google_rating": place.rating,
            "google_review_count": None,
            "web_rating": None,
            "web_review_count": 0,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "distance_km": None,
            "review_count": 0,
            "price_level": place.price_level,
            "open_now": place.open_now,
            "photo_url": place.photo_url,
            "contact_phone": place.contact_phone,
            "primary_type": place.primary_type,
            "score": None,
        }
        for place in place_repo.search_local_places(query)
    ]


def _dedupe_places(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []

    for item in items:
        key = (
            f"external:{item.get('external_place_id')}"
            if item.get("external_place_id")
            else f"id:{item.get('id')}"
            if item.get("id") is not None
            else f"text:{(item.get('name') or '').strip().lower()}|{(item.get('address') or '').strip().lower()}"
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped


def _sort_places(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            item.get("distance_km") is None,
            item.get("distance_km") or 0,
            -(item.get("rating") or 0),
            str(item.get("name") or ""),
        ),
    )


def _apply_route_distances(
    items: list[dict[str, Any]],
    *,
    latitude: float | None,
    longitude: float | None,
) -> list[dict[str, Any]]:
    if latitude is None or longitude is None:
        return items

    candidate_limit = max(0, int(settings.route_distance_candidate_limit))
    if candidate_limit == 0:
        return items

    enriched_items: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        enriched_item = dict(item)
        if index < candidate_limit:
            route_distance_km = get_route_distance_km(
                latitude,
                longitude,
                enriched_item.get("latitude"),
                enriched_item.get("longitude"),
                travel_mode="driving",
            )
            if route_distance_km is not None:
                enriched_item["distance_km"] = route_distance_km
        enriched_items.append(enriched_item)
    return enriched_items


def search_places(
    query: str = "",
    latitude: float | None = None,
    longitude: float | None = None,
    db: Session | None = None,
) -> list[dict[str, Any]]:
    """Search candidate places."""
    google_results: list[dict[str, Any]] = []
    normalized_google_results: list[dict[str, Any]] = []
    cached_results: list[dict[str, Any]] = []
    cache_repo: TemporaryPlaceCacheRepository | None = None

    if db is not None:
        cache_repo = TemporaryPlaceCacheRepository(db)
        cache_repo.cleanup_expired()
        cached_results = cache_repo.search_active_places(query=query, limit=24)

    try:
        google_results = _search_google_places(query=query, latitude=latitude, longitude=longitude)
    except Exception:
        google_results = []

    if google_results and db is not None:
        place_repo = PlaceRepository(db)
        normalized_results: list[dict[str, Any]] = []
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
            if cache_repo is not None:
                cache_repo.upsert_cached_place(
                    place_id=place.id,
                    external_place_id=place.external_place_id,
                    name=place.name,
                    address=place.address,
                    rating=place.rating,
                    latitude=place.latitude,
                    longitude=place.longitude,
                    price_level=place.price_level,
                    open_now=place.open_now,
                    photo_url=place.photo_url,
                    contact_phone=place.contact_phone,
                    primary_type=place.primary_type,
                    ttl_minutes=settings.temporary_place_cache_ttl_minutes,
                )
        normalized_google_results = normalized_results

    if google_results and not normalized_google_results:
        for index, item in enumerate(google_results, start=1):
            item["id"] = index
        normalized_google_results = google_results

    local_results = _search_local_places(query=query, db=db)
    for item in local_results:
        item["distance_km"] = _extract_distance_km(
            latitude,
            longitude,
            item.get("latitude"),
            item.get("longitude"),
        )

    fallback_local_results = _search_local_places(query="", db=db)
    for item in fallback_local_results:
        item["distance_km"] = _extract_distance_km(
            latitude,
            longitude,
            item.get("latitude"),
            item.get("longitude"),
        )

    merged_results = _dedupe_places(normalized_google_results + local_results + cached_results)
    if len(merged_results) < 10:
        merged_results = _dedupe_places(merged_results + fallback_local_results)

    if merged_results:
        sorted_results = _sort_places(merged_results)[:24]
        return _apply_route_distances(
            sorted_results,
            latitude=latitude,
            longitude=longitude,
        )

    return [
        {
            "id": 1,
            "name": "Sample Place",
            "address": "123 Demo Street",
            "rating": 4.5,
            "review_count": 0,
            "distance_km": 1.2,
            "latitude": 10.7769,
            "longitude": 106.7009,
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


def resolve_place_from_coordinates(
    latitude: float,
    longitude: float,
    *,
    db: Session | None = None,
) -> dict[str, Any] | None:
    nearby_place = _nearby_google_place(latitude, longitude)
    if nearby_place is not None:
        return _persist_place_candidate(nearby_place, db=db)

    reverse_geocoded_place = _reverse_geocode_coordinates(latitude, longitude)
    if reverse_geocoded_place is not None:
        return _persist_place_candidate(reverse_geocoded_place, db=db)

    return None
