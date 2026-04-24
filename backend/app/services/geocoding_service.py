"""Geocoding helpers backed by database first, then OSM/Nominatim."""

from __future__ import annotations

import re
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.place_repo import PlaceRepository

GEOCODING_ENDPOINT = "/search"
REVERSE_GEOCODING_ENDPOINT = "/reverse"
REQUEST_TIMEOUT_SECONDS = 10

COORDINATE_PATTERN = re.compile(
    r"^\s*(?P<lat>-?\d+(?:\.\d+)?)\s*,\s*(?P<lng>-?\d+(?:\.\d+)?)\s*$"
)


def _coerce_coordinate(value: str) -> tuple[float, float] | None:
    match = COORDINATE_PATTERN.match(value)
    if not match:
        return None

    latitude = float(match.group("lat"))
    longitude = float(match.group("lng"))
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None
    return latitude, longitude


def _request_nominatim(path: str, *, params: dict[str, Any]) -> Any:
    response = httpx.get(
        f"{settings.nominatim_base_url.rstrip('/')}{path}",
        params={
            **params,
            "format": "jsonv2",
            "accept-language": "vi",
        },
        headers={"User-Agent": settings.external_maps_user_agent},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def _lookup_local_place(normalized_address: str, db: Session | None) -> dict | None:
    owns_session = db is None
    active_db = db or SessionLocal()
    try:
        place = PlaceRepository(active_db).get_by_name_or_address(normalized_address)
    finally:
        if owns_session:
            active_db.close()

    if place is None or place.latitude is None or place.longitude is None:
        return None

    return {
        "formatted_address": place.address,
        "latitude": place.latitude,
        "longitude": place.longitude,
    }


def geocode_address(address: str, *, db: Session | None = None) -> dict:
    normalized_address = address.strip()
    if not normalized_address:
        return {
            "formatted_address": "",
            "latitude": None,
            "longitude": None,
        }

    coordinates = _coerce_coordinate(normalized_address)
    if coordinates is not None:
        latitude, longitude = coordinates
        return {
            "formatted_address": normalized_address,
            "latitude": latitude,
            "longitude": longitude,
        }

    local_match = _lookup_local_place(normalized_address, db)
    if local_match is not None:
        return local_match

    try:
        results = _request_nominatim(
            GEOCODING_ENDPOINT,
            params={
                "q": normalized_address,
                "limit": 1,
                "addressdetails": 1,
            },
        )
    except Exception:
        return {
            "formatted_address": normalized_address,
            "latitude": None,
            "longitude": None,
        }

    if not results:
        return {
            "formatted_address": normalized_address,
            "latitude": None,
            "longitude": None,
        }

    best_match = results[0]
    return {
        "formatted_address": best_match.get("display_name", normalized_address),
        "latitude": float(best_match["lat"]) if best_match.get("lat") is not None else None,
        "longitude": float(best_match["lon"]) if best_match.get("lon") is not None else None,
    }


def reverse_geocode_coordinates(latitude: float, longitude: float) -> dict | None:
    try:
        payload = _request_nominatim(
            REVERSE_GEOCODING_ENDPOINT,
            params={
                "lat": latitude,
                "lon": longitude,
                "zoom": 18,
                "addressdetails": 1,
            },
        )
    except Exception:
        return None

    if not payload:
        return None

    display_name = payload.get("display_name") or f"{latitude},{longitude}"
    return {
        "name": payload.get("name") or display_name.split(",")[0].strip() or "Selected map point",
        "address": display_name,
        "latitude": float(payload.get("lat", latitude)),
        "longitude": float(payload.get("lon", longitude)),
        "source": "osm",
    }
