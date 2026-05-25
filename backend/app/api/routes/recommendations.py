"""Recommendation API routes.

Owner:
- TV1: GET /recommendations request/response and search-history side effect.

File input:
- Query params from frontend recommendation search/filter UI.
- Authenticated user from dependency.

File output:
- Top 10 recommendation response for frontend.
- Persisted search history for personalization.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_completed_profile
from app.db.session import get_db
from app.recommendation.recommender import recommend_places
from app.repositories.search_history_repo import SearchHistoryRepository
from app.repositories.user_repo import UserRepository
from app.services.geocoding_service import geocode_address

router = APIRouter()

# Giá trị mặc định của max_distance_km khi frontend không gửi lên.
# Không lưu filter này vào history vì nó không phản ánh ý định tìm kiếm.
_DEFAULT_MAX_DISTANCE_KM = 5.0


def _build_history_query(query: str, filters: dict) -> str:
    """Build searchable history text từ natural-language input và filter-only searches.

    Owner: TV1.

    Input:
    - query: raw text typed by user. Can be empty.
    - filters: dict các filter values. Chỉ truyền max_distance_km vào đây
      khi user thực sự chọn (khác default), tránh lưu noise.

    Output:
    - compact text stored in user_search_history.query.
    - Trả về query gốc khi user có nhập text.
    - Trả về "key:value" pairs khi user chỉ dùng filter.
    - Trả về empty string khi không có gì có ý nghĩa để lưu.

    Examples:
    - query="quán cà phê yên tĩnh", filters={} -> "quán cà phê yên tĩnh"
    - query="", {"budget_level":"cheap","companion_type":"couple"}
      -> "budget_level:cheap companion_type:couple"
    - query="", filters={} -> ""
    """
    normalized_query = query.strip()
    if normalized_query:
        return normalized_query

    # Lọc bỏ None, chuỗi rỗng, và False để không lưu filter không có ý nghĩa
    meaningful_filters = {
        key: value
        for key, value in filters.items()
        if value not in (None, "", False)
    }
    filter_parts = [f"{key}:{value}" for key, value in meaningful_filters.items()]
    return " ".join(filter_parts)


@router.get("")
def get_recommendations(
    query: str = "",
    entertainment_type: str | None = None,
    budget_level: str | None = None,
    companion_type: str | None = None,
    start_time: str | None = None,
    max_distance_km: float | None = None,
    require_open_now: bool = False,
    min_rating: float | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    limit: int = Query(default=10, ge=1, le=30),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> dict:
    """Recommendation list endpoint.

    Owner: TV1.

        - query: natural-language search string from frontend
    - entertainment_type: explicit UI category filter, overrides NLP category
    - budget_level: low/medium/high filter
    - companion_type: solo/couple/family/friends preference
    - start_time: intended visit time or time slot
    - max_distance_km: optional maximum distance radius. When omitted, default
      suggestions are ranked from the full candidate set instead of being
      limited to 5km.
    - require_open_now: when true, only return currently-open candidates
    - min_rating: minimum rating 0..5
    - latitude/longitude: GPS or map context
    - limit: number of ranked places to return, default 10, max 30
    - offset: number of ranked places to skip for "load more"
    - current_user: authenticated user with completed profile
    - db: SQLAlchemy session

    Output:
    - {"items": ranked place dicts, "has_more", "next_offset", "limit", "offset"}.
    - Each item should be compatible with PlaceResponse/RecommendationList:
      id, name, address, latitude, longitude, rating, review_count,
      primary_type/category, photo_url/thumbnail, score, explanation if present.

    Side effects:
    - Lưu history khi có query text hoặc filter có ý nghĩa.
    - Trim lịch sử về tối đa settings.max_search_history_per_user (80) dòng.

    Future extension:
    - Thay GET params bằng POST RecommendationQuery khi filter UI hoàn chỉnh.
    - Bổ sung per-place ranking explanation từ F4 (TV5).
    """
    user = UserRepository(db).get_by_id(current_user["id"])
    effective_latitude = latitude
    effective_longitude = longitude

    # Fallback: nếu không có GPS từ frontend, geocode địa chỉ trong profile
    if (effective_latitude is None or effective_longitude is None) and user and user.address:
        geocoded_address = geocode_address(user.address, db=db)
        effective_latitude = geocoded_address.get("latitude")
        effective_longitude = geocoded_address.get("longitude")

    safe_limit = min(max(int(limit or 10), 1), 30)
    safe_offset = max(int(offset or 0), 0)

    # Chỉ đưa max_distance_km vào history khi user thực sự chọn (khác default)
    distance_for_history = (
        max_distance_km
        if max_distance_km is not None and max_distance_km != _DEFAULT_MAX_DISTANCE_KM
        else None
    )

    history_query = _build_history_query(
        query,
        {
            "entertainment_type": entertainment_type,
            "budget_level": budget_level,
            "companion_type": companion_type,
            "start_time": start_time,
            "max_distance_km": distance_for_history,
            "require_open_now": require_open_now,
            "min_rating": min_rating,
        },
    )
    if history_query and safe_offset == 0:
        SearchHistoryRepository(db).record_search(
            user_id=current_user["id"],
            query=history_query,
            latitude=effective_latitude,
            longitude=effective_longitude,
        )

    page_items = recommend_places(
        query=query,
        latitude=effective_latitude,
        longitude=effective_longitude,
        db=db,
        user_id=current_user["id"],
        user_address=user.address if user else None,
        entertainment_type=entertainment_type,
        budget_level=budget_level,
        companion_type=companion_type,
        start_time=start_time,
        max_distance_km=max_distance_km,
        require_open_now=require_open_now,
        min_rating=min_rating,
        limit=safe_limit + 1,
        offset=safe_offset,
    )
    items = page_items[:safe_limit]
    has_more = len(page_items) > safe_limit
    return {
        "items": items,
        "limit": safe_limit,
        "offset": safe_offset,
        "has_more": has_more,
        "next_offset": safe_offset + len(items) if has_more else None,
    }
