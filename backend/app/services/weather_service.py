"""Weather service wrapper.

Input:
- coordinates or city name

Output:
- normalized weather summary used for recommendation scoring
"""


def get_weather_summary(city: str = "", latitude: float | None = None, longitude: float | None = None) -> dict:
    """Get weather summary.

    TODO:
    - call selected weather provider
    - normalize weather condition, temperature, rain probability
    - feed result into recommendation weather bonus logic
    """
    return {
        "city": city,
        "condition": "sunny",
        "temperature_c": None,
        "rain_probability": None,
    }
