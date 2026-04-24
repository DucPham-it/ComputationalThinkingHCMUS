"""User search history repository.

Owner:
- TV1: Recommendation Request + Search History.

File input:
- Authenticated user id.
- Natural-language query or serialized filter-only query text.
- Optional latitude/longitude from browser GPS/profile geocode.

File output:
- Inserted user_search_history rows.
- Newest unique queries for ranking/personalization.
- Per-user history capped by settings.max_search_history_per_user, default 80.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings


class SearchHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def _trim_history(self, user_id: int) -> None:
        """Keep the newest search-history rows for one user.

        Input:
        - user_id: authenticated user id

        Output:
        - deletes older rows so each user has at most settings.max_search_history_per_user.
        - project requirement: default cap is 80.
        """
        max_items = max(1, int(settings.max_search_history_per_user))
        self.db.execute(
            text(
                """
                DELETE FROM user_search_history
                WHERE id IN (
                    SELECT id
                    FROM (
                        SELECT
                            id,
                            ROW_NUMBER() OVER (ORDER BY searched_at DESC, id DESC) AS item_rank
                        FROM user_search_history
                        WHERE user_id = :user_id
                    ) AS ranked_searches
                    WHERE item_rank > :max_items
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
        """Insert one search-history row and trim old rows.

        Owner:
        - TV1.

        Input:
        - user_id: authenticated user id.
        - query: non-empty normalized text to store. Can be raw query or
          filter-only text such as "budget_level:low min_rating:4".
        - latitude/longitude: optional user/map context at search time.

        Output:
        - no return value.
        - commits inserted row.
        - trims this user's history to max_search_history_per_user.
        """
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
        """Return newest unique search-history queries for one user.

        Owner:
        - TV1 provides the data.
        - TV5 consumes it for ranking.

        Input:
        - user_id: authenticated user id.
        - limit: maximum rows to read. Final personalization can request up to 80.

        Output:
        - list[str] of non-empty unique queries, newest first.
        """
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
