import requests
from config.settings import GOOGLE_MAPS_API_KEY

BASE_URL = "https://maps.googleapis.com/maps/api/place"


def nearby_search(lat: float, lng: float, radius: int = 1500, place_type: str | None = None):
    url = f"{BASE_URL}/nearbysearch/json"

    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "key": GOOGLE_MAPS_API_KEY,
    }

    if place_type:
        params["type"] = place_type

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    return data.get("results", [])


def text_search(query: str):
    url = f"{BASE_URL}/textsearch/json"

    params = {
        "query": query,
        "key": GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    return data.get("results", [])


def get_place_details(place_id: str):
    url = f"{BASE_URL}/details/json"

    params = {
        "place_id": place_id,
        "fields": ",".join([
            "place_id",
            "name",
            "formatted_address",
            "geometry",
            "rating",
            "user_ratings_total",
            "price_level",
            "types",
            "formatted_phone_number",
            "website",
            "opening_hours",
            "reviews",
            "editorial_summary",
        ]),
        "key": GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    return data.get("result", {})


def normalize_place(place: dict):
    return {
        "google_place_id": place.get("place_id"),
        "name": place.get("name"),
        "address": place.get("formatted_address") or place.get("vicinity"),
        "lat": place.get("geometry", {}).get("location", {}).get("lat"),
        "lng": place.get("geometry", {}).get("location", {}).get("lng"),
        "rating": place.get("rating"),
        "total_ratings": place.get("user_ratings_total"),
        "price_level": place.get("price_level"),
        "types": place.get("types", []),
        "open_now": place.get("opening_hours", {}).get("open_now"),
    }