"""Database bootstrap helpers.

Typical use cases:
- run SQL migration files once in development
- seed sample records for local testing
"""

from pathlib import Path



def init_db() -> None:
    """Initialize database resources.

    Current behavior:
    - prints a placeholder message

    TODO:
    - open SQL Server connection
    - execute migration files in order from `backend/app/migrations/`
    - optionally insert development seed data
    """
    migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
    print(f"Initialize database here. Migration directory: {migrations_dir}")
