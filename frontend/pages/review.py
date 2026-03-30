import streamlit as st
from utils.session_state import rating_stars, now_string

place = st.session_state.get("selected_place")

st.title("💬 Review")

if not place:
    st.warning("Chưa chọn địa điểm.")
else:
    st.subheader(f"Đánh giá cho: {place['name']}")

    st.markdown("### Đánh giá nội bộ")
    for review in st.session_state.get("reviews", []):
        st.markdown('<div class="review-card">', unsafe_allow_html=True)
        st.write(f"**{review['user']}** - {rating_stars(review['rating'])}")
        st.write(review["comment"])
        st.caption(review["time"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Thêm đánh giá của bạn")

    with st.form("review_form"):
        user = st.text_input("Tên của bạn")
        rating = st.slider("Số sao", min_value=1, max_value=5, value=5)
        comment = st.text_area("Nội dung đánh giá")
        submitted = st.form_submit_button("Gửi đánh giá")

    if submitted:
        if not user.strip() or not comment.strip():
            st.error("Vui lòng nhập đầy đủ tên và nội dung đánh giá.")
        else:
            st.session_state["reviews"].insert(
                0,
                {
                    "user": user.strip(),
                    "rating": rating,
                    "comment": comment.strip(),
                    "time": now_string(),
                },
            )
            st.success("Đã gửi đánh giá thành công.")
            st.rerun()

if st.button("⬅️ Quay lại chi tiết"):
    st.switch_page("pages/place_detail.py")