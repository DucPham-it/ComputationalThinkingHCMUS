"""Geocoding service wrapper."""

from __future__ import annotations

import httpx

from app.core.config import settings

GEOCODING_ENDPOINT = "https://maps.googleapis.com/maps/api/geocode/json"
REQUEST_TIMEOUT_SECONDS = 10


def geocode_address(address: str) -> dict:
    """Convert text address to latitude/longitude."""
    normalized_address = address.strip()
    if not normalized_address or not settings.google_maps_api_key:
        return {
            "formatted_address": normalized_address,
            "latitude": None,
            "longitude": None,
        }

    try:
        response = httpx.get(
            GEOCODING_ENDPOINT,
            params={
                "address": normalized_address,
                "key": settings.google_maps_api_key,
                "language": "vi",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return {
            "formatted_address": normalized_address,
            "latitude": None,
            "longitude": None,
        }

    results = payload.get("results") or []
    if not results:
        return {
            "formatted_address": normalized_address,
            "latitude": None,
            "longitude": None,
        }

    best_match = results[0]
    location = best_match.get("geometry", {}).get("location", {})
    return {
        "formatted_address": best_match.get("formatted_address", normalized_address),
        "latitude": location.get("lat"),
        "longitude": location.get("lng"),
    }
