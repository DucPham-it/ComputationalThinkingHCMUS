"""User search history repository."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings


class SearchHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def _trim_history(self, user_id: int) -> None:
        max_items = max(1, int(settings.max_search_history_per_user))
        self.db.execute(
            text(
                """
                DELETE FROM user_search_history
                WHERE id IN (
                    SELECT id
                    FROM user_search_history
                    WHERE user_id = :user_id
                    ORDER BY searched_at DESC, id DESC
                    LIMIT -1 OFFSET :max_items
                )
                """
            ),
            {"user_id": user_id, "max_items": max_items},
        )

    def record_search(
        self,
        *,
        user_id: int,
        query: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        normalized_query = query.strip()
        if not normalized_query:
            return

        self.db.execute(
            text(
                """
                INSERT INTO user_search_history (user_id, query, latitude, longitude)
                VALUES (:user_id, :query, :latitude, :longitude)
                """
            ),
            {
                "user_id": user_id,
                "query": normalized_query,
                "latitude": latitude,
                "longitude": longitude,
            },
        )
        self._trim_history(user_id)
        self.db.commit()

    def list_recent_queries(self, user_id: int, limit: int = 10) -> list[str]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT query
                    FROM user_search_history
                    WHERE user_id = :user_id
                    ORDER BY searched_at DESC
                    LIMIT :limit
                    """
                ),
                {"user_id": user_id, "limit": limit},
            )
            .mappings()
            .all()
        )
        seen: set[str] = set()
        recent_queries: list[str] = []
        for row in rows:
            query = str(row["query"]).strip()
            normalized_query = query.lower()
            if not query or normalized_query in seen:
                continue
            seen.add(normalized_query)
            recent_queries.append(query)
        return recent_queries
