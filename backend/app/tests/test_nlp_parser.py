from app.recommendation.nlp_parser import (
    parse_recommendation_language_contract,
    extract_filter_fields_from_text
)

def test_nlp_basic():
    query = "quan cafe re gan day cho cap doi tren 4 sao"
    result = parse_recommendation_language_contract(query)

    assert result["entertainment_type"] == "cafe"
    assert result["budget_level"] == "low"
    assert result["companion_type"] == "couple"
    assert result["distance_hint_km"] == 1
    assert result["min_rating"] == 4


def test_filter_extraction():
    query = "quan cafe gan day"
    result = extract_filter_fields_from_text(query)

    assert "max_distance_km" in result

if __name__ == "__main__":
    from app.recommendation.nlp_parser import (
        parse_recommendation_language_contract,
        extract_filter_fields_from_text
    )
    import json

    print("===== TEST NLP PARSER =====")

    queries = [
        "quan cafe gan day",
        "quan an re cho gia dinh",
        "cafe cho cap doi tren 4 sao",
        "noi di choi voi ban be toi nay",
        "quan an dang mo cua gan quan 1",
        "Quán ăn đắt cho cặp đôi trên 3 sao",
        "",
    ]

    for i, q in enumerate(queries, 1):
        print("\n" + "="*50)
        print(f"TEST {i}")
        print("="*50)

        print(f"Input: {q}")

        parsed = parse_recommendation_language_contract(q)
        print("\nParsed:")
        print(json.dumps(parsed, indent=4, ensure_ascii=False))

        filters = extract_filter_fields_from_text(q)
        print("\nFilters:")
        print(json.dumps(filters, indent=4, ensure_ascii=False))

        print("="*50)