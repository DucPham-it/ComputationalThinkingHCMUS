from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.repositories.favorite_repo import FavoriteRepository

router = APIRouter()


@router.get("")
def list_favorites(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return favorite places of current user."""
    favorite_repo = FavoriteRepository(db)
    items = [
        {
            "id": place.id,
            "name": place.name,
            "address": place.address,
            "rating": place.rating,
        }
        for place in favorite_repo.list_by_user(current_user["id"])
    ]
    return {"items": items}
