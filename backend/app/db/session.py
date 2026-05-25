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

if database_url.startswith("sqlite"):
    # Automatically initialize SQLite tables if they do not exist
    with engine.begin() as connection:
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            birth_date TEXT,
            gender TEXT,
            address TEXT,
            avatar_url TEXT,
            is_virtual INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            complete_address_json TEXT,
            address_text TEXT NOT NULL,
            borough TEXT,
            street TEXT,
            city TEXT,
            postal_code TEXT,
            state TEXT,
            country TEXT,
            latitude REAL,
            longitude REAL,
            open_hours_json TEXT NOT NULL DEFAULT '{}',
            popular_times_json TEXT NOT NULL DEFAULT '{}',
            price_range TEXT,
            price_level INTEGER,
            website TEXT,
            phone TEXT,
            descriptions TEXT,
            about_json TEXT NOT NULL DEFAULT '[]',
            status TEXT,
            place_id TEXT UNIQUE,
            cid TEXT UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            place_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            rating INTEGER NOT NULL,
            reviewed_at TEXT,
            is_imported INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS place_review_stats (
            place_id INTEGER PRIMARY KEY,
            average_rating REAL,
            review_count INTEGER NOT NULL DEFAULT 0,
            rating_1_count INTEGER NOT NULL DEFAULT 0,
            rating_2_count INTEGER NOT NULL DEFAULT 0,
            rating_3_count INTEGER NOT NULL DEFAULT 0,
            rating_4_count INTEGER NOT NULL DEFAULT 0,
            rating_5_count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS place_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_id INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            title TEXT,
            sort_order INTEGER NOT NULL DEFAULT 0,
            is_primary INTEGER NOT NULL DEFAULT 0,
            source TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS review_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            place_id INTEGER NOT NULL,
            UNIQUE (user_id, place_id)
        )
        """)
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            status TEXT NOT NULL,
            role TEXT NOT NULL,
            approved_by INTEGER,
            approved_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS place_change_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester_user_id INTEGER NOT NULL,
            request_type TEXT NOT NULL,
            status TEXT NOT NULL,
            target_place_id INTEGER,
            title TEXT,
            category TEXT,
            address_text TEXT,
            latitude REAL,
            longitude REAL,
            price_range TEXT,
            price_level INTEGER,
            website TEXT,
            phone TEXT,
            descriptions TEXT,
            request_note TEXT,
            review_content TEXT,
            review_rating INTEGER,
            admin_user_id INTEGER,
            admin_note TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TEXT
        )
        """)
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS place_change_request_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            image_type TEXT NOT NULL,
            image_url TEXT NOT NULL,
            sort_order INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS user_place_picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            place_id INTEGER NOT NULL,
            picked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        connection.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS user_search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            searched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)

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
