"""Temporary place cache repository with TTL support."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


class TemporaryPlaceCacheRepository:
    def __init__(self, db: Session):
        self.db = db

    def cleanup_expired(self) -> None:
        self.db.execute(
            text(
                """
                DELETE FROM temporary_place_cache
                WHERE expires_at <= CURRENT_TIMESTAMP
                """
            )
        )
        self.db.commit()

    def upsert_cached_place(
        self,
        *,
        place_id: int,
        external_place_id: str | None,
        name: str,
        address: str,
        rating: float | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        price_level: int | None = None,
        open_now: bool | None = None,
        photo_url: str | None = None,
        contact_phone: str | None = None,
        primary_type: str | None = None,
        ttl_minutes: int = 30,
    ) -> None:
        self.db.execute(
            text(
                """
                DELETE FROM temporary_place_cache
                WHERE place_id = :place_id
                """
            ),
            {"place_id": place_id},
        )
        self.db.execute(
            text(
                """
                INSERT INTO temporary_place_cache (
                    place_id,
                    external_place_id,
                    name,
                    address,
                    rating,
                    latitude,
                    longitude,
                    price_level,
                    open_now,
                    photo_url,
                    contact_phone,
                    primary_type,
                    expires_at
                )
                VALUES (
                    :place_id,
                    :external_place_id,
                    :name,
                    :address,
                    :rating,
                    :latitude,
                    :longitude,
                    :price_level,
                    :open_now,
                    :photo_url,
                    :contact_phone,
                    :primary_type,
                    CURRENT_TIMESTAMP + CAST(:ttl_interval AS INTERVAL)
                )
                """
            ),
            {
                "place_id": place_id,
                "external_place_id": external_place_id,
                "name": name,
                "address": address,
                "rating": rating,
                "latitude": latitude,
                "longitude": longitude,
                "price_level": price_level,
                "open_now": open_now,
                "photo_url": photo_url,
                "contact_phone": contact_phone,
                "primary_type": primary_type,
                "ttl_interval": f"{ttl_minutes} minutes",
            },
        )
        self.db.commit()

    def search_active_places(self, query: str = "", limit: int = 20) -> list[dict]:
        normalized_keyword = f"%{query.lower()}%"
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT
                        place_id,
                        external_place_id,
                        name,
                        address,
                        rating,
                        latitude,
                        longitude,
                        price_level,
                        open_now,
                        photo_url,
                        contact_phone,
                        primary_type
                    FROM temporary_place_cache
                    WHERE expires_at > CURRENT_TIMESTAMP
                      AND (
                        :keyword = '%%'
                        OR LOWER(name) LIKE :keyword
                        OR LOWER(address) LIKE :keyword
                      )
                    ORDER BY expires_at DESC, id DESC
                    LIMIT :limit
                    """
                ),
                {"keyword": normalized_keyword, "limit": limit},
            )
            .mappings()
            .all()
        )
        return [
            {
                "id": int(row["place_id"]),
                "external_place_id": row.get("external_place_id"),
                "name": row["name"],
                "address": row["address"],
                "rating": None,
                "latitude": float(row["latitude"]) if row.get("latitude") is not None else None,
                "longitude": float(row["longitude"]) if row.get("longitude") is not None else None,
                "distance_km": None,
                "review_count": 0,
                "price_level": int(row["price_level"]) if row.get("price_level") is not None else None,
                "open_now": row.get("open_now"),
                "photo_url": row.get("photo_url"),
                "contact_phone": row.get("contact_phone"),
                "primary_type": row.get("primary_type"),
                "score": None,
            }
            for row in rows
        ]
