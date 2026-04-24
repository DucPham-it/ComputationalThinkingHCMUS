"""Application settings."""

from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "travel-recommendation-backend"
    app_env: str = "development"
    app_port: int = 8000
    nominatim_base_url: str = "https://nominatim.openstreetmap.org"
    osrm_base_url: str = "https://router.project-osrm.org"
    external_maps_user_agent: str = "computationalthinking-hcmus/1.0"
    weather_api_key: str = ""
    resolve_point_local_match_radius_km: float = 0.35
    max_saved_places_per_user: int = 100
    max_picked_places_per_user: int = 60
    max_search_history_per_user: int = 80
    upload_max_bytes: int = 5 * 1024 * 1024
    supabase_url: str = ""
    supabase_service_role_key: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_STORAGE_KEY"),
    )
    supabase_storage_avatar_bucket: str = "avatars"
    supabase_storage_place_bucket: str = "place-images"
    supabase_storage_review_bucket: str = "review-images"
    supabase_storage_cache_control: str = "3600"
    database_url: str = Field(
        default="sqlite:///./travel_catalog.db",
        validation_alias=AliasChoices("DATABASE_URL", "SUPABASE_DB_URL"),
    )
    database_ssl_require: bool = Field(
        default=False,
        validation_alias=AliasChoices("DATABASE_SSL_REQUIRE", "DB_SSL_REQUIRE"),
    )
    jwt_secret: str = "change_this_secret"
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        extra="ignore",
    )


settings = Settings()
