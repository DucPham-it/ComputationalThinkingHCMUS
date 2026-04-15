"""Internal place model.

Represents place data merged from Google Maps Platform and local database.
"""

from dataclasses import dataclass


@dataclass
class Place:
    """Place entity.

    Minimum fields already defined.
    TODO later:
    - latitude, longitude
    - price_level
    - open_now
    - photo_url
    - contact_phone
    - types
    - source labels (google/local)
    """

    id: int
    name: str
    address: str
    external_place_id: str | None = None
    rating: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    price_level: int | None = None
    open_now: bool | None = None
    photo_url: str | None = None
    contact_phone: str | None = None
    primary_type: str | None = None
