"""Application settings."""

import json
from pathlib import Path
from typing import Annotated, Any

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "travel-recommendation-backend"
    app_env: str = "development"
    app_port: int = Field(default=8000, validation_alias=AliasChoices("APP_PORT", "PORT"))
    nominatim_base_url: str = "https://nominatim.openstreetmap.org"
    osrm_base_url: str = "https://router.project-osrm.org"
    external_maps_user_agent: str = "computationalthinking-hcmus/1.0"
    resolve_point_local_match_radius_km: float = 0.35
    max_saved_places_per_user: int = 100
    max_picked_places_per_user: int = 60
    max_search_history_per_user: int = 80
    upload_max_bytes: int = 5 * 1024 * 1024
    gemini_api_key: str = ""
    supabase_url: str = ""
    supabase_service_role_key: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_STORAGE_KEY"),
    )
    supabase_storage_avatar_bucket: str = "avatars"
    supabase_storage_place_bucket: str = "place-images"
    supabase_storage_review_bucket: str = "review-images"
    supabase_storage_cache_control: str = "3600"
    local_storage_dir: str = Field(
        default="",
        validation_alias=AliasChoices("LOCAL_STORAGE_DIR", "STORAGE_DIR"),
    )
    database_url: str = Field(
        default=f"sqlite:///{Path(__file__).resolve().parents[2].as_posix()}/travel_catalog.db",
        validation_alias=AliasChoices("DATABASE_URL", "SUPABASE_DB_URL"),
    )
    database_ssl_require: bool = Field(
        default=False,
        validation_alias=AliasChoices("DATABASE_SSL_REQUIRE", "DB_SSL_REQUIRE"),
    )
    jwt_secret: str = "change_this_secret"
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    cors_origin_regex: str | None = Field(
        default=r"^https://computational-thinking-hcmus(?:-[a-z0-9]+(?:-[a-z0-9]+)*)?\.vercel\.app$",
        validation_alias=AliasChoices("CORS_ORIGIN_REGEX", "CORS_REGEX"),
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        raw_value = value.strip()
        if not raw_value:
            return []

        if raw_value.startswith("["):
            return json.loads(raw_value)

        return [origin.strip() for origin in raw_value.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        extra="ignore",
    )


settings = Settings()
