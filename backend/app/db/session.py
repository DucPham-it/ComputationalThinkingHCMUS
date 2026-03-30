"""Database session management.

Current state:
- placeholder SQLite engine so project can start without full SQL Server wiring

Target state:
- replace with SQL Server engine using SQLAlchemy + pyodbc
- expose `get_db()` dependency for FastAPI routes
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# TODO: replace with SQL Server URI once pyodbc integration is finalized.
engine = create_engine("sqlite:///placeholder.db", echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)



def get_db():
    """Yield database session for FastAPI dependency injection.

    Output:
    - SQLAlchemy session object

    TODO:
    - ensure session commits/rollbacks are handled centrally
    - migrate engine from SQLite placeholder to SQL Server
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
