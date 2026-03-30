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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, favorites, places, recommendations, reviews, routes, weather
from app.core.config import settings

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
    return {"status": "ok"}
