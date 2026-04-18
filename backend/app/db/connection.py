"""Database URL helpers.

Current goal:
- normalize a SQLAlchemy URL for the active database
- support Supabase/Postgres through a single `DATABASE_URL`
- provide a lightweight connectivity probe for health checks
"""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.config import settings


def normalize_database_url(database_url: str) -> str:
    """Normalize connection strings for SQLAlchemy.

    Supported forms:
    - `postgres://...`
    - `postgresql://...`
    - `postgresql+psycopg://...`
    - `sqlite:///...`

    Output:
    - SQLAlchemy-ready database URL
    """
    database_url = database_url.strip()

    if not database_url:
        return "sqlite:///placeholder.db"

    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://") :]

    if database_url.startswith("postgresql://"):
        database_url = "postgresql+psycopg://" + database_url[len("postgresql://") :]

    if not database_url.startswith("postgresql+psycopg://"):
        return database_url

    parsed_url = urlsplit(database_url)
    query_params = dict(parse_qsl(parsed_url.query, keep_blank_values=True))

    if settings.database_ssl_require and "sslmode" not in query_params:
        query_params["sslmode"] = "require"

    return urlunsplit(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            urlencode(query_params),
            parsed_url.fragment,
        )
    )


def build_database_url() -> str:
    """Return the active database URL from settings."""
    return normalize_database_url(settings.database_url)


def check_database_connection(engine: Engine) -> tuple[bool, str]:
    """Run a tiny probe query against the active database."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "connected"
    except Exception as exc:  # pragma: no cover - defensive health check
        return False, str(exc)
