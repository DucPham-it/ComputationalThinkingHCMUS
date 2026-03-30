import streamlit as st

from config.services.places_service import get_place_details


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


def load_place_detail() -> dict | None:
    selected_place = st.session_state.get("selected_place")
    if not selected_place:
        st.warning("Chưa chọn địa điểm.")
        return None

    place_id = selected_place.get("google_place_id")
    if not place_id:
        st.warning("Địa điểm chưa có google_place_id.")
        return selected_place

    try:
        detail = get_place_details(place_id)
    except Exception as e:
        st.error(f"Lỗi lấy chi tiết địa điểm: {e}")
        return selected_place

    merged = {
        "id": selected_place.get("id"),
        "google_place_id": place_id,
        "name": detail.get("name", selected_place.get("name")),
        "category": ", ".join(detail.get("types", selected_place.get("types", []))),
        "address": detail.get("formatted_address", selected_place.get("address")),
        "rating": detail.get("rating", selected_place.get("rating")),
        "price_level": detail.get("price_level", selected_place.get("price_level")),
        "open_now": detail.get("opening_hours", {}).get("open_now", selected_place.get("open_now")),
        "distance_km": selected_place.get("distance_km"),
        "description": detail.get("editorial_summary", {}).get("overview", selected_place.get("description")),
        "lat": detail.get("geometry", {}).get("location", {}).get("lat", selected_place.get("lat")),
        "lng": detail.get("geometry", {}).get("location", {}).get("lng", selected_place.get("lng")),
        "phone": detail.get("formatted_phone_number"),
        "website": detail.get("website"),
        "user_ratings_total": detail.get("user_ratings_total"),
        "reviews_google": detail.get("reviews", []),
        "weekday_text": detail.get("opening_hours", {}).get("weekday_text", []),
    }

    st.session_state["selected_place"] = merged
    return merged


place = load_place_detail()

st.title("📌 Place Detail")

if place:
    st.subheader(place["name"])

    left, right = st.columns([2, 1])

    with left:
        st.write(f"**Loại hình:** {place.get('category', 'Đang cập nhật')}")
        st.write(f"**Địa chỉ:** {place.get('address', 'Đang cập nhật')}")
        st.write(f"**Mô tả:** {place.get('description', 'Chưa có mô tả')}")
        st.write(f"**Số điện thoại:** {place.get('phone', 'Không rõ')}")
        st.write(f"**Website:** {place.get('website', 'Không có')}")
        st.write(f"**Chi phí:** {format_price_level(place.get('price_level'))}")
        st.write(f"**Trạng thái:** {'Đang mở cửa' if place.get('open_now') else 'Không rõ'}")
        st.write(f"**Tọa độ:** ({place.get('lat', 'N/A')}, {place.get('lng', 'N/A')})")

        if place.get("weekday_text"):
            st.markdown("### Giờ mở cửa")
            for day in place["weekday_text"]:
                st.write(f"- {day}")

    with right:
        st.metric("Rating", f"{place.get('rating', 'N/A')}/5")
        st.metric("Total ratings", place.get("user_ratings_total", "N/A"))
        st.metric("Distance", f"{place.get('distance_km', 'N/A')} km")

    if place.get("reviews_google"):
        st.markdown("### Đánh giá từ Google")
        for review in place["reviews_google"][:5]:
            st.markdown('<div class="review-card">', unsafe_allow_html=True)
            st.write(f"**{review.get('author_name', 'Ẩn danh')}** - {review.get('rating', 'N/A')}/5")
            st.write(review.get("text", ""))
            st.markdown("</div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🗺️ Map", use_container_width=True):
        st.switch_page("pages/map_view.py")

with col2:
    if st.button("🚗 Route", use_container_width=True):
        st.switch_page("pages/route_view.py")

with col3:
    if st.button("💬 Review", use_container_width=True):
        st.switch_page("pages/review.py")

with col4:
    if st.button("⬅ Home", use_container_width=True):
        st.switch_page("pages/home.py")