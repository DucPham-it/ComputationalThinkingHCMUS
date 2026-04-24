"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, auth, favorites, place_requests, places, recommendations, reviews, routes, uploads, weather
from app.core.config import settings
from app.db.connection import check_database_connection
from app.db.session import engine

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(places.router, prefix="/api/v1/places", tags=["places"])
app.include_router(place_requests.router, prefix="/api/v1/place-requests", tags=["place-requests"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["uploads"])
app.include_router(favorites.router, prefix="/api/v1/favorites", tags=["favorites"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(routes.router, prefix="/api/v1/routes", tags=["routes"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["weather"])


@app.get("/health")
def health_check() -> dict[str, str]:
    database_ok, database_message = check_database_connection(engine)
    return {
        "status": "ok",
        "database": "connected" if database_ok else f"error: {database_message}",
        "driver": engine.url.drivername,
    }
