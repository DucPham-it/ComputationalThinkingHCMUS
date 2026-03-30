import streamlit as st

place = st.session_state.get("selected_place")

st.title("🗺️ Map View")

if not place:
    st.warning("Chưa có địa điểm được chọn.")
else:
    st.subheader(f"Bản đồ địa điểm: {place['name']}")
    st.info("Trang này đang dùng placeholder. Dữ liệu tọa độ đã lấy từ API và có thể nối bản đồ thật sau.")

    st.markdown(
        f"""
        <div style="
            height:420px;
            border-radius:12px;
            background:#e9eef6;
            display:flex;
            align-items:center;
            justify-content:center;
            color:#333;
            font-size:20px;
            font-weight:600;
            text-align:center;
        ">
            Map Placeholder<br/>
            {place.get('name', '')}<br/>
            ({place.get('lat', 'N/A')}, {place.get('lng', 'N/A')})
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.button("⬅️ Quay lại chi tiết"):
    st.switch_page("pages/place_detail.py")