"""Internal place model.

Represents place data merged from Google Maps Platform and local database.
"""

from dataclasses import dataclass


@dataclass
class Place:
    """Place entity.

    Minimum fields already defined.
    TODO later:
    - external_place_id
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
    rating: float | None = None
