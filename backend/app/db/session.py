"""Database session management.

Current state:
- use SQLAlchemy sessions against the configured database URL

Supported databases:
- Supabase / PostgreSQL through `DATABASE_URL`
- SQLite fallback for local placeholder runs
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.db.connection import build_database_url

database_url = build_database_url()
engine_options: dict = {"echo": False, "pool_pre_ping": True}

if database_url.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    # Supabase already manages Postgres connections; avoid long-lived stale pools.
    engine_options["poolclass"] = NullPool
    # Supabase PgBouncer transaction pooling is incompatible with psycopg prepared statements.
    engine_options["connect_args"] = {"prepare_threshold": None}

engine = create_engine(database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)



def get_db():
    """Yield database session for FastAPI dependency injection.

    Output:
    - SQLAlchemy session object

    TODO:
    - ensure session commits/rollbacks are handled centrally
    - wire repositories and routes to use the shared session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
