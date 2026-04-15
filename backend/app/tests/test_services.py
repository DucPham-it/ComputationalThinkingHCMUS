from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.services.directions_service import get_directions
from app.services.geocoding_service import geocode_address
from app.services.weather_service import get_weather_summary
from app.utils.distance import haversine_km


def test_security_helpers_roundtrip():
    password_hash = hash_password("secret12")
    assert verify_password("secret12", password_hash) is True
    assert verify_password("wrong", password_hash) is False

    token = create_access_token(1, "test@example.com")
    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["email"] == "test@example.com"


def test_distance_helper_returns_positive_distance():
    assert haversine_km(10.7769, 106.7009, 21.0278, 105.8342) > 1000


def test_external_services_fallback_without_required_inputs():
    assert geocode_address("") == {
        "formatted_address": "",
        "latitude": None,
        "longitude": None,
    }

    assert get_directions("", "").get("distance_text") == "0 km"
    assert get_weather_summary(city="").get("condition") == "unknown"
