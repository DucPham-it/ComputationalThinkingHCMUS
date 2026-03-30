"""Shared map utilities.

Use cases:
- build photo URLs from Google photo references
- map Google place types into UI labels
- convert raw API payloads into internal fields
"""

GOOGLE_PLACE_TYPE_LABELS = {
    "clothing_store": "Clothing Store",
    "department_store": "Department Store",
    "establishment": "Establishment",
    "food": "Food",
    "movie_theater": "Movie Theater",
    "point_of_interest": "Point of Interest",
    "restaurant": "Restaurant",
    "shopping_mall": "Shopping Mall",
    "store": "Store",
}



def normalize_place_type(raw_type: str | None) -> str | None:
    """Map raw Google place type to display label.

    Input:
    - raw_type: Google place type string

    Output:
    - user-friendly label if known, else raw input
    """
    if raw_type is None:
        return None
    return GOOGLE_PLACE_TYPE_LABELS.get(raw_type, raw_type)
