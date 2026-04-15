from math import asin, cos, radians, sin, sqrt


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
