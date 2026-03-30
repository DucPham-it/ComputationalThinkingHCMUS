from dataclasses import dataclass


@dataclass
class Review:
    """User review entity.

    Input source:
    - internal database reviews table

    Output use:
    - returned in place detail page and review list endpoints
    """

    id: int
    user_id: int
    place_id: int
    content: str
    rating: int
