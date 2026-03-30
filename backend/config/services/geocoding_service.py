import requests
from config.settings import GOOGLE_MAPS_API_KEY

BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def geocode_address(address: str):
    params = {
        "address": address,
        "key": GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    status = data.get("status")
    results = data.get("results", [])

    if status != "OK" or not results:
        print("Geocoding API error:", data)
        return None

    location = results[0]["geometry"]["location"]

    return {
        "lat": location["lat"],
        "lng": location["lng"],
        "formatted_address": results[0]["formatted_address"],
    }