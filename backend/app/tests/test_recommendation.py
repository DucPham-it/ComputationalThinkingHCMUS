"""Very small smoke tests for placeholder recommendation logic."""

from app.recommendation.recommender import recommend_places



def test_recommend_places_returns_list():
    items = recommend_places("quán ăn tối")
    assert isinstance(items, list)
