from fastapi import APIRouter

from app.services.weather_service import get_weather_summary

router = APIRouter()


@router.get("")
def get_weather(city: str = "") -> dict:
    """Return normalized weather data.

    Input:
    - city name or later latitude/longitude

    Output:
    - weather condition summary for recommendation layer or UI
    """
    return get_weather_summary(city=city)
