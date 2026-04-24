"""Review repository."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models.review import Review
from app.services.upload_storage import default_avatar_url


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def _list_review_images(self, review_ids: list[int]) -> dict[int, list[str]]:
        if not review_ids:
            return {}

        try:
            rows = []
            for review_id in review_ids:
                rows.extend(
                    self.db.execute(
                        text(
                            """
                            SELECT review_id, image_url
                            FROM review_images
                            WHERE review_id = :review_id
                            ORDER BY sort_order ASC, id ASC
                            """
                        ),
                        {"review_id": review_id},
                    )
                    .mappings()
                    .all()
                )
        except DBAPIError:
            self.db.rollback()
            return {}

        images_by_review: dict[int, list[str]] = {}
        for row in rows:
            review_id = int(row["review_id"])
            images_by_review.setdefault(review_id, []).append(str(row["image_url"]))
        return images_by_review

    def _add_review_images(self, review_id: int, image_urls: list[str]) -> None:
        cleaned_urls = [url.strip() for url in image_urls if url and url.strip()]
        if not cleaned_urls:
            return

        try:
            for index, image_url in enumerate(cleaned_urls):
                self.db.execute(
                    text(
                        """
                        INSERT INTO review_images (review_id, image_url, sort_order)
                        VALUES (:review_id, :image_url, :sort_order)
                        """
                    ),
                    {
                        "review_id": review_id,
                        "image_url": image_url,
                        "sort_order": index,
                    },
                )
            self.db.commit()
        except DBAPIError:
            self.db.rollback()

    @staticmethod
    def _to_review(row) -> Review:
        return Review(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            place_id=int(row["place_id"]),
            content=row["content"],
            rating=int(row["rating"]),
            user_name=row.get("user_name"),
            user_avatar_url=row.get("user_avatar_url") or default_avatar_url(),
            reviewed_at=row.get("reviewed_at"),
            image_urls=[],
            is_virtual_user=bool(row.get("is_virtual_user") or False),
        )

    def list_by_place(self, place_id: int) -> list[Review]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT
                        r.id,
                        r.user_id,
                        r.place_id,
                        r.content,
                        r.rating,
                        r.reviewed_at,
                        u.user_name,
                        u.avatar_url AS user_avatar_url,
                        u.is_virtual AS is_virtual_user
                    FROM reviews AS r
                    JOIN users AS u ON u.id = r.user_id
                    WHERE r.place_id = :place_id
                    ORDER BY
                        CASE WHEN NULLIF(CAST(r.reviewed_at AS TEXT), '') IS NULL THEN 1 ELSE 0 END,
                        r.reviewed_at DESC,
                        r.created_at DESC,
                        r.id DESC
                    """
                ),
                {"place_id": place_id},
            )
            .mappings()
            .all()
        )
        reviews = [self._to_review(row) for row in rows]
        images_by_review = self._list_review_images([review.id for review in reviews])
        for review in reviews:
            review.image_urls = images_by_review.get(review.id, [])
        return reviews

    def create_review(
        self,
        user_id: int,
        place_id: int,
        content: str,
        rating: int,
        image_urls: list[str] | None = None,
    ) -> Review:
        row = (
            self.db.execute(
                text(
                    """
                    INSERT INTO reviews (
                        user_id,
                        place_id,
                        content,
                        rating,
                        reviewed_at,
                        is_imported
                    )
                    VALUES (
                        :user_id,
                        :place_id,
                        :content,
                        :rating,
                        CAST(CURRENT_TIMESTAMP AS TEXT),
                        FALSE
                    )
                    RETURNING id, user_id, place_id, content, rating, reviewed_at
                    """
                ),
                {
                    "user_id": user_id,
                    "place_id": place_id,
                    "content": content,
                    "rating": rating,
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        self._add_review_images(int(row["id"]), image_urls or [])

        hydrated_row = (
            self.db.execute(
                text(
                    """
                    SELECT
                        r.id,
                        r.user_id,
                        r.place_id,
                        r.content,
                        r.rating,
                        r.reviewed_at,
                        u.user_name,
                        u.avatar_url AS user_avatar_url,
                        u.is_virtual AS is_virtual_user
                    FROM reviews AS r
                    JOIN users AS u ON u.id = r.user_id
                    WHERE r.id = :review_id
                    """
                ),
                {"review_id": row["id"]},
            )
            .mappings()
            .one()
        )
        review = self._to_review(hydrated_row)
        review.image_urls = self._list_review_images([review.id]).get(review.id, review.image_urls)
        return review
