"""Directions service wrapper."""

from __future__ import annotations

import httpx

from app.core.config import settings
from app.services.maps_helper import strip_html_tags

DIRECTIONS_ENDPOINT = "https://maps.googleapis.com/maps/api/directions/json"
REQUEST_TIMEOUT_SECONDS = 10


def get_directions(origin: str, destination: str, travel_mode: str = "driving") -> dict:
    """Fetch route information."""
    normalized_origin = origin.strip()
    normalized_destination = destination.strip()

    empty_result = {
        "origin": normalized_origin,
        "destination": normalized_destination,
        "distance_text": "0 km",
        "duration_text": "0 mins",
        "polyline": "",
        "steps": [],
    }

    if not normalized_origin or not normalized_destination or not settings.google_maps_api_key:
        return empty_result

    try:
        response = httpx.get(
            DIRECTIONS_ENDPOINT,
            params={
                "origin": normalized_origin,
                "destination": normalized_destination,
                "mode": travel_mode,
                "key": settings.google_maps_api_key,
                "language": "vi",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return empty_result

    routes = payload.get("routes") or []
    if not routes:
        return empty_result

    route = routes[0]
    leg = (route.get("legs") or [{}])[0]
    steps = []
    for step in leg.get("steps") or []:
        steps.append(
            {
                "instruction": strip_html_tags(step.get("html_instructions")),
                "distance_text": step.get("distance", {}).get("text"),
                "duration_text": step.get("duration", {}).get("text"),
            }
        )

    return {
        "origin": leg.get("start_address", normalized_origin),
        "destination": leg.get("end_address", normalized_destination),
        "distance_text": leg.get("distance", {}).get("text", "0 km"),
        "duration_text": leg.get("duration", {}).get("text", "0 mins"),
        "polyline": route.get("overview_polyline", {}).get("points"),
        "steps": steps,
    }
