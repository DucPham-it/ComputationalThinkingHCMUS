# Fix Solving - Map Pick Feature

## Vấn đề
- **Nhảy tên / Nhảy điểm:** Khi click vào một điểm trên bản đồ, điểm bị "hút" (snap) sang một địa điểm có sẵn trong database thay vì ở ngay tọa độ vừa click.
- **Không hiện tên / Lỗi:** Khi hệ thống OpenStreetMap bị lỗi mạng hoặc không trả về dữ liệu tại tọa độ click, màn hình không hiển thị tên điểm (lỗi 404 từ backend).

## Những thay đổi đã thực hiện

### 1. Backend
- **File đã sửa:** `backend/app/services/place_search_service.py`
- **Chi tiết thay đổi:**
  - Xóa bỏ việc sử dụng `PlaceRepository(db).find_nearest_place` trong hàm `resolve_place_from_coordinates` để tắt cơ chế tự động "hút" điểm. Từ nay, điểm sẽ nằm đúng vị trí tọa độ click.
  - Thêm cơ chế Fallback: Nếu API `reverse_geocode_coordinates` (OpenStreetMap) trả về `None`, thay vì gây lỗi rỗng, hệ thống sẽ trả về một object địa điểm mặc định với tên `"Điểm đã chọn"` và giữ nguyên tọa độ gốc.

### 2. Frontend
- **File đã sửa:** `frontend/src/services/mapPickService.js`
- **Chi tiết thay đổi:**
  - Bao bọc toàn bộ code gọi API `api.post("/places/resolve-point")` vào trong khối `try...catch` ở hàm `resolvePlaceFromCoordinates`.
  - Trong trường hợp API backend bị lỗi (500, 404, hoặc đứt kết nối), hàm sẽ chủ động catch lỗi và trả về một điểm giả định mang tên `"Điểm tùy chọn"` để bản đồ vẫn có thể vẽ ra một marker hợp lệ và không làm hỏng trải nghiệm người dùng.

# Fix Solving - Search & NLP Feature

## Vấn đề
- **Tìm kiếm thiếu chính xác:** Bộ máy phân tích ngôn ngữ tự nhiên (NLP) cũ dựa trên luật (Rule-based) và TF-IDF chưa xử lý tốt các câu phức tạp tiếng Việt.
- **Không tìm thấy địa điểm ngoài Database:** Khi người dùng tìm một địa danh cụ thể (ví dụ: "Núi Bà Rá") chưa có sẵn trong cơ sở dữ liệu Supabase, hệ thống trả về rỗng thay vì hiển thị lên bản đồ.

## Những thay đổi đã thực hiện

### 1. Tích hợp Trí tuệ Nhân tạo (Gemini AI)
- **File đã tạo/sửa:** `backend/app/services/gemini_service.py`, `backend/app/recommendation/nlp_parser.py`, `backend/app/core/config.py`, `backend/.env`
- **Chi tiết thay đổi:**
  - Cài đặt thư viện `google-generativeai` và cấu hình biến môi trường `GEMINI_API_KEY`.
  - Tạo service `gemini_service.py` để gửi câu hỏi của người dùng lên LLM `gemini-1.5-flash`, yêu cầu trả về chuẩn dữ liệu JSON bóc tách chi tiết: mục đích (intent), loại hình (entertainment_type), ngân sách, đối tượng, và từ khóa phụ.
  - Sửa hàm `parse_recommendation_language_contract` trong `nlp_parser.py` để sử dụng Gemini làm bộ não phân tích chính, tự động lùi về (fallback) dùng bộ máy cũ nếu API lỗi.

### 2. Tìm kiếm Toàn cầu (External Map Fallback)
- **File đã sửa:** `backend/app/services/geocoding_service.py`, `backend/app/services/place_search_service.py`
- **Chi tiết thay đổi:**
  - Thêm hàm `search_external_place` vào `geocoding_service.py` sử dụng Nominatim API của OpenStreetMap để tìm kiếm văn bản địa danh (Text Search) trên toàn cầu.
  - Cập nhật hàm `search_places` trong `place_search_service.py`: Khi thuật toán truy vấn local database trả về 0 kết quả, tự động gọi sang `search_external_place` để lấy các tọa độ và tên từ OSM, đóng gói thành đối tượng Place giả lập.
  - Nhờ đó, người dùng có thể gõ bất kỳ địa danh, ngọn núi, dòng sông nào cũng có thể hiện ra kết quả để chọn làm điểm đến.

