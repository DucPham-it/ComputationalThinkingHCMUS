from dataclasses import dataclass


@dataclass
class Route:
    """Route summary entity.

    Stores condensed route information from the backend route planner.
    """

    origin: str
    destination: str
    distance_text: str
    duration_text: str
