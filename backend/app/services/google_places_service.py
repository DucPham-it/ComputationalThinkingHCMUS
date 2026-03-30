"""Google Places API wrapper.

Input:
- query text, location, radius, place types, budget or ranking preferences

Output:
- normalized place dictionaries usable by recommendation layer

TODO:
- call Google Places API / Nearby Search / Text Search / Place Details
- normalize data into internal format
- map Google fields to frontend-friendly fields
"""

from typing import Any



def search_places(query: str = "", latitude: float | None = None, longitude: float | None = None) -> list[dict[str, Any]]:
    """Search candidate places.

    Input:
    - query: free-text user intent
    - latitude/longitude: optional user location for nearby search

    Output:
    - list of normalized place dictionaries

    Expected normalized fields later:
    - id
    - name
    - address
    - rating
    - lat/lng
    - primary_type
    - price_level
    - open_now
    - photo_url
    - contact_phone
    """
    # TODO: replace placeholder with real Google Places requests.
    return [
        {
            "id": 1,
            "name": "Sample Place",
            "address": "123 Demo Street",
            "rating": 4.5,
            "distance_km": 1.2,
            "price_level": 2,
            "open_now": True,
            "primary_type": "restaurant",
            "score": None,
        }
    ]
