"""Application settings.

Input source:
- environment variables from `backend/.env`

Output:
- strongly typed settings object used across backend layers
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration.

    Notes:
    - Keep secret keys only in backend `.env`.
    - Do not expose private API keys to frontend unless the API explicitly requires a browser key.
    """

    app_name: str = "travel-recommendation-backend"
    app_env: str = "development"
    app_port: int = 8000
    google_maps_api_key: str = ""
    weather_api_key: str = ""
    db_host: str = "localhost"
    db_port: int = 1433
    db_name: str = "TravelAppDB"
    db_user: str = "sa"
    db_password: str = ""
    jwt_secret: str = "change_this_secret"
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
