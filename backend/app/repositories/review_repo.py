"""Review repository."""

from __future__ import annotations

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_review(row) -> Review:
        return Review(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            place_id=int(row["place_id"]),
            content=row["content"],
            rating=int(row["rating"]),
        )

    def list_by_place(self, place_id: int) -> list[Review]:
        """Return all reviews for a place."""
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT id, user_id, place_id, content, rating
                    FROM reviews
                    WHERE place_id = :place_id
                    ORDER BY id DESC
                    """
                ),
                {"place_id": place_id},
            )
            .mappings()
            .all()
        )
        return [self._to_review(row) for row in rows]

    def create_review(self, user_id: int, place_id: int, content: str, rating: int) -> Review:
        """Insert review and return created review."""
        row = (
            self.db.execute(
                text(
                    """
                    INSERT INTO reviews (user_id, place_id, content, rating)
                    VALUES (:user_id, :place_id, :content, :rating)
                    RETURNING id, user_id, place_id, content, rating
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
        return self._to_review(row)

    def get_place_summary(self, place_id: int) -> tuple[float | None, int]:
        """Return average rating and review count for a place."""
        row = (
            self.db.execute(
                text(
                    """
                    SELECT AVG(rating) AS average_rating, COUNT(*) AS review_count
                    FROM reviews
                    WHERE place_id = :place_id
                    """
                ),
                {"place_id": place_id},
            )
            .mappings()
            .one()
        )
        review_count = int(row["review_count"] or 0)
        average_rating = float(row["average_rating"]) if row["average_rating"] is not None else None
        return average_rating, review_count

    def get_place_summaries(self, place_ids: list[int]) -> dict[int, dict[str, float | int | None]]:
        """Return average rating and review count keyed by place id."""
        if not place_ids:
            return {}

        rows = (
            self.db.execute(
                text(
                    """
                    SELECT place_id, AVG(rating) AS average_rating, COUNT(*) AS review_count
                    FROM reviews
                    WHERE place_id IN :place_ids
                    GROUP BY place_id
                    """
                ).bindparams(bindparam("place_ids", expanding=True)),
                {"place_ids": place_ids},
            )
            .mappings()
            .all()
        )

        summaries: dict[int, dict[str, float | int | None]] = {}
        for row in rows:
            place_id = int(row["place_id"])
            summaries[place_id] = {
                "average_rating": (
                    float(row["average_rating"]) if row["average_rating"] is not None else None
                ),
                "review_count": int(row["review_count"] or 0),
            }
        return summaries
