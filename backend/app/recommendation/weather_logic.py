"""Weather-aware scoring helpers."""



def weather_bonus(condition: str) -> float:
    """Return additive score bonus based on weather condition.

    Example intent:
    - sunny weather may favor outdoor attractions
    - rainy weather may favor indoor places like malls, cafés, cinemas

    TODO:
    - expand to type-aware bonus logic
    - include rain probability, temperature, and time of day
    """
    normalized = condition.lower().strip()
    if normalized == "sunny":
        return 1.0
    if normalized in {"rain", "rainy", "storm"}:
        return 0.2
    return 0.0
