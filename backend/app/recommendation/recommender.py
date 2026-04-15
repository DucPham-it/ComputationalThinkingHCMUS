"""Top-level recommendation pipeline.

Pipeline idea:
1. receive user query and contextual input
2. parse NLP intent from free text
3. fetch candidate places from Google Places / local DB
4. filter by distance, type, open hours, budget
5. rank using rating, distance, weather, preferences, habits
6. return UI-ready recommendation list
"""

from typing import Any

from sqlalchemy.orm import Session

from app.recommendation.filters import apply_filters
from app.recommendation.nlp_parser import parse_search_text
from app.recommendation.ranking import rank_places
from app.services.google_places_service import search_places



def recommend_places(
    query: str = "",
    latitude: float | None = None,
    longitude: float | None = None,
    db: Session | None = None,
) -> list[dict[str, Any]]:
    """Generate recommendation list.

    Input:
    - query: free-text search from user

    Output:
    - ranked list of place dictionaries for frontend cards

    TODO:
    - accept structured filters from schema, not only free text
    - merge Google data with internal reviews/favorites/history
    - incorporate weather and special festival data
    """
    parsed = parse_search_text(query)
    places = search_places(query=query, latitude=latitude, longitude=longitude, db=db)
    filtered = apply_filters(
        places=places,
        allowed_types=[parsed["entertainment_type"]] if parsed.get("entertainment_type") else None,
    )
    ranked = rank_places(filtered)
    return ranked
