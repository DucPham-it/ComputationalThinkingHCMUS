"""Favorites repository."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.place import Place


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def _trim_favorites(self, user_id: int) -> None:
        max_items = max(1, int(settings.max_saved_places_per_user))
        self.db.execute(
            text(
                """
                DELETE FROM favorites
                WHERE id IN (
                    SELECT id
                    FROM favorites
                    WHERE user_id = :user_id
                    ORDER BY id DESC
                    LIMIT -1 OFFSET :max_items
                )
                """
            ),
            {"user_id": user_id, "max_items": max_items},
        )

    @staticmethod
    def _to_place(row) -> Place:
        return Place(
            id=int(row["id"]),
            name=row["name"],
            address=row["address"],
            external_place_id=row.get("external_place_id"),
            rating=float(row["rating"]) if row["rating"] is not None else None,
            latitude=float(row["latitude"]) if row.get("latitude") is not None else None,
            longitude=float(row["longitude"]) if row.get("longitude") is not None else None,
            price_level=int(row["price_level"]) if row.get("price_level") is not None else None,
            open_now=row.get("open_now"),
            photo_url=row.get("photo_url"),
            contact_phone=row.get("contact_phone"),
            primary_type=row.get("primary_type"),
        )

    def list_by_user(self, user_id: int, limit: int = 50) -> list[Place]:
        """Return user favorite places."""
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT
                        p.id,
                        p.name,
                        p.address,
                        p.external_place_id,
                        p.rating,
                        p.latitude,
                        p.longitude,
                        p.price_level,
                        p.open_now,
                        p.photo_url,
                        p.contact_phone,
                        p.primary_type
                    FROM favorites AS f
                    JOIN places AS p ON p.id = f.place_id
                    WHERE f.user_id = :user_id
                    ORDER BY f.id DESC
                    LIMIT :limit
                    """
                ),
                {"user_id": user_id, "limit": limit},
            )
            .mappings()
            .all()
        )
        return [self._to_place(row) for row in rows]

    def list_place_ids_by_user(self, user_id: int) -> list[int]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT place_id
                    FROM favorites
                    WHERE user_id = :user_id
                    ORDER BY id DESC
                    """
                ),
                {"user_id": user_id},
            )
            .mappings()
            .all()
        )
        return [int(row["place_id"]) for row in rows]

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
        self._trim_favorites(user_id)
        self.db.commit()

    def remove_favorite(self, user_id: int, place_id: int) -> None:
        self.db.execute(
            text(
                """
                DELETE FROM favorites
                WHERE user_id = :user_id AND place_id = :place_id
                """
            ),
            {"user_id": user_id, "place_id": place_id},
        )
        self.db.commit()
