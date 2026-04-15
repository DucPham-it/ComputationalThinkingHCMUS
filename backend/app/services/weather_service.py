"""Weather service wrapper."""

from __future__ import annotations

import httpx

from app.services.geocoding_service import geocode_address

OPEN_METEO_ENDPOINT = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 10

WMO_CONDITIONS = {
    0: "clear",
    1: "mainly_clear",
    2: "partly_cloudy",
    3: "cloudy",
    45: "fog",
    48: "fog",
    51: "drizzle",
    53: "drizzle",
    55: "drizzle",
    56: "freezing_drizzle",
    57: "freezing_drizzle",
    61: "rain",
    63: "rain",
    65: "rain",
    66: "freezing_rain",
    67: "freezing_rain",
    71: "snow",
    73: "snow",
    75: "snow",
    77: "snow",
    80: "rain_showers",
    81: "rain_showers",
    82: "rain_showers",
    85: "snow_showers",
    86: "snow_showers",
    95: "storm",
    96: "storm",
    99: "storm",
}


def get_weather_summary(city: str = "", latitude: float | None = None, longitude: float | None = None) -> dict:
    """Get weather summary."""
    resolved_city = city.strip()
    resolved_latitude = latitude
    resolved_longitude = longitude

    if (resolved_latitude is None or resolved_longitude is None) and resolved_city:
        geocoded = geocode_address(resolved_city)
        resolved_city = geocoded.get("formatted_address") or resolved_city
        resolved_latitude = geocoded.get("latitude")
        resolved_longitude = geocoded.get("longitude")

    if resolved_latitude is None or resolved_longitude is None:
        return {
            "city": resolved_city,
            "condition": "unknown",
            "temperature_c": None,
            "rain_probability": None,
        }

    try:
        response = httpx.get(
            OPEN_METEO_ENDPOINT,
            params={
                "latitude": resolved_latitude,
                "longitude": resolved_longitude,
                "current": "temperature_2m,weather_code",
                "hourly": "precipitation_probability",
                "forecast_days": 1,
                "timezone": "auto",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return {
            "city": resolved_city,
            "condition": "unknown",
            "temperature_c": None,
            "rain_probability": None,
        }

    current = payload.get("current") or {}
    hourly = payload.get("hourly") or {}
    precipitation_probabilities = hourly.get("precipitation_probability") or []

    weather_code = current.get("weather_code")
    return {
        "city": resolved_city,
        "condition": WMO_CONDITIONS.get(weather_code, "unknown"),
        "temperature_c": current.get("temperature_2m"),
        "rain_probability": precipitation_probabilities[0] if precipitation_probabilities else None,
    }
