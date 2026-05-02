from math import asin, cos, radians, sin, sqrt
from typing import Any


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Ước lượng khoảng cách thực tế khách hàng phải di chuyển.
    # Việc tính toán nội bộ giúp hệ thống trả về kết quả gợi ý ngay lập tức, 
    # đảm bảo trải nghiệm mượt mà mà không phụ thuộc vào độ trễ của mạng.
    earth_radius_km = 6371.0

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    )
    c = 2 * asin(sqrt(a))
    
    return earth_radius_km * c


def get_distance_between_points(user_loc: dict[str, Any], place_loc: dict[str, Any]) -> float | None:
    # Cung cấp cự ly chính xác để hệ thống quyết định xem địa điểm có nằm trong phạm vi chịu đi của khách hay không.
    # Đặt tính an toàn lên hàng đầu: Âm thầm bỏ qua các tọa độ lỗi hoặc khuyết thiếu 
    # để luồng gợi ý chính luôn vận hành trơn tru, không bao giờ bị sập (crash).
    def try_parse_float(val: Any) -> float | None:
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    lat1 = try_parse_float(user_loc.get("latitude"))
    lon1 = try_parse_float(user_loc.get("longitude"))
    lat2 = try_parse_float(place_loc.get("latitude"))
    lon2 = try_parse_float(place_loc.get("longitude"))

    if None in (lat1, lon1, lat2, lon2):
        return None

    return haversine_km(lat1, lon1, lat2, lon2)