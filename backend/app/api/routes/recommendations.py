from fastapi import APIRouter

from app.recommendation.recommender import recommend_places

router = APIRouter()


@router.get("")
def get_recommendations(query: str = "") -> dict:
    """Recommendation list endpoint.

    Input:
    - query: free-text search string from frontend

    Output:
    - list of recommended places

    Future extension:
    - replace simple query params with structured recommendation payload
    - add browser GPS coordinates and filter params
    """
    items = recommend_places(query=query)
    return {"items": items}
