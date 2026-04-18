"""Application settings.

Input source:
- environment variables from `backend/.env`

Output:
- strongly typed settings object used across backend layers
"""

from pathlib import Path

from pydantic import AliasChoices, Field
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
    temporary_place_cache_ttl_minutes: int = 30
    route_distance_candidate_limit: int = 10
    temporary_place_cache_cleanup_interval_minutes: int = 10
    max_saved_places_per_user: int = 100
    max_picked_places_per_user: int = 60
    max_search_history_per_user: int = 60
    database_url: str = Field(
        default="sqlite:///placeholder.db",
        validation_alias=AliasChoices("DATABASE_URL", "SUPABASE_DB_URL"),
    )
    database_ssl_require: bool = Field(
        default=True,
        validation_alias=AliasChoices("DATABASE_SSL_REQUIRE", "DB_SSL_REQUIRE"),
    )
    db_host: str = "localhost"
    db_port: int = 1433
    db_name: str = "TravelAppDB"
    db_user: str = "sa"
    db_password: str = ""
    jwt_secret: str = "change_this_secret"
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        extra="ignore",
    )


settings = Settings()
