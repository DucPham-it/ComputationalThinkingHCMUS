from app.recommendation.nlp_parser import (
    extract_filter_fields_from_text,
    parse_recommendation_language_contract,
)


def test_nlp_contract_extracts_recommendation_fields():
    result = parse_recommendation_language_contract(
        "quan cafe re gan day cho cap doi tren 4 sao dang mo cua"
    )

    assert result["entertainment_type"] == "cafe"
    assert result["budget_level"] == "low"
    assert result["companion_type"] == "couple"
    assert result["distance_hint_km"] == 3.0
    assert result["min_rating"] == 4.0
    assert result["require_open_now"] is True


def test_extract_filter_fields_returns_backend_filter_keys():
    result = extract_filter_fields_from_text("tim rap phim trong 5km tren 4.5 sao")

    assert result == {
        "max_distance_km": 5.0,
        "min_rating": 4.5,
        "preferred_types": ["movie_theater"],
    }
