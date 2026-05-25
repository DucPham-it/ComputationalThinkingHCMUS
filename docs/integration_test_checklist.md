# Bảng Kiểm Thử Tích Hợp (Integration Test Checklist) - Turn-by-Turn Navigation

Tài liệu này hướng dẫn cách kiểm thử tích hợp cho tính năng Dẫn đường chi tiết (Turn-by-Turn Navigation) do nhóm phát triển (tập trung vào công việc của Người 6 & Người 7).

---

## 1. Chuẩn Bị Môi Trường (Setup)
1. Khởi động backend API server:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```
2. Khởi động frontend client:
   ```bash
   cd frontend
   npm run dev
   ```
3. Đăng nhập và hoàn thiện thông tin tài khoản (Profile) để có quyền sử dụng chức năng Dẫn đường (Route planner).

---

## 2. Các Kịch Bản Kiểm Thử (Test Cases)

### Kịch Bản 1: Luồng Dẫn Đường Bình Thường (Normal Navigation Flow)
* **Mục tiêu**: Đảm bảo GPS cập nhật liên tục, tự động chuyển step, hiển thị đúng chỉ dẫn và thời gian/khoảng cách đếm ngược.
* **Các bước thực hiện**:
  1. Truy cập trang Route Planner (`/route`).
  2. Chọn điểm xuất phát (Use GPS hoặc Pick on map) và điểm đích.
  3. Nhấp nút **Find Shortest Route** để lấy tuyến đường từ backend.
  4. Nhấp nút **Bắt đầu dẫn đường (Turn-by-Turn)**.
* **Kết quả kỳ vọng**:
  * [ ] Giao diện chuyển sang chế độ full-screen navigation overlay.
  * [ ] Biểu tượng vị trí người dùng (`UserPositionMarker`) hiển thị với vòng tròn độ chính xác màu xanh dương và hiệu ứng sóng pulse.
  * [ ] Bảng điều khiển `NavigationPanel` hiển thị ở trên bản đồ với thông tin chỉ dẫn rẽ, khoảng cách đến cua rẽ tiếp theo, tổng quãng đường/thời gian còn lại và thanh tiến trình (progress bar).
  * [ ] Bản đồ tự động căn chỉnh và dịch chuyển (`setView`) theo tọa độ GPS của người dùng (`followPosition`).
  * [ ] Có tiếng Việt phát ra hướng dẫn chỉ đường qua giọng nói (TTS).

---

### Kịch Bản 2: Đi Chệch Hướng & Tự Động Tính Lại Đường (Off-Route & Auto Rerouting)
* **Mục tiêu**: Đảm bảo hệ thống phát hiện chính xác khi người dùng đi lệch lộ trình và tính toán lại đường đi một cách thông minh mà không gây đơ/treo ứng dụng.
* **Các bước thực hiện**:
  1. Trong chế độ Dẫn đường đang hoạt động, mô phỏng vị trí GPS mới nằm ngoài lộ trình đã chọn (khoảng cách > 50 mét so với tất cả các đoạn thẳng của lộ trình, duy trì trong ≥ 5 giây).
* **Kết quả kỳ vọng**:
  * [ ] Hệ thống chuyển trạng thái sang `OFF_ROUTE`.
  * [ ] Tiếng nói cảnh báo đi sai đường hoặc tự động gọi API lấy route mới.
  * [ ] Một yêu cầu reroute (`handleReroute`) được kích hoạt tự động lên backend để tìm lộ trình mới từ vị trí hiện tại đến đích cũ.
  * [ ] Rerouting được giới hạn tần suất (throttle) tối thiểu cách nhau 10 giây để tránh spam API của server.
  * [ ] Khi nhận được route mới từ backend, bản đồ cập nhật lại đường đi và bộ điều khiển (`useNavigationController`) tự động đặt lại lộ trình của Engine để tiếp tục dẫn đường mượt mà.

---

### Kịch Bản 3: Điều Khiển Âm Thanh & Cơ Chế Dự Phòng (Voice Toggle & TTS Fallback)
* **Mục tiêu**: Kiểm tra nút bật/tắt tiếng nói và khả năng tự động fallback khi API TTS backend gặp lỗi hoặc bị chặn autoplay.
* **Các bước thực hiện**:
  1. Bắt đầu dẫn đường, bấm nút biểu tượng Loa ở góc dưới để tắt âm thanh (`voiceEnabled` = false).
  2. Mô phỏng di chuyển sang step tiếp theo.
  3. Bật lại loa và mô phỏng lỗi kết nối tới API `/api/v1/tts` (ví dụ: ngắt kết nối mạng hoặc tắt API TTS).
* **Kết quả kỳ vọng**:
  * [ ] Khi tắt loa: Không có bất kỳ âm thanh chỉ dẫn nào phát ra.
  * [ ] Khi bật loa: Có âm thanh phát ra mỗi khi người dùng chuẩn bị tới khúc cua tiếp theo.
  * [ ] Khi backend TTS lỗi hoặc trình duyệt chặn autoplay: Hệ thống bắt được Exception và kích hoạt fallback sang thư viện Web Speech Synthesis của trình duyệt để tiếp tục đọc chỉ dẫn bằng tiếng Việt (giọng `vi-VN`).

---

### Kịch Bản 4: Đến Đích An Toàn (Arrival Behavior)
* **Mục tiêu**: Kiểm tra phản hồi của hệ thống khi người dùng đã đến điểm đích.
* **Các bước thực hiện**:
  1. Di chuyển tọa độ GPS đến gần điểm đích cuối cùng (khoảng cách < 30 mét).
* **Kết quả kỳ vọng**:
  * [ ] Navigation Engine chuyển sang trạng thái `ARRIVED`.
  * [ ] Bộ theo dõi GPS dừng định vị để tiết kiệm pin (`stopTracking`).
  * [ ] Ứng dụng hiển thị thông báo chúc mừng: *"Chúc mừng! Bạn đã đến đích an toàn."*
  * [ ] Phát âm thanh thông báo qua giọng nói: *"Bạn đã đến nơi"*.

---

### Kịch Bản 5: Tương Thích Ngược & Kết Thúc Hành Trình (Backward Compatibility & End Navigation)
* **Mục tiêu**: Đảm bảo chế độ lập kế hoạch tĩnh (static route planner) hoạt động bình thường và nút kết thúc hoạt động tốt.
* **Các bước thực hiện**:
  1. Ở màn hình tĩnh, kiểm tra việc hiển thị bản đồ, marker và danh sách chỉ dẫn dạng danh sách tĩnh.
  2. Bắt đầu dẫn đường, sau đó bấm nút **Kết thúc** màu đỏ trên thanh điều hướng dưới.
* **Kết quả kỳ vọng**:
  * [ ] Chế độ lập kế hoạch tĩnh không bị ảnh hưởng bởi code dẫn đường mới (bản đồ, danh sách địa điểm gợi ý hoạt động trơn tru).
  * [ ] Khi bấm nút **Kết thúc**:
    * Chế độ full-screen navigation đóng lại ngay lập tức.
    * GPS dừng theo dõi, giọng nói bị hủy.
    * Bản đồ và giao diện trả về trạng thái tĩnh ban đầu.
