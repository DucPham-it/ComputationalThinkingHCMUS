"""Place repository for internal place data."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.place import Place


PLACE_SELECT_COLUMNS = """
    id,
    name,
    address,
    external_place_id,
    rating,
    latitude,
    longitude,
    price_level,
    open_now,
    photo_url,
    contact_phone,
    primary_type
"""


class PlaceRepository:
    def __init__(self, db: Session):
        self.db = db

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

    def get_by_id(self, place_id: int) -> Place | None:
        """Fetch local place record by id."""
        row = (
            self.db.execute(
                text(
                    f"""
                    SELECT {PLACE_SELECT_COLUMNS}
                    FROM places
                    WHERE id = :place_id
                    """
                ),
                {"place_id": place_id},
            )
            .mappings()
            .first()
        )
        return self._to_place(row) if row else None

    def get_by_external_id(self, external_place_id: str) -> Place | None:
        """Fetch local place record by external place id."""
        row = (
            self.db.execute(
                text(
                    f"""
                    SELECT {PLACE_SELECT_COLUMNS}
                    FROM places
                    WHERE external_place_id = :external_place_id
                    """
                ),
                {"external_place_id": external_place_id},
            )
            .mappings()
            .first()
        )
        return self._to_place(row) if row else None

    def search_local_places(self, keyword: str = "") -> list[Place]:
        """Search locally stored places."""
        normalized_keyword = f"%{keyword.lower()}%"
        rows = (
            self.db.execute(
                text(
                    f"""
                    SELECT {PLACE_SELECT_COLUMNS}
                    FROM places
                    WHERE :keyword = '%%'
                       OR LOWER(name) LIKE :keyword
                       OR LOWER(address) LIKE :keyword
                    ORDER BY id DESC
                    """
                ),
                {"keyword": normalized_keyword},
            )
            .mappings()
            .all()
        )
        return [self._to_place(row) for row in rows]

    def ensure_exists(
        self,
        place_id: int,
        name: str | None = None,
        address: str | None = None,
        rating: float | None = None,
    ) -> Place:
        """Create a minimal local place record when it does not exist yet."""
        existing_place = self.get_by_id(place_id)
        if existing_place is not None:
            return existing_place

        default_name = name or ("Sample Place" if place_id == 1 else f"Place #{place_id}")
        default_address = address or ("123 Demo Street" if place_id == 1 else "Unknown address")
        row = (
            self.db.execute(
                text(
                    f"""
                    INSERT INTO places (id, name, address, rating)
                    VALUES (:id, :name, :address, :rating)
                    RETURNING {PLACE_SELECT_COLUMNS}
                    """
                ),
                {
                    "id": place_id,
                    "name": default_name,
                    "address": default_address,
                    "rating": rating,
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return self._to_place(row)

    def upsert_external_place(
        self,
        *,
        external_place_id: str,
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
    ) -> Place:
        """Create or update a local place mapped from an external provider."""
        existing_place = self.get_by_external_id(external_place_id)
        if existing_place is None:
            row = (
                self.db.execute(
                    text(
                        f"""
                        INSERT INTO places (
                            name,
                            address,
                            external_place_id,
                            rating,
                            latitude,
                            longitude,
                            price_level,
                            open_now,
                            photo_url,
                            contact_phone,
                            primary_type
                        )
                        VALUES (
                            :name,
                            :address,
                            :external_place_id,
                            :rating,
                            :latitude,
                            :longitude,
                            :price_level,
                            :open_now,
                            :photo_url,
                            :contact_phone,
                            :primary_type
                        )
                        RETURNING {PLACE_SELECT_COLUMNS}
                        """
                    ),
                    {
                        "name": name,
                        "address": address,
                        "external_place_id": external_place_id,
                        "rating": rating,
                        "latitude": latitude,
                        "longitude": longitude,
                        "price_level": price_level,
                        "open_now": open_now,
                        "photo_url": photo_url,
                        "contact_phone": contact_phone,
                        "primary_type": primary_type,
                    },
                )
                .mappings()
                .one()
            )
            self.db.commit()
            return self._to_place(row)

        self.db.execute(
            text(
                """
                UPDATE places
                SET name = :name,
                    address = :address,
                    rating = :rating,
                    latitude = :latitude,
                    longitude = :longitude,
                    price_level = :price_level,
                    open_now = :open_now,
                    photo_url = :photo_url,
                    contact_phone = COALESCE(:contact_phone, contact_phone),
                    primary_type = :primary_type
                WHERE external_place_id = :external_place_id
                """
            ),
            {
                "name": name,
                "address": address,
                "external_place_id": external_place_id,
                "rating": rating,
                "latitude": latitude,
                "longitude": longitude,
                "price_level": price_level,
                "open_now": open_now,
                "photo_url": photo_url,
                "contact_phone": contact_phone,
                "primary_type": primary_type,
            },
        )
        self.db.commit()
        return self.get_by_external_id(external_place_id) or existing_place

    def update_rating(self, place_id: int, rating: float | None) -> None:
        """Persist the latest aggregated rating for a place."""
        self.db.execute(
            text(
                """
                UPDATE places
                SET rating = :rating
                WHERE id = :place_id
                """
            ),
            {"place_id": place_id, "rating": rating},
        )
        self.db.commit()
