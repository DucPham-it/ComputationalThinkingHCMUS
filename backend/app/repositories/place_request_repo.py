"""Repository for user-submitted place change requests."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


class PlaceRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_request(row, image_urls: dict[str, list[str]] | None = None) -> dict:
        grouped_images = image_urls or {"place": [], "review": []}
        return {
            "id": int(row["id"]),
            "requester_user_id": int(row["requester_user_id"]),
            "requester_name": row.get("requester_name"),
            "request_type": row["request_type"],
            "status": row["status"],
            "place_id": int(row["target_place_id"]) if row.get("target_place_id") is not None else None,
            "target_place_id": int(row["target_place_id"]) if row.get("target_place_id") is not None else None,
            "title": row.get("title"),
            "category": row.get("category"),
            "address_text": row.get("address_text"),
            "latitude": float(row["latitude"]) if row.get("latitude") is not None else None,
            "longitude": float(row["longitude"]) if row.get("longitude") is not None else None,
            "price_range": row.get("price_range"),
            "price_level": int(row["price_level"]) if row.get("price_level") is not None else None,
            "website": row.get("website"),
            "phone": row.get("phone"),
            "descriptions": row.get("descriptions"),
            "request_note": row.get("request_note"),
            "review_content": row.get("review_content"),
            "review_rating": int(row["review_rating"]) if row.get("review_rating") is not None else None,
            "place_image_urls": grouped_images.get("place", []),
            "review_image_urls": grouped_images.get("review", []),
            "admin_user_id": int(row["admin_user_id"]) if row.get("admin_user_id") is not None else None,
            "admin_note": row.get("admin_note"),
            "created_at": str(row["created_at"]) if row.get("created_at") is not None else None,
            "reviewed_at": str(row["reviewed_at"]) if row.get("reviewed_at") is not None else None,
        }

    def _list_images(self, request_id: int) -> dict[str, list[str]]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT image_type, image_url
                    FROM place_change_request_images
                    WHERE request_id = :request_id
                    ORDER BY image_type, sort_order ASC, id ASC
                    """
                ),
                {"request_id": request_id},
            )
            .mappings()
            .all()
        )
        grouped = {"place": [], "review": []}
        for row in rows:
            image_type = row.get("image_type") or "place"
            grouped.setdefault(image_type, []).append(str(row["image_url"]))
        return grouped

    def _add_images(self, request_id: int, *, place_image_urls: list[str], review_image_urls: list[str]) -> None:
        for image_type, image_urls in {
            "place": place_image_urls,
            "review": review_image_urls,
        }.items():
            cleaned_urls = [url.strip() for url in image_urls if url and url.strip()]
            for index, image_url in enumerate(cleaned_urls):
                self.db.execute(
                    text(
                        """
                        INSERT INTO place_change_request_images (
                            request_id,
                            image_type,
                            image_url,
                            sort_order
                        )
                        VALUES (:request_id, :image_type, :image_url, :sort_order)
                        """
                    ),
                    {
                        "request_id": request_id,
                        "image_type": image_type,
                        "image_url": image_url,
                        "sort_order": index,
                    },
                )

    def create_request(self, *, requester_user_id: int, payload) -> dict:
        row = (
            self.db.execute(
                text(
                    """
                    INSERT INTO place_change_requests (
                        requester_user_id,
                        request_type,
                        target_place_id,
                        title,
                        category,
                        address_text,
                        latitude,
                        longitude,
                        price_range,
                        price_level,
                        website,
                        phone,
                        descriptions,
                        request_note,
                        review_content,
                        review_rating
                    )
                    VALUES (
                        :requester_user_id,
                        :request_type,
                        :target_place_id,
                        :title,
                        :category,
                        :address_text,
                        :latitude,
                        :longitude,
                        :price_range,
                        :price_level,
                        :website,
                        :phone,
                        :descriptions,
                        :request_note,
                        :review_content,
                        :review_rating
                    )
                    RETURNING *
                    """
                ),
                {
                    "requester_user_id": requester_user_id,
                    "request_type": payload.request_type,
                    "target_place_id": payload.place_id,
                    "title": payload.title,
                    "category": payload.category,
                    "address_text": payload.address_text,
                    "latitude": payload.latitude,
                    "longitude": payload.longitude,
                    "price_range": payload.price_range,
                    "price_level": payload.price_level,
                    "website": payload.website,
                    "phone": payload.phone,
                    "descriptions": payload.descriptions,
                    "request_note": payload.request_note,
                    "review_content": payload.review_content,
                    "review_rating": payload.review_rating,
                },
            )
            .mappings()
            .one()
        )
        self._add_images(
            int(row["id"]),
            place_image_urls=payload.place_image_urls,
            review_image_urls=payload.review_image_urls,
        )
        self.db.commit()
        return self.get_by_id(int(row["id"]))

    def get_by_id(self, request_id: int) -> dict | None:
        row = (
            self.db.execute(
                text(
                    """
                    SELECT
                        pcr.*,
                        u.user_name AS requester_name
                    FROM place_change_requests AS pcr
                    LEFT JOIN users AS u ON u.id = pcr.requester_user_id
                    WHERE pcr.id = :request_id
                    """
                ),
                {"request_id": request_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            return None
        return self._to_request(row, self._list_images(request_id))

    def list_for_user(self, user_id: int) -> list[dict]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT
                        pcr.*,
                        u.user_name AS requester_name
                    FROM place_change_requests AS pcr
                    LEFT JOIN users AS u ON u.id = pcr.requester_user_id
                    WHERE pcr.requester_user_id = :user_id
                    ORDER BY pcr.created_at DESC, pcr.id DESC
                    """
                ),
                {"user_id": user_id},
            )
            .mappings()
            .all()
        )
        return [self._to_request(row, self._list_images(int(row["id"]))) for row in rows]

    def list_all(self, status: str | None = None) -> list[dict]:
        status_clause = "WHERE pcr.status = :status" if status else ""
        rows = (
            self.db.execute(
                text(
                    f"""
                    SELECT
                        pcr.*,
                        u.user_name AS requester_name
                    FROM place_change_requests AS pcr
                    LEFT JOIN users AS u ON u.id = pcr.requester_user_id
                    {status_clause}
                    ORDER BY
                        CASE pcr.status
                            WHEN 'pending' THEN 0
                            WHEN 'approved' THEN 1
                            ELSE 2
                        END,
                        pcr.created_at DESC,
                        pcr.id DESC
                    """
                ),
                {"status": status} if status else {},
            )
            .mappings()
            .all()
        )
        return [self._to_request(row, self._list_images(int(row["id"]))) for row in rows]

    def mark_reviewed(
        self,
        *,
        request_id: int,
        status: str,
        admin_user_id: int,
        admin_note: str | None = None,
        target_place_id: int | None = None,
    ) -> dict:
        row = (
            self.db.execute(
                text(
                    """
                    UPDATE place_change_requests
                    SET status = :status,
                        admin_user_id = :admin_user_id,
                        admin_note = :admin_note,
                        target_place_id = COALESCE(:target_place_id, target_place_id),
                        reviewed_at = CURRENT_TIMESTAMP
                    WHERE id = :request_id
                    RETURNING *
                    """
                ),
                {
                    "request_id": request_id,
                    "status": status,
                    "admin_user_id": admin_user_id,
                    "admin_note": admin_note,
                    "target_place_id": target_place_id,
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return self.get_by_id(int(row["id"]))

