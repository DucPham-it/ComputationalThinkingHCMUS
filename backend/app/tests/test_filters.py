from app.recommendation.filters import apply_filters, build_filter_plan
from app.utils.distance import get_distance_between_points


def test_build_filter_plan_normalizes_budget_and_prefers_ui():
    plan = build_filter_plan(
        {"budget_level": "cheap", "max_distance_km": 10},
        {"budget_level": "premium"},
    )

    assert plan["budget_level"] == "high"
    assert plan["max_distance_km"] == 10
    assert plan["source_map"]["budget_level"] == "ui"


def test_apply_filters_keeps_existing_recommender_contract():
    places = [
        {"id": 1, "primary_type": "cafe", "rating": 4.5, "price_level": 1, "distance_km": 1.2},
        {"id": 2, "primary_type": "park", "rating": 4.8, "price_level": 4, "distance_km": 1.0},
        {"id": 3, "primary_type": "cafe", "rating": 3.0, "price_level": 1, "distance_km": 0.8},
    ]

    filtered = apply_filters(
        places,
        max_distance_km=2,
        allowed_types=["cafe"],
        min_rating=4,
        budget_level="cheap",
    )

    assert [place["id"] for place in filtered] == [1]


def test_distance_helper_accepts_frontend_and_backend_coordinate_names():
    distance = get_distance_between_points(
        {"lat": 10.7769, "lng": 106.7009},
        {"latitude": 10.7779, "longitude": 106.7019},
    )

    assert distance is not None
    assert distance > 0
