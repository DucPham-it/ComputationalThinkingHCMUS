from app.recommendation.nlp_parser import (
    parse_recommendation_language_contract,
    extract_filter_fields_from_text
)


def test_nlp_contract_extracts_recommendation_fields():
    result = parse_recommendation_language_contract(
        "quan cafe re gan day cho cap doi tren 4 sao dang mo cua"
    )

    assert result["entertainment_type"] == "cafe"
    assert result["budget_level"] == "low"
    assert result["companion_type"] == "couple"
    assert result["distance_hint_km"] == 1
    assert result["min_rating"] == 4.0
    assert result["require_open_now"] is True


def test_nlp_basic():
    query = "quan cafe re gan day cho cap doi tren 4 sao"
    result = parse_recommendation_language_contract(query)

    assert result["entertainment_type"] == "cafe"
    assert result["budget_level"] == "low"
    assert result["companion_type"] == "couple"
    assert result["distance_hint_km"] == 1
    assert result["min_rating"] == 4


def test_extract_filter_fields_returns_backend_filter_keys():
    result = extract_filter_fields_from_text("tim rap phim trong 5km tren 4.5 sao")

    assert result == {
        "max_distance_km": 5.0,
        "min_rating": 4.5,
        "preferred_types": ["movie_theater"],
    }


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
        #case 1: Basic
    "quan cafe gan day",
    "quan an re",
    "cafe cho cap doi",
    "noi di choi voi ban be",
    "quan an cho gia dinh",

    #Case 2:BUDGET
    "quan an re",
    "quan an gia re",
    "quan an binh dan",
    "quan an tiet kiem",

    "quan an vua tui tien",
    "quan an tam trung",
    "quan an ok",

    "quan an dat",
    "quan an mac",
    "quan an cao cap",
    "quan an sang trong",

    #Case 3:COMPANION
    "di mot minh",
    "di voi nguoi yeu",
    "di voi cap doi",
    "di voi gia dinh",
    "di voi tre em",
    "di voi ban be",
    "di voi team",
    "di voi group",

    #Case 4:Time
    "di sang nay",
    "di buoi sang",
    "di buoi chieu",
    "di toi nay",
    "di ban dem",
    "di overnight",

    #Case 5.1: DISTANCE
    "quan cafe gan day",
    "quan cafe gan",
    "quan cafe trong 5km",
    "quan cafe 3km",

    #Case 5.2:
    "quan cafe xa",
    "quan cafe xa qua",
    "quan cafe o xa",

    "quan cafe xa tren 10km",
    "quan cafe tren 10km",
    "quan cafe hon 10km",
    "quan cafe duoi 5km",

    "quan cafe khoang 7km",
    "quan cafe tam 3km",

    #Case 5.3:
    "quan cafe rat xa",
    "quan cafe gan xiu",
    "quan cafe xa vai",
    "quan cafe xa lam",

    #Case 6: RATING
    "quan cafe tren 4 sao",
    "quan cafe 4 sao",
    "quan cafe 4.5 sao",
    "quan cafe >= 4 sao",
    #Case 7 :OPEN NOW
    "quan an dang mo cua",
    "quan an con mo",
    "quan an open now",
    "quan an available",

    #Case 8:LOCATION
    "quan cafe gan quan 1",
    "quan an o quan 5",
    "quan cafe district 7",
    "quan cafe gan district 1",

    #Case 9:COMBO CASE
    "quan cafe re gan day cho cap doi",
    "quan an dat cho gia dinh tren 4 sao",
    "cafe cho ban be toi nay gan day",
    "quan an dang mo cua gan quan 1",
    "quan cafe cao cap cho nguoi yeu toi nay",

    #Case 10.1:EDGE CASE
    "",
    "   ",
    #Case 10.2 : Không rõ nghĩa
    "toi muon di choi",
    "cho toi mot noi",
    "tim gi do vui vui",

    #Case 10.3:dễ bug substring
    "quan cafe tron ven",
    "quan cafe ton tai",
    "quan cafe on dinh",

    #Case 10.4: English
    "cheap cafe near me",
    "restaurant for couple",
    "premium restaurant tonight",
    "family friendly cafe",

    "Case 10.5:mixed language",
    "cafe cheap gan day",
    "restaurant cho cap doi tonight",
    "quan an premium cho gia dinh",

    #Case 11: CASE “TRAP”
    "quan cafe khong can re",
    "quan cafe khong can dat",
    "quan an khong gan",
    "quan cafe khong xa",

    #Case 12: input ngắn
    "uh",
    "ờ",
    "à",
    "gì đó",
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
