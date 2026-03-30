"""NLP preprocessing helpers for free-text search.

Purpose:
- extract structured intent from Vietnamese or English user text
- detect category, budget, time, companion type, and destination hints

This file is a placeholder for later NLP work.
"""


def parse_search_text(query: str) -> dict:
    """Extract structured fields from free-text query.

    Input example:
    - "quán ăn tối rẻ gần tôi cho 2 người"

    Output example:
    - {
        "entertainment_type": "restaurant",
        "budget_level": "low",
        "companion_type": "couple",
        "time_slot": "evening"
      }

    TODO:
    - add keyword dictionaries
    - add language normalization
    - add synonym mapping for place categories
    """
    text = query.lower().strip()
    result = {
        "entertainment_type": None,
        "budget_level": None,
        "companion_type": None,
        "time_slot": None,
    }

    if any(word in text for word in ["ăn", "quán ăn", "restaurant", "food"]):
        result["entertainment_type"] = "restaurant"
    if any(word in text for word in ["rẻ", "cheap", "tiết kiệm"]):
        result["budget_level"] = "low"
    if any(word in text for word in ["2 người", "couple", "hẹn hò"]):
        result["companion_type"] = "couple"
    if any(word in text for word in ["tối", "evening", "dinner"]):
        result["time_slot"] = "evening"

    return result
