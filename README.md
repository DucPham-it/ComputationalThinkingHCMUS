# ComputationalThinkingHCMUS

Travel recommendation system built for learning Computational Thinking and full-stack project structure.

This project combines a `FastAPI` backend with a `React + Vite` frontend and uses Supabase as the source of truth for places, reviews, favorites, and recommendations. OpenStreetMap/Nominatim/OSRM handle map lookup and routing; Google Places is no longer part of the runtime flow.

## Mục tiêu

- Học cách thiết kế và triển khai ứng dụng web đầy đủ (frontend + backend)
- Tìm hiểu cách thiết kế hệ thống gợi ý dựa trên dữ liệu Supabase và bản đồ OSM
- Xây dựng hệ thống gợi ý du lịch và tìm đường đi
- Quản lý người dùng, đánh giá, và yêu thích địa điểm
- Áp dụng tư duy tính toán vào giải bài toán thực tế

## Kiến trúc dự án

- `backend/`: API server với `FastAPI`
  - `app/main.py`: điểm vào của ứng dụng backend
  - `app/core/config.py`: cấu hình môi trường
  - `app/api/routes/`: các endpoint API cho auth, places, reviews, favorites, recommendations, routes, weather, place requests, admin
  - `app/services/`: logic tìm kiếm địa điểm từ database, geocoding/routing OSM và weather
  - `backend/requirements.txt`: các dependency Python
- `split_places_csv.py`: script chạy thủ công ở root để tách CSV thô thành nhiều CSV theo bảng Supabase mới
- `supabase_schema_reference.sql`: SQL tham chiếu để tạo bảng trên Supabase thủ công, không phải migration

- `frontend/`: giao diện người dùng với `React` và `Vite`
  - `frontend/package.json`: script và dependency frontend
  - `frontend/src/`: component, page, context, service và route
  - `frontend/src/services/api.js`: kết nối tới backend API
  - `frontend/src/components/map/MapContainer.jsx`: tích hợp Leaflet + OpenStreetMap

## Cách chạy

### 1. Backend

1. Vào thư mục `backend`:

```bash
cd backend
```

2. Tạo và kích hoạt virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Cài dependency:

```bash
pip install -r requirements.txt
```

4. Chuẩn bị biến môi trường (hoặc tạo file `backend/.env`):

```bash
DATABASE_URL=postgresql://...
DATABASE_SSL_REQUIRE=false
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_STORAGE_AVATAR_BUCKET=avatars
SUPABASE_STORAGE_PLACE_BUCKET=place-images
SUPABASE_STORAGE_REVIEW_BUCKET=review-images
NOMINATIM_BASE_URL=https://nominatim.openstreetmap.org
OSRM_BASE_URL=https://router.project-osrm.org
WEATHER_API_KEY=
JWT_SECRET=your_jwt_secret
```

5. Chạy server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend mặc định sẽ chạy tại `http://localhost:8000`

### 2. Frontend

1. Vào thư mục `frontend`:

```bash
cd frontend
```

2. Cài dependency:

```bash
npm install
```

3. Nếu cần cấu hình URL backend, tạo file `.env` trong `frontend`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
```

4. Chạy frontend:

```bash
npm run dev
```

Frontend mặc định sẽ chạy tại `http://localhost:5173`

## Luồng hoạt động

- Frontend gọi API backend tại `http://localhost:8000/api/v1/...`
- Backend xử lý NLP nội bộ trước, tìm trực tiếp trong Supabase, dùng OSM/Nominatim để geocode/reverse geocode và OSRM để dựng route
- Người dùng có thể đăng ký/đăng nhập, thêm đánh giá, lưu yêu thích và xem gợi ý du lịch
- Người dùng có thể đề xuất thêm/sửa/xóa địa điểm từ bản đồ; admin đã được duyệt có thể approve/reject trong `/admin`
- Gợi ý trả top 10 địa điểm theo ngôn ngữ tự nhiên, filter, lịch sử pick/favorite/search; mỗi user giữ tối đa 80 lịch sử tìm kiếm.

## Kiểm tra nhanh

- Backend health: `http://localhost:8000/health`
