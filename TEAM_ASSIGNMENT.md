# PHÂN CÔNG CÔNG VIỆC PROJECT
Hệ thống gợi ý địa điểm vui chơi giải trí (Smart Travel Recommendation)


# 1. NGUYÊN TẮC LÀM VIỆC

- Mỗi thành viên phụ trách một module riêng
- Không sửa code của người khác
- Giao tiếp thông qua interface rõ ràng:
  - Frontend ↔ Backend: API (JSON)
  - Backend ↔ AI: function
  - Backend ↔ Database: repository
- Mỗi người làm độc lập, giảm conflict


# 2. FRONTEND

## FE1 — UI System + Home (Design Owner)

Phụ trách:
- Toàn bộ design system
- Trang Home:
  - Search
  - Filter
  - Recommendation list

Scope:
frontend/src/
├── assets/styles/
├── components/common/
├── pages/Home.jsx

Deliver:
- Button, Card, Input chuẩn
- UI đồng nhất toàn app


## FE2 — Place Detail + Review

Phụ trách:
- Trang chi tiết địa điểm
- Review, Rating, Favorite UI

Scope:
pages/PlaceDetail.jsx
pages/ReviewPage.jsx
components/review/


## FE3 — Map + Route

Phụ trách:
- Google Maps UI
- Hiển thị route
- Directions

Scope:
pages/MapView.jsx
pages/RouteView.jsx
components/map/


# 3. BACKEND

## BE1 — Places API (Core Business API)

Phụ trách:
- API chính:
  - /places
  - /place/{id}
  - /search

Scope:
api/routes/places.py
schemas/place_schema.py


## BE2 — User + Review + Favorite

Phụ trách:
- User
- Review
- Favorite

Scope:
api/routes/reviews.py
api/routes/favorites.py
repositories/
models/


## BE3 — External APIs (Google + Weather)

Phụ trách:
- Google Maps Platform:
  - Places API
  - Directions API
  - Geocoding API
- Weather API

Scope:
services/google_places_service.py
services/directions_service.py
services/geocoding_service.py
services/weather_service.py


# 4. AI — RECOMMENDATION ENGINE:

## AI1 — Recommendation System

Phụ trách:
- Parse input user (NLP)
- Filter + Ranking
- Logic gợi ý

Scope:
recommendation/
├── recommender.py
├── ranking.py
├── filters.py
├── nlp_parser.py


# 5. INTEGRATION + QA

## INT1 — Integration + Testing

Phụ trách:
- Kết nối frontend và backend
- Test toàn bộ hệ thống
- Viết test case
- Fix bug integration

Scope:
tests/
postman/
README.md


# 6. LUỒNG GIAO TIẾP HỆ THỐNG

Frontend ↔ Backend:
- Giao tiếp qua API JSON

Ví dụ:
GET /recommend?lat=...&lng=...&type=restaurant


Backend ↔ AI:
- Gọi function nội bộ

Ví dụ:
recommend_places(user_input)


Backend ↔ Database:
- Thông qua repository

Ví dụ:
place_repo.get_places()
review_repo.add_review()


# 7. LUỒNG HOẠT ĐỘNG CHÍNH

User Input (Frontend)
    ↓
Backend API
    ↓
AI Recommendation
    ↓
External APIs (Google + Weather)
    ↓
Database (Review, Favorite)
    ↓
Return Result → Frontend


# 8. OUTPUT HỆ THỐNG

Danh sách gợi ý:
- Tên địa điểm
- Loại hình
- Địa chỉ
- Khoảng cách
- Rating
- Giá
- Trạng thái mở cửa
- Ảnh


Chi tiết địa điểm:
- Tên
- Địa chỉ
- Mô tả
- Rating
- Review
- Ảnh
- Giờ mở cửa
- Giá
- Liên hệ


Chỉ đường:
- Điểm bắt đầu
- Điểm đích
- Quãng đường
- Thời gian
- Tuyến đường
- Các bước chỉ dẫn


# 9. GHI CHÚ QUAN TRỌNG

- Không gọi Google API trực tiếp từ frontend
- API key đặt ở backend
- AI phải tích hợp vào pipeline
- UI phải thống nhất theo design system
