"""Very small smoke tests for placeholder recommendation logic."""

from inspect import signature

from app.api.routes.recommendations import get_recommendations
from app.recommendation import recommender
from app.recommendation.recommender import recommend_places
from app.schemas.place_schema import RecommendationQuery



def test_recommend_places_returns_list():
    items = recommend_places("quán ăn tối")
    assert isinstance(items, list)


def test_recommendation_distance_defaults_to_unbounded():
    assert signature(get_recommendations).parameters["max_distance_km"].default is None
    assert RecommendationQuery().max_distance_km is None


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


def test_recommend_places_broadens_database_candidates_for_text_filters(monkeypatch):
    cafe_place = {
        "id": 1,
        "name": "Quiet Coffee",
        "address": "Test address",
        "external_place_id": None,
        "rating": 4.8,
        "review_count": 12,
        "latitude": None,
        "longitude": None,
        "distance_km": None,
        "price_level": 1,
        "price_range": None,
        "open_now": None,
        "photo_url": None,
        "contact_phone": None,
        "primary_type": "cafe",
    }
    park_place = {
        **cafe_place,
        "id": 2,
        "name": "Green Park",
        "primary_type": "park",
    }
    search_queries = []

    def fake_search_places(**kwargs):
        search_queries.append(kwargs["query"])
        if kwargs["query"]:
            return []
        return [cafe_place, park_place]

    monkeypatch.setattr(recommender, "search_places", fake_search_places)

    items = recommend_places("cafe gan day", limit=10)

    assert search_queries == ["quan cafe", ""]
    assert [item["id"] for item in items] == [1]