# Fix Solving - Routing Feature

## Vấn đề
- **Đi đường tắt qua quốc gia khác:** Khi tìm đường đi khoảng cách rất xa giữa hai miền Nam - Bắc Việt Nam (VD: TP.Hồ Chí Minh - Hà Nội), thuật toán tìm đường ngắn nhất của OSRM (Open Source Routing Machine) tính toán hình học thuần túy và thường vạch ra tuyến đường băng qua Lào hoặc Campuchia thay vì đi dọc theo quốc lộ 1A của Việt Nam.

## Những thay đổi đã thực hiện
- **File đã sửa:** `backend/app/services/routing_service.py`, `backend/app/services/geocoding_service.py`
- **Chi tiết thay đổi:**
  - Cập nhật các hàm Geocoding (`geocode_address`, `reverse_geocode_coordinates`) để lấy thêm thông tin mã quốc gia (`country_code`) từ OpenStreetMap.
  - Thêm logic kiểm tra vị trí quốc gia ở hàm `plan_route`:
    - **Cùng quốc gia (Việt Nam):** Vẫn giữ hàm Heuristic kiểm tra phân vùng Bắc - Nam. Tự động chèn tọa độ của **Đà Nẵng** (miền Trung) làm một "Trạm trung chuyển" (Waypoint) ngầm để ép thuật toán OSRM tìm đường đi men theo bờ biển, giữ nguyên lộ trình di chuyển 100% nằm trong lãnh thổ Việt Nam.
    - **Khác quốc gia (Quốc tế):** Nếu điểm xuất phát và điểm đến ở 2 quốc gia khác nhau, hệ thống tự động tìm kiếm sân bay quốc tế gần nhất thông qua hàm `search_external_place` dựa trên quốc gia xuất phát. Lộ trình sẽ được trỏ hướng tới sân bay đó và đổi tên điểm đến thành "Sân bay (tên sân bay) để bay sang nước khác".

# Fix Solving - API Optimization & Anti-Ban

## Vấn đề
- **Nguy cơ bị khóa IP từ OpenStreetMap:** Các tính năng Geocoding và Routing gọi API Nominatim quá nhiều lần cho một thao tác, dẫn đến rủi ro bị chặn IP do vi phạm luật giới hạn (Rate Limit) của nền tảng này.

## Những thay đổi đã thực hiện
- **File đã sửa:** `backend/app/services/geocoding_service.py`
- **Chi tiết thay đổi:**
  - **Thêm Caching (Bộ nhớ đệm) & Chống tràn RAM:** Lưu trữ kết quả trả về của các truy vấn địa lý trong 24 giờ để tránh gọi lại API. Để khắc phục lỗi Memory Leak (đầy RAM), hệ thống tự động xóa bộ nhớ đệm (clear cache) nếu số lượng phần tử lưu trữ vượt quá 500.
  - **Thêm Rate Limiting (Kiểm soát tần suất):** Đảm bảo khoảng cách giữa các lần gọi API luôn lớn hơn hoặc bằng 1.1 giây bằng hàm `time.sleep()`, tuân thủ tuyệt đối chính sách của OpenStreetMap. (Lưu ý: Đánh đổi lại là hệ thống sẽ xử lý chậm hơn nếu có nhiều người dùng truy cập cùng lúc).
  - **Cải tiến Bounding Box Heuristic:** Khai báo hàm `is_in_vietnam()` chia nhỏ bản đồ thành 3 khung chữ nhật nhỏ bám sát hình chữ S (Bắc, Trung, Nam) thay vì 1 khung lớn. Cách này giúp loại trừ tối đa sự nhầm lẫn với lãnh thổ của Lào, Campuchia và Biển Đông. Nếu tọa độ nằm trong 3 khung này, hệ thống bỏ qua API và tự động gán mã quốc gia là `"vn"`.
