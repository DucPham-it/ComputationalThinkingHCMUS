"""Directions service wrapper.

Input:
- origin, destination, travel mode

Output:
- route summary and step-by-step navigation data
"""


def get_directions(origin: str, destination: str, travel_mode: str = "driving") -> dict:
    """Fetch route information.

    TODO:
    - call Google Directions API
    - parse polyline, total distance, duration, and route steps
    - support driving / walking / transit modes
    """
    return {
        "origin": origin,
        "destination": destination,
        "distance_text": "0 km",
        "duration_text": "0 mins",
        "polyline": "",
        "steps": [],
    }
