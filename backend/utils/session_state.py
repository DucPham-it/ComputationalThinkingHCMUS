from datetime import datetime
import streamlit as st


def init_session_state() -> None:
    """
    Khởi tạo các biến cần thiết trong session_state.
    Chỉ set nếu chưa tồn tại (tránh overwrite dữ liệu runtime).
    """

    defaults = {
        # =========================
        # SEARCH
        # =========================
        "search_form": {
            "location": "Quận 1, TP.HCM",
            "category": "Tất cả",
            "budget": "Tất cả",
            "time_slot": "Tối",
            "radius": 5,
        },

        # =========================
        # DATA FROM API
        # =========================
        "recommendations": [],          # danh sách place từ Places API
        "resolved_location": None,      # kết quả geocoding
        "selected_place": None,         # place đang chọn
        "route": None,                  # dữ liệu directions

        # =========================
        # LOCAL DATA (REVIEW)
        # =========================
        "reviews": [],                 # review local (chưa nối DB)
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =========================
# HELPER FUNCTIONS
# =========================

def rating_stars(rating: int | float | None) -> str:
    """
    Convert rating -> string sao
    """
    if rating is None:
        return "Chưa có đánh giá"

    try:
        full = int(round(float(rating)))
        full = max(0, min(full, 5))
        return "⭐" * full
    except Exception:
        return "N/A"


def now_string() -> str:
    """
    Lấy thời gian hiện tại dạng string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def reset_search_results() -> None:
    """
    Reset kết quả tìm kiếm (dùng khi đổi filter)
    """
    st.session_state["recommendations"] = []
    st.session_state["resolved_location"] = None


def clear_selected_place() -> None:
    """
    Xoá place đang chọn
    """
    st.session_state["selected_place"] = None
    st.session_state["route"] = None