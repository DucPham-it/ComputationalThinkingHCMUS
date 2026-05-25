"""Route planning with database/coordinate resolution and OSRM routing."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.services.geocoding_service import geocode_address
from app.utils.distance import haversine_km

REQUEST_TIMEOUT_SECONDS = 12

OSRM_PROFILE_BY_MODE = {
    "driving": "driving",
    "walking": "foot",
    "bicycling": "bike",
    "transit": "driving",
}

AVERAGE_SPEED_KMH_BY_MODE = {
    "driving": 28.0,
    "walking": 4.8,
    "bicycling": 14.0,
    "transit": 22.0,
}


def _format_distance(distance_km: float) -> str:
    if distance_km < 1:
        return f"{int(round(distance_km * 1000))} m"
    if distance_km >= 100:
        return f"{distance_km:.0f} km"
    return f"{distance_km:.1f} km"


def _format_duration(duration_seconds: int) -> str:
    minutes = max(1, int(round(duration_seconds / 60)))
    if minutes < 60:
        return f"{minutes} mins"

    hours, remaining_minutes = divmod(minutes, 60)
    if remaining_minutes == 0:
        return f"{hours} hr"
    return f"{hours} hr {remaining_minutes} mins"


def _resolve_location(raw_value: str, *, db) -> dict[str, Any] | None:
    normalized_value = raw_value.strip()
    if not normalized_value:
        return None

    geocoded = geocode_address(normalized_value, db=db)
    latitude = geocoded.get("latitude")
    longitude = geocoded.get("longitude")
    if latitude is None or longitude is None:
        return None

    return {
        "name": geocoded.get("formatted_address") or normalized_value,
        "latitude": float(latitude),
        "longitude": float(longitude),
    }


def _build_fallback_route(
    *,
    origin: dict[str, Any],
    destination: dict[str, Any],
    travel_mode: str,
) -> dict[str, Any]:
    distance_km = haversine_km(
        origin["latitude"],
        origin["longitude"],
        destination["latitude"],
        destination["longitude"],
    )
    speed_kmh = AVERAGE_SPEED_KMH_BY_MODE.get(
        (travel_mode or "driving").strip().lower(),
        AVERAGE_SPEED_KMH_BY_MODE["driving"],
    )
    duration_seconds = max(60, int(round((distance_km / speed_kmh) * 3600)))
    return {
        "origin": origin["name"],
        "destination": destination["name"],
        "distance_text": _format_distance(distance_km),
        "distance_km": round(distance_km, 2),
        "duration_text": _format_duration(duration_seconds),
        "duration_seconds": duration_seconds,
        "path": [
            {"latitude": round(origin["latitude"], 6), "longitude": round(origin["longitude"], 6)},
            {"latitude": round(destination["latitude"], 6), "longitude": round(destination["longitude"], 6)},
        ],
        "steps": [
            {
                "instruction": f"Go to {destination['name']}",
                "distance_text": _format_distance(distance_km),
                "duration_text": _format_duration(duration_seconds),
                "geometry": [
                    [
                        round(origin["longitude"], 6),
                        round(origin["latitude"], 6),
                    ],
                    [
                        round(destination["longitude"], 6),
                        round(destination["latitude"], 6),
                    ],
                ],

                "maneuver_type": "depart",

                "maneuver_modifier": None,

                "maneuver_location": [
                    round(origin["longitude"], 6),
                    round(origin["latitude"], 6),
                ],
                    
                "distance_meters": round(distance_km * 1000, 2),

                "duration_seconds": duration_seconds,
            }
        ],
    }


def _normalize_step(step: dict[str, Any]) -> str:
    maneuver = step.get("maneuver") or {}
    instruction = maneuver.get("instruction")
    if instruction:
        return instruction

    maneuver_type = maneuver.get("type") or "continue"
    modifier = maneuver.get("modifier")
    name = step.get("name")
    parts = [str(maneuver_type).replace("_", " ").capitalize()]
    if modifier:
        parts.append(str(modifier).replace("_", " "))
    if name:
        parts.append(f"onto {name}")
    return " ".join(parts)


def plan_route(
    *,
    origin_text: str,
    destination_text: str,
    travel_mode: str = "driving",
    db=None,
) -> dict[str, Any] | None:
    origin = _resolve_location(origin_text, db=db)
    destination = _resolve_location(destination_text, db=db)
    if origin is None or destination is None:
        return None

    normalized_mode = (travel_mode or "driving").strip().lower()
    profile = OSRM_PROFILE_BY_MODE.get(normalized_mode, "driving")
    base_url = settings.osrm_base_url.rstrip("/")
    coordinates = (
        f"{origin['longitude']},{origin['latitude']};"
        f"{destination['longitude']},{destination['latitude']}"
    )

    try:
        response = httpx.get(
            f"{base_url}/route/v1/{profile}/{coordinates}",
            params={
                "overview": "full",
                "geometries": "geojson",
                "steps": "true",
            },
            headers={"User-Agent": settings.external_maps_user_agent},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return _build_fallback_route(
            origin=origin,
            destination=destination,
            travel_mode=normalized_mode,
        )

    routes = payload.get("routes") or []
    if not routes:
        return _build_fallback_route(
            origin=origin,
            destination=destination,
            travel_mode=normalized_mode,
        )

    route = routes[0]
    legs = route.get("legs") or []
    geometry = route.get("geometry", {})
    coordinates_list = geometry.get("coordinates") or []
    path = [
        {
            "latitude": round(float(item[1]), 6),
            "longitude": round(float(item[0]), 6),
        }
        for item in coordinates_list
        if isinstance(item, list) and len(item) >= 2
    ]

    total_distance_km = round(float(route.get("distance", 0.0)) / 1000, 2)
    total_duration_seconds = int(round(float(route.get("duration", 0.0))))

    steps: list[dict[str, Any]] = []
    for leg in legs:
        for step in leg.get("steps") or []:
            step_distance_meters = float(step.get("distance", 0.0))
            step_distance_km = float(step.get("distance", 0.0)) / 1000
            step_duration_seconds = int(round(float(step.get("duration", 0.0))))
            maneuver = step.get("maneuver") or {}
            step_geometry = (
                step.get("geometry", {}).get("coordinates")
                if isinstance(step.get("geometry"), dict)
                else []
            )
            normalized_geometry = [
                [float(point[0]), float(point[1])]
                for point in step_geometry
                if isinstance(point, list) and len(point) >= 2
            ]
            maneuver_location = maneuver.get("location") or []

            steps.append(
                {
                    "instruction": _normalize_step(step),
                    "distance_text": _format_distance(step_distance_km),
                    "duration_text": _format_duration(step_duration_seconds),
                    "geometry": normalized_geometry,
                    "maneuver_type": maneuver.get("type"),
                    "maneuver_modifier": maneuver.get("modifier"),
                    "maneuver_location": (
                        [
                            float(maneuver_location[0]),
                            float(maneuver_location[1]),
                        ]
                        if len(maneuver_location) >= 2
                     else None
                    ),
                    "distance_meters": round(step_distance_meters, 2),
                    "duration_seconds": step_duration_seconds,
                }
            )

    if not path:
        path = [
            {"latitude": round(origin["latitude"], 6), "longitude": round(origin["longitude"], 6)},
            {"latitude": round(destination["latitude"], 6), "longitude": round(destination["longitude"], 6)},
        ]

    if not steps:
        steps = [
            {
                "instruction": f"Go to {destination['name']}",
                "distance_text": _format_distance(total_distance_km),
                "duration_text": _format_duration(total_duration_seconds),
                "geometry": [
                    [round(origin["longitude"], 6), round(origin["latitude"], 6)],
                    [round(destination["longitude"], 6), round(destination["latitude"], 6)],
                ],
                "maneuver_type": "depart",
                "maneuver_modifier": None,
                "maneuver_location": [
                    round(origin["longitude"], 6),
                    round(origin["latitude"], 6),
                ],
                "distance_meters": round(total_distance_km * 1000, 2),
                "duration_seconds": total_duration_seconds,
            }
        ]

    return {
        "origin": origin["name"],
        "destination": destination["name"],
        "distance_text": _format_distance(total_distance_km),
        "distance_km": total_distance_km,
        "duration_text": _format_duration(total_duration_seconds),
        "duration_seconds": total_duration_seconds,
        "path": path,
        "steps": steps,
    }
