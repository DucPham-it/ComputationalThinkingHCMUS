import re
import streamlit as st

from config.services.directions_service import get_directions


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def load_route() -> dict | None:
    place = st.session_state.get("selected_place")
    origin_info = st.session_state.get("resolved_location")

    if not place or not origin_info:
        return None

    origin = origin_info.get("formatted_address")
    destination = place.get("address")

    if not origin or not destination:
        return None

    try:
        route = get_directions(origin=origin, destination=destination, mode="driving")
    except Exception as e:
        st.error(f"Lỗi lấy dữ liệu chỉ đường: {e}")
        return None

    if route:
        route["steps"] = [strip_html(step) for step in route.get("steps", [])]
        st.session_state["route"] = route

    return route


place = st.session_state.get("selected_place")
route = load_route() or st.session_state.get("route")

st.title("🚗 Route View")

if not place:
    st.warning("Chưa chọn địa điểm.")
elif not route:
    st.warning("Không lấy được dữ liệu tuyến đường.")
else:
    st.subheader(f"Hướng dẫn đến: {place['name']}")

    left, right = st.columns([2, 1])

    with left:
        st.markdown("### Tuyến đường")
        st.info("Đã lấy khoảng cách và thời gian thật từ Directions API. Phần bản đồ tuyến đường có thể nối sau.")

        st.markdown(
            """
            <div style="
                height:360px;
                border-radius:12px;
                background:#eef3f8;
                display:flex;
                align-items:center;
                justify-content:center;
                color:#333;
                font-size:18px;
                font-weight:600;
            ">
                Route Placeholder
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("### Thông tin")
        st.write(f"**Điểm đi:** {route.get('start_address', 'Không rõ')}")
        st.write(f"**Điểm đến:** {route.get('end_address', 'Không rõ')}")
        st.write(f"**Quãng đường:** {route.get('distance', 'Không rõ')}")
        st.write(f"**Thời gian:** {route.get('duration', 'Không rõ')}")

    st.markdown("### Các bước chỉ đường")
    for i, step in enumerate(route.get("steps", []), start=1):
        st.write(f"{i}. {step}")

if st.button("⬅️ Quay lại chi tiết"):
    st.switch_page("pages/place_detail.py")