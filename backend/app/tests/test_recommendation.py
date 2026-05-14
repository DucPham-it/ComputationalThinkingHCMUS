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
    assert RecommendationQuery().limit == 10
    assert RecommendationQuery().offset == 0


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


def test_recommend_places_supports_offset_pagination(monkeypatch):
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

    items = recommend_places("restaurant", limit=5, offset=5)

    assert [item["id"] for item in items] == [5, 6, 7, 8, 9]


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
    search_calls = []

    def fake_search_places(**kwargs):
        search_calls.append(kwargs)
        return [cafe_place, park_place]

    monkeypatch.setattr(recommender, "search_places", fake_search_places)

    items = recommend_places("cafe gan day", limit=10)

    assert len(search_calls) == 1
    assert search_calls[0]["query"] == "quan cafe"
    assert search_calls[0]["filters"]["allowed_types"] == ["cafe"]
    assert [item["id"] for item in items] == [1]


def test_recommend_places_uses_type_filter_as_database_candidate_query(monkeypatch):
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
        "price_level": None,
        "price_range": None,
        "open_now": None,
        "photo_url": None,
        "contact_phone": None,
        "primary_type": "cafe",
    }
    search_calls = []

    def fake_search_places(**kwargs):
        search_calls.append(kwargs)
        return [cafe_place] if kwargs["query"] == "cafe" else []

    monkeypatch.setattr(recommender, "search_places", fake_search_places)

    items = recommend_places(entertainment_type="cafe", limit=10)

    assert len(search_calls) == 1
    assert search_calls[0]["query"] == "cafe"
    assert search_calls[0]["filters"]["allowed_types"] == ["cafe"]
    assert [item["id"] for item in items] == [1]
