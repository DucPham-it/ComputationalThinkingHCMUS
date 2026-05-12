from math import asin, cos, radians, sin, sqrt
from typing import Any


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance in kilometers."""
    earth_radius_km = 6371.0

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    )
    c = 2 * asin(sqrt(a))
    return earth_radius_km * c


def get_distance_between_points(user_location: dict[str, Any], place_location: dict[str, Any]) -> float | None:
    """Compute distance between two location dictionaries.

    Input:
    - user_location: dict with latitude/longitude or lat/lng.
    - place_location: dict with latitude/longitude or lat/lng.

    Output:
    - distance in kilometers.
    - None when either point is missing or not numeric.
    """

    def read_coordinate(payload: dict[str, Any], primary: str, fallback: str) -> float | None:
        value = payload.get(primary)
        if value is None:
            value = payload.get(fallback)

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    lat1 = read_coordinate(user_location, "latitude", "lat")
    lon1 = read_coordinate(user_location, "longitude", "lng")
    lat2 = read_coordinate(place_location, "latitude", "lat")
    lon2 = read_coordinate(place_location, "longitude", "lng")

    if None in (lat1, lon1, lat2, lon2):
        return None

    return haversine_km(lat1, lon1, lat2, lon2)
