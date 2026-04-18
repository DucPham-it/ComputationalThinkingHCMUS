"""FastAPI application entry point.

Input:
- HTTP requests from frontend React application.
- JSON payloads validated by Pydantic schemas.

Output:
- JSON responses for auth, place details, recommendations, routes, reviews, weather.

Responsibility:
- register routers
- configure CORS
- expose health endpoint
"""

import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, favorites, places, recommendations, reviews, routes, weather
from app.core.config import settings
from app.db.connection import check_database_connection
from app.db.session import SessionLocal, engine
from app.repositories.temp_place_cache_repo import TemporaryPlaceCacheRepository


async def run_temporary_cache_cleanup() -> None:
    """Background cleanup loop for expired temporary place cache rows."""
    interval_seconds = max(60, int(settings.temporary_place_cache_cleanup_interval_minutes) * 60)

    while True:
        db = SessionLocal()
        try:
            TemporaryPlaceCacheRepository(db).cleanup_expired()
        except Exception as exc:  # pragma: no cover - background safety
            print(f"Temporary cache cleanup failed: {exc}")
            db.rollback()
        finally:
            db.close()

        await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    cleanup_task = asyncio.create_task(run_temporary_cache_cleanup())
    try:
        yield
    finally:
        cleanup_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(places.router, prefix="/api/v1/places", tags=["places"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(favorites.router, prefix="/api/v1/favorites", tags=["favorites"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(routes.router, prefix="/api/v1/routes", tags=["routes"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["weather"])


@app.get("/health")
def health_check() -> dict[str, str]:
    """Basic liveness endpoint.

    Input:
    - no input

    Output:
    - dict with backend status
    """
    database_ok, database_message = check_database_connection(engine)
    return {
        "status": "ok",
        "database": "connected" if database_ok else f"error: {database_message}",
        "driver": engine.url.drivername,
    }
