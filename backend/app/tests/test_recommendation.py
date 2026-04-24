"""Very small smoke tests for placeholder recommendation logic."""

from app.recommendation import recommender
from app.recommendation.recommender import recommend_places



def test_recommend_places_returns_list():
    items = recommend_places("quán ăn tối")
    assert isinstance(items, list)


def test_recommend_places_returns_top_10(monkeypatch):
    places = [
        {
            "id": index,
            "name": f"Place {index}",
            "address": "Test address",
            "external_place_id": None,
            "rating": 5,
            "review_count": 10,
            "latitude": None,
            "longitude": None,
            "distance_km": None,
            "price_level": None,
            "price_range": None,
            "open_now": None,
            "photo_url": None,
            "contact_phone": None,
            "primary_type": "restaurant",
        }
        for index in range(20)
    ]

    monkeypatch.setattr(recommender, "search_places", lambda **kwargs: places)

    items = recommend_places("restaurant", limit=10)

    assert len(items) == 10
