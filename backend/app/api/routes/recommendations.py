from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.recommendation.recommender import recommend_places

router = APIRouter()


@router.get("")
def get_recommendations(
    query: str = "",
    latitude: float | None = None,
    longitude: float | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """Recommendation list endpoint.

    Input:
    - query: free-text search string from frontend

    Output:
    - list of recommended places

    Future extension:
    - replace simple query params with structured recommendation payload
    - add browser GPS coordinates and filter params
    """
    items = recommend_places(query=query, latitude=latitude, longitude=longitude, db=db)
    return {"items": items}
