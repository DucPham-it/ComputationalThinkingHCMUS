import streamlit as st

from config.services.geocoding_service import geocode_address
from config.services.places_service import nearby_search, text_search, normalize_place


CATEGORY_OPTIONS = {
    "Tất cả": None,
    "Địa điểm du lịch": "tourist_attraction",
    "Công viên": "park",
    "Bảo tàng": "museum",
    "Quán cà phê": "cafe",
    "Trung tâm mua sắm": "shopping_mall",
    "Nhà hàng": "restaurant",
}

BUDGET_OPTIONS = ["Tất cả", "Miễn phí", "Thấp", "Trung bình", "Cao"]
TIME_OPTIONS = ["Sáng", "Chiều", "Tối", "Cuối tuần"]


def format_price_level(price_level: int | None) -> str:
    if price_level is None:
        return "Không rõ"
    mapping = {
        0: "Miễn phí",
        1: "Thấp",
        2: "Trung bình",
        3: "Cao",
        4: "Rất cao",
    }
    return mapping.get(price_level, "Không rõ")


def price_match(selected_budget: str, place_price_level: int | None) -> bool:
    if selected_budget == "Tất cả":
        return True

    mapped = format_price_level(place_price_level)

    if selected_budget == "Cao":
        return mapped in ["Cao", "Rất cao"]

    return mapped == selected_budget


def render_place_card(place: dict) -> None:
    st.markdown('<div class="place-card">', unsafe_allow_html=True)
    st.markdown(f"### {place.get('name', 'Không có tên')}")
    st.write(f"**Loại:** {', '.join(place.get('types', [])) if place.get('types') else 'Không rõ'}")
    st.write(f"**Địa chỉ:** {place.get('address', 'Không rõ')}")
    st.write(f"**Đánh giá:** {place.get('rating', 'N/A')}/5")
    st.write(f"**Chi phí:** {format_price_level(place.get('price_level'))}")
    st.write(f"**Mở cửa:** {'Có' if place.get('open_now') else 'Không rõ'}")

    lat = place.get("lat")
    lng = place.get("lng")
    if lat is not None and lng is not None:
        st.caption(f"Tọa độ: ({lat}, {lng})")

    if st.button("Xem chi tiết", key=f"detail_{place.get('google_place_id', place.get('name', 'x'))}"):
        st.session_state["selected_place"] = place.copy()
        st.switch_page("pages/place_detail.py")

    st.markdown("</div>", unsafe_allow_html=True)


def search_places(location: str, category_label: str, radius_km: int) -> list[dict]:
    category_type = CATEGORY_OPTIONS[category_label]

    geo_result = geocode_address(location)
    if not geo_result:
        st.error(
            "Không tìm thấy địa điểm nhập vào. "
            "Hãy thử nhập rõ hơn, ví dụ: 'Quận 1, TP.HCM' hoặc 'Đà Nẵng'."
        )
    return []

    st.session_state["resolved_location"] = geo_result

    try:
        if category_type is None:
            query = f"địa điểm vui chơi gần {geo_result['formatted_address']}"
            raw_places = text_search(query)
        else:
            raw_places = nearby_search(
                lat=geo_result["lat"],
                lng=geo_result["lng"],
                radius=radius_km * 1000,
                place_type=category_type,
            )
    except Exception as e:
        st.error(f"Lỗi gọi Places API: {e}")
        return []

    return [normalize_place(place) for place in raw_places]


st.title("🏠 Home")
st.caption("Tìm kiếm và gợi ý địa điểm vui chơi")

current_form = st.session_state.get(
    "search_form",
    {
        "location": "Quận 1, TP.HCM",
        "category": "Tất cả",
        "budget": "Tất cả",
        "time_slot": "Tối",
        "radius": 5,
    },
)

with st.sidebar:
    st.header("Bộ lọc tìm kiếm")

    location = st.text_input("Địa điểm", value=current_form["location"])
    category = st.selectbox(
        "Loại hình",
        list(CATEGORY_OPTIONS.keys()),
        index=list(CATEGORY_OPTIONS.keys()).index(current_form["category"]),
    )
    budget = st.selectbox(
        "Ngân sách",
        BUDGET_OPTIONS,
        index=BUDGET_OPTIONS.index(current_form["budget"]),
    )
    time_slot = st.selectbox(
        "Thời gian",
        TIME_OPTIONS,
        index=TIME_OPTIONS.index(current_form["time_slot"]),
    )
    radius = st.slider("Bán kính tìm kiếm (km)", 1, 20, current_form["radius"])

    search_clicked = st.button("Tìm kiếm", use_container_width=True)

if search_clicked:
    st.session_state["search_form"] = {
        "location": location,
        "category": category,
        "budget": budget,
        "time_slot": time_slot,
        "radius": radius,
    }

    with st.spinner("Đang tìm địa điểm..."):
        places = search_places(location, category, radius)

    filtered_places = [
        place for place in places
        if price_match(budget, place.get("price_level"))
    ]

    st.session_state["recommendations"] = filtered_places

    if filtered_places:
        st.success(f"Tìm thấy {len(filtered_places)} địa điểm phù hợp.")
    else:
        st.warning("Không tìm thấy địa điểm phù hợp.")

st.subheader("Kết quả gợi ý")

recommendations = st.session_state.get("recommendations", [])
resolved_location = st.session_state.get("resolved_location")

if resolved_location:
    st.caption(f"Khu vực tìm kiếm: {resolved_location.get('formatted_address', '')}")

if not recommendations:
    st.info("Chưa có dữ liệu. Hãy nhập bộ lọc và nhấn Tìm kiếm.")
else:
    cols = st.columns(3)
    for idx, place in enumerate(recommendations):
        with cols[idx % 3]:
            render_place_card(place)