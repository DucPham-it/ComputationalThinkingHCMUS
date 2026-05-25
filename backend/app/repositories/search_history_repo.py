"""User search history repository.

Owner:
- TV1: Recommendation Request + Search History.

File input:
- Authenticated user id.
- Natural-language query hoặc serialized filter-only query text.
- Optional latitude/longitude từ GPS hoặc profile geocode.

File output:
- Inserted user_search_history rows.
- Newest unique queries cho ranking/personalization (dùng bởi F4/TV5).
- Per-user history được trim về settings.max_search_history_per_user (default 80).
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings


class SearchHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def _trim_history(self, user_id: int) -> None:
        """Giữ lại tối đa max_search_history_per_user dòng gần nhất của một user.

        Input:
        - user_id: authenticated user id.

        Output:
        - DELETE các dòng cũ vượt quá giới hạn.
        - Giới hạn mặc định là 80 (settings.max_search_history_per_user).
        - Nếu settings bị cấu hình sai (<=0), fallback về tối thiểu 1.

        SQL strategy: dùng ROW_NUMBER() OVER (ORDER BY searched_at DESC, id DESC)
        để xác định thứ tự từ mới nhất đến cũ nhất, sau đó DELETE tất cả
        những dòng có rank > max_items.
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
        """Insert một dòng search history và trim lịch sử cũ.

        Owner: TV1.

        Input:
        - user_id: authenticated user id.
        - query: non-empty normalized text. Có thể là raw query người dùng nhập
          hoặc filter-only text dạng "budget_level:cheap companion_type:couple".
        - latitude/longitude: vị trí của user tại thời điểm tìm kiếm (optional).

        Output:
        - Không trả giá trị.
        - Commit row mới vào DB.
        - Trim history của user về max_search_history_per_user (80).

        Note: Hàm này không dedup — việc lưu cùng một query nhiều lần là chủ ý,
        vì F4 dùng tần suất xuất hiện để tính mức độ quan tâm của user.
        list_recent_queries() sẽ dedup ở tầng đọc khi cần.
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
        """Trả về các query gần nhất, đã dedup, của một user.

        Owner:
        - TV1 cung cấp data.
        - TV5 (F4) consume để personalization ranking.

        Input:
        - user_id: authenticated user id.
        - limit: số dòng tối đa đọc từ DB. F4 có thể request đến 80.

        Output:
        - list[str] các query không trùng lặp, sắp xếp từ mới nhất đến cũ nhất.
        - Dedup theo lowercase để tránh đếm "Cafe" và "cafe" là hai query khác nhau.
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
