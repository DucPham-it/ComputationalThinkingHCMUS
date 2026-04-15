"""Shared map utilities.

Use cases:
- build photo URLs from Google photo references
- map Google place types into UI labels
- convert raw API payloads into internal fields
"""

from __future__ import annotations

from html import unescape
import re

from app.core.config import settings

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


def build_google_photo_url(photo_reference: str | None, max_width: int = 800) -> str | None:
    """Build a Google Places photo URL from a photo reference."""
    if not photo_reference or not settings.google_maps_api_key:
        return None

    return (
        "https://maps.googleapis.com/maps/api/place/photo"
        f"?maxwidth={max_width}"
        f"&photo_reference={photo_reference}"
        f"&key={settings.google_maps_api_key}"
    )


def strip_html_tags(value: str | None) -> str:
    """Remove simple HTML markup from Google directions instructions."""
    if not value:
        return ""
    return unescape(re.sub(r"<[^>]+>", "", value)).strip()
