"""Favorites repository."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.place import Place


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, user_id: int) -> list[Place]:
        """Return user favorite places."""
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT p.id, p.name, p.address, p.rating
                    FROM favorites AS f
                    JOIN places AS p ON p.id = f.place_id
                    WHERE f.user_id = :user_id
                    ORDER BY f.id DESC
                    """
                ),
                {"user_id": user_id},
            )
            .mappings()
            .all()
        )
        return [
            Place(
                id=int(row["id"]),
                name=row["name"],
                address=row["address"],
                rating=float(row["rating"]) if row["rating"] is not None else None,
            )
            for row in rows
        ]

    def add_favorite(self, user_id: int, place_id: int) -> None:
        """Save a place as favorite for a user."""
        existing = self.db.execute(
            text(
                """
                SELECT id
                FROM favorites
                WHERE user_id = :user_id AND place_id = :place_id
                """
            ),
            {"user_id": user_id, "place_id": place_id},
        ).first()
        if existing is not None:
            return

        self.db.execute(
            text(
                """
                INSERT INTO favorites (user_id, place_id)
                VALUES (:user_id, :place_id)
                """
            ),
            {"user_id": user_id, "place_id": place_id},
        )
        self.db.commit()
