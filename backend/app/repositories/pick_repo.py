"""User picked places repository."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.place import Place
from app.repositories.place_repo import _normalize_primary_type


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
                    FROM (
                        SELECT
                            id,
                            ROW_NUMBER() OVER (ORDER BY picked_at DESC, id DESC) AS item_rank
                        FROM user_place_picks
                        WHERE user_id = :user_id
                    ) AS ranked_picks
                    WHERE item_rank > :max_items
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
                DO UPDATE SET picked_at = CURRENT_TIMESTAMP
                """
            ),
            {"user_id": user_id, "place_id": place_id},
        )
        self._trim_picks(user_id)
        self.db.commit()

    def list_by_user(self, user_id: int, limit: int = 20) -> list[Place]:
        query = """
            SELECT
                p.id,
                p.title AS name,
                p.address_text AS address,
                p.place_id AS external_place_id,
                prs.average_rating AS rating,
                COALESCE(prs.review_count, 0) AS review_count,
                p.latitude,
                p.longitude,
                p.price_level,
                p.price_range,
                NULL AS open_now,
                (
                    SELECT pi.image_url
                    FROM place_images AS pi
                    WHERE pi.place_id = p.id
                    ORDER BY pi.is_primary DESC, pi.sort_order ASC, pi.id ASC
                    LIMIT 1
                ) AS photo_url,
                p.phone AS contact_phone,
                p.category AS primary_type
            FROM user_place_picks AS upp
            JOIN places AS p ON p.id = upp.place_id
            LEFT JOIN place_review_stats AS prs ON prs.place_id = p.id
            WHERE upp.user_id = :user_id
            ORDER BY upp.picked_at DESC
            LIMIT :limit
        """
        legacy_query = """
            SELECT
                p.id,
                p.title AS name,
                p.address_text AS address,
                p.place_id AS external_place_id,
                p.review_rating AS rating,
                p.review_count,
                p.latitude,
                p.longitude,
                p.price_level,
                p.price_range,
                NULL AS open_now,
                p.thumbnail AS photo_url,
                p.phone AS contact_phone,
                p.category AS primary_type
            FROM user_place_picks AS upp
            JOIN places AS p ON p.id = upp.place_id
            WHERE upp.user_id = :user_id
            ORDER BY upp.picked_at DESC
            LIMIT :limit
        """
        try:
            rows = self.db.execute(text(query), {"user_id": user_id, "limit": limit}).mappings().all()
        except DBAPIError:
            self.db.rollback()
            rows = self.db.execute(text(legacy_query), {"user_id": user_id, "limit": limit}).mappings().all()
        return [
            Place(
                id=int(row["id"]),
                name=row["name"],
                address=row["address"],
                external_place_id=row.get("external_place_id"),
                rating=float(row["rating"]) if row["rating"] is not None else None,
                review_count=int(row.get("review_count") or 0),
                latitude=float(row["latitude"]) if row.get("latitude") is not None else None,
                longitude=float(row["longitude"]) if row.get("longitude") is not None else None,
                price_level=int(row["price_level"]) if row.get("price_level") is not None else None,
                price_range=row.get("price_range"),
                open_now=row.get("open_now"),
                photo_url=row.get("photo_url"),
                contact_phone=row.get("contact_phone"),
                primary_type=_normalize_primary_type(row.get("primary_type")),
            )
            for row in rows
        ]
