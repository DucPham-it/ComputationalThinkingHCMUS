from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_favorites() -> dict:
    """Return favorite places of current user.

    TODO:
    - require authenticated user
    - fetch favorite place ids from database
    - enrich with place summary for frontend cards
    """
    return {"items": []}
