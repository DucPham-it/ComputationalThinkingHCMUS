# ComputationalThinkingHCMUS

Travel recommendation system built for learning Computational Thinking and full-stack project structure.

This project combines a `FastAPI` backend with a `React + Vite` frontend and uses Google Maps / Google Places to power location search, route planning, weather, reviews, and personalized recommendations.

## Mục tiêu

- Học cách thiết kế và triển khai ứng dụng web đầy đủ (frontend + backend)
- Tìm hiểu cách làm việc với API bên ngoài (Google Places, Directions, Weather)
- Xây dựng hệ thống gợi ý du lịch và tìm đường đi
- Quản lý người dùng, đánh giá, và yêu thích địa điểm
- Áp dụng tư duy tính toán vào giải bài toán thực tế

## Kiến trúc dự án

- `backend/`: API server với `FastAPI`
  - `app/main.py`: điểm vào của ứng dụng backend
  - `app/core/config.py`: cấu hình môi trường
  - `app/api/routes/`: các endpoint API cho auth, places, reviews, favorites, recommendations, routes, weather
  - `app/services/`: logic gọi Google API và xử lý dữ liệu
  - `backend/requirements.txt`: các dependency Python

- `frontend/`: giao diện người dùng với `React` và `Vite`
  - `frontend/package.json`: script và dependency frontend
  - `frontend/src/`: component, page, context, service và route
  - `frontend/src/services/api.js`: kết nối tới backend API
  - `frontend/src/components/map/MapContainer.jsx`: tích hợp Google Maps

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
DATABASE_URL=sqlite:///./dev.db
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
WEATHER_API_KEY=your_weather_api_key
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

3. Nếu cần cấu hình URL backend hoặc Google Maps key, tạo file `.env` trong `frontend`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_GOOGLE_MAPS_KEY=your_google_maps_key
```

4. Chạy frontend:

```bash
npm run dev
```

Frontend mặc định sẽ chạy tại `http://localhost:5173`

## Luồng hoạt động

- Frontend gọi API backend tại `http://localhost:8000/api/v1/...`
- Backend truy vấn Google Places API để tìm kiếm địa điểm, lấy chi tiết, định tuyến và thời tiết
- Người dùng có thể đăng ký/đăng nhập, thêm đánh giá, lưu yêu thích và xem gợi ý du lịch

## Kiểm tra nhanh

- Backend health: `http://localhost:8000/healt`

## Ghi chú
h
- Dự án dùng `DATABASE_URL` hoặc `SUPABASE_DB_URL` để cấu hình kết nối database
- Nếu không có database, backend có thể dùng SQLite theo `DATABASE_URL=sqlite:///./dev.db`
- Đảm bảo khóa API Google Maps và Weather hợp lệ để bản đồ và dữ liệu thời tiết hoạt động đúng
