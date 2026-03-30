import requests
from config.settings import GOOGLE_MAPS_API_KEY

BASE_URL = "https://maps.googleapis.com/maps/api/directions/json"


def get_directions(origin: str, destination: str, mode: str = "driving"):
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "key": GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    routes = data.get("routes", [])

    if not routes:
        return None

    leg = routes[0]["legs"][0]

    return {
        "distance": leg["distance"]["text"],
        "duration": leg["duration"]["text"],
        "start_address": leg["start_address"],
        "end_address": leg["end_address"],
        "steps": [
            step["html_instructions"] for step in leg.get("steps", [])
        ],
        "polyline": routes[0]["overview_polyline"]["points"],
    }