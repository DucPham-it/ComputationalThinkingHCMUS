"""User picked places repository."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.place import Place


class PickRepository:
    def __init__(self, db: Session):
        self.db = db

    def _trim_picks(self, user_id: int) -> None:
        max_items = max(1, int(settings.max_picked_places_per_user))
        self.db.execute(
            text(
                """
                DELETE FROM user_place_picks
                WHERE id IN (
                    SELECT id
                    FROM user_place_picks
                    WHERE user_id = :user_id
                    ORDER BY picked_at DESC, id DESC
                    LIMIT -1 OFFSET :max_items
                )
                """
            ),
            {"user_id": user_id, "max_items": max_items},
        )

    def add_pick(self, user_id: int, place_id: int) -> None:
        self.db.execute(
            text(
                """
                INSERT INTO user_place_picks (user_id, place_id)
                VALUES (:user_id, :place_id)
                ON CONFLICT (user_id, place_id)
                DO UPDATE SET picked_at = NOW()
                """
            ),
            {"user_id": user_id, "place_id": place_id},
        )
        self._trim_picks(user_id)
        self.db.commit()

    def list_by_user(self, user_id: int, limit: int = 20) -> list[Place]:
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
                    FROM user_place_picks AS upp
                    JOIN places AS p ON p.id = upp.place_id
                    WHERE upp.user_id = :user_id
                    ORDER BY upp.picked_at DESC
                    LIMIT :limit
                    """
                ),
                {"user_id": user_id, "limit": limit},
            )
            .mappings()
            .all()
        )
        return [
            Place(
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
            for row in rows
        ]
