"""Database bootstrap helpers.

Typical use cases:
- run SQL migration files against Supabase/Postgres
- seed sample records for local testing later
"""

from pathlib import Path

from app.db.session import engine


def init_db() -> None:
    """Initialize database resources.

    Current behavior:
    - execute migration files in order from `backend/app/migrations/`
    """
    migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    with engine.begin() as connection:
        for migration_file in migration_files:
            sql = migration_file.read_text(encoding="utf-8").strip()
            if not sql:
                continue
            connection.exec_driver_sql(sql)
            print(f"Applied migration: {migration_file.name}")


if __name__ == "__main__":
    init_db()
