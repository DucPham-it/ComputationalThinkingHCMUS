import streamlit as st
from pathlib import Path
from utils.session_state import init_session_state


def load_css() -> None:
    css_path = Path("assets/style.css")
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(
    page_title="Travel App",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
init_session_state()

st.title("📍 Travel Recommendation App")
st.subheader("Hệ thống gợi ý địa điểm vui chơi")

st.markdown(
    """
    Chọn trang ở sidebar để trải nghiệm giao diện:

    - **Home**: tìm kiếm và xem danh sách gợi ý
    - **Place Detail**: xem chi tiết địa điểm
    - **Map View**: xem bản đồ
    - **Route View**: xem hướng dẫn đường đi
    - **Review**: xem và gửi đánh giá
    """
)

st.info("Đây là phiên bản frontend demo bằng Streamlit. Backend và API thật có thể nối sau.")