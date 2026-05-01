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

from fastapi import APIRouter, Depends
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
    max_distance_km: float | None = _DEFAULT_MAX_DISTANCE_KM,
    require_open_now: bool = False,
    min_rating: float | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> dict:
    """Recommendation list endpoint.

    Owner: TV1.

    Input:
    - query: natural-language search string từ SearchBar.
    - entertainment_type: "restaurant"|"cafe"|"museum"|"park"|"shopping"|"bar"
    - budget_level: "cheap"|"medium"|"premium"
    - companion_type: "solo"|"couple"|"family"|"friends"|"kids"
    - start_time: ISO datetime hoặc time slot do UI chuẩn hóa.
    - max_distance_km: bán kính tối đa tính từ vị trí hiện tại (default 5 km).
    - require_open_now: chỉ trả địa điểm đang mở cửa nếu True.
    - min_rating: điểm đánh giá tối thiểu, từ 0.0 đến 5.0.
    - latitude / longitude: GPS từ trình duyệt hoặc điểm trên bản đồ.
    - current_user: authenticated user đã hoàn chỉnh profile.
    - db: SQLAlchemy session.

    Output (200 OK):
    {
      "items": [
        {
          "id": 42,
          "name": "The Workshop Coffee",
          "address": "27 Ngô Đức Kế, Q.1",
          "latitude": 10.7769,
          "longitude": 106.7009,
          "primary_type": "cafe",
          "category": "cafe",
          "rating": 4.5,
          "review_count": 120,
          "photo_url": "https://...",
          "distance_km": 1.2,
          "open_now": true,
          "price_level": 2,
          "score": null,        // TODO TV5 (F4): điểm ranking
          "explanation": null   // TODO TV5 (F4): lý do gợi ý
        },
        ...  // tối đa 10 items
      ]
    }

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

    if history_query:
        SearchHistoryRepository(db).record_search(
            user_id=current_user["id"],
            query=history_query,
            latitude=effective_latitude,
            longitude=effective_longitude,
        )

    items = recommend_places(
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
        limit=10,
    )

    # TODO TV5 (F4): merge score + explanation vào mỗi item sau khi ranking hoàn chỉnh.
    # Các trường này đã có sẵn trong PlaceResponse schema (score: float | None = None).

    return {"items": items}
