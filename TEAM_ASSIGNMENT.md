# PHÂN CÔNG CÔNG VIỆC PROJECT

Smart Travel Recommendation - bản phân công cho 7 thành viên thực thi. Nhóm trưởng không nằm trong 7 người này.

## Vai Trò Nhóm Trưởng

Bạn là người connect, quản lý và test:
- Chốt API contract giữa các tính năng.
- Review tiến độ, gồm branch, merge code.
- Chạy test tích hợp và test nghiệm thu cuối.
- Không nhận một module thực thi riêng để tránh vừa làm vừa kiểm.

## Nguyên Tắc Chia Việc

- Chia theo tính năng trước, sau đó mới chia việc nhỏ trong tính năng.
- Một tính năng có thể có 1 hoặc 2 người phụ trách nếu cần FE + BE/AI.
- Frontend là phần nhẹ nên được ghép vào tính năng, không tách thành nhóm riêng.
- Mỗi hàm mới phải có docstring/comment ghi rõ Input, Output, TODO.
- Mỗi file trong scope phải có comment đầu file ghi Owner, File input, File output.
- Mỗi hàm public/helper quan trọng phải có comment/docstring ghi Owner, Input, Output.
- Mỗi API phải ghi rõ request input, response output, lỗi có thể trả về.
- Recommendation luôn trả tối đa top 10 địa điểm.
- Search history mỗi user lưu tối đa 80 dòng gần nhất.
- Thành viên chỉ sửa file trong scope của mình. Nếu cần đổi contract, báo nhóm trưởng chốt trước.

## Tong Quan Tinh Nang Va Owner

| Tính năng | Owner | Mục tiêu |
| --- | --- | --- |
| F1. Recommendation Request + Search History | TV1 + TV2 | Nhận ngôn ngữ tự nhiên/filter, gọi API, lưu lịch sử 80 dòng |
| F2. NLP Field Extraction | TV3 | Tách câu người dùng thành các trường filter có cấu trúc |
| F3. Candidate Filtering | TV4 | Lọc địa điểm theo query, filter, khoảng cách, rating, open now |
| F4. Ranking + Personalization | TV5 | Xếp hạng top 10 theo random baseline, pick history, search history |
| F5. Map Pick To Route | TV6 | Chọn địa điểm trên map thành điểm muốn đến ở route |
| F6. Media Upload + Review Avatar | TV7 | Upload avatar/review/place image, hiện avatar fallback |

---

## F1. Recommendation Request + Search History

Owner:
- TV1: Backend API, request contract, search history.
- TV2: Frontend search/filter/result wiring.

Mục tiêu:
- Người dùng có thể nhập ngôn ngữ tự nhiên, dùng filter, hoặc dùng cả hai.
- Frontend gửi đầy đủ request lên backend.
- Backend lưu lịch sử tìm kiếm của user, tối đa 80 dòng mỗi user.
- API trả về top 10 địa điểm phù hợp.

Scope TV1:
- `backend/app/api/routes/recommendations.py`
- `backend/app/repositories/search_history_repo.py`
- `backend/app/core/config.py`
- `backend/app/schemas/place_schema.py`

Scope TV2:
- `frontend/src/pages/Home.jsx`
- `frontend/src/components/recommendation/FilterPanel.jsx`
- `frontend/src/components/recommendation/RecommendationList.jsx`
- `frontend/src/services/placeService.js`

Input chi tiết:
- Từ frontend:
  - `query`: string, câu tự nhiên người dùng nhập. Có thể rỗng nếu chỉ dùng filter.
  - `entertainment_type`: string optional, ví dụ `restaurant`, `cafe`, `museum`, `park`, `shopping`, `bar`.
  - `budget_level`: string optional, ví dụ `cheap`, `medium`, `premium`.
  - `companion_type`: string optional, ví dụ `solo`, `couple`, `family`, `friends`, `kids`.
  - `start_time`: string optional, ISO datetime hoặc time slot do UI chuẩn hóa.
  - `max_distance_km`: number optional, khoảng cách tối đa tính từ tọa độ hiện tại.
  - `require_open_now`: boolean, chỉ lấy địa điểm đang mở cửa nếu `true`.
  - `min_rating`: number optional, từ 0 đến 5.
  - `latitude`: number optional, vĩ độ hiện tại của user.
  - `longitude`: number optional, kinh độ hiện tại của user.
- Từ auth:
  - `user_id`: string optional, lấy từ token nếu user đã đăng nhập.
- Từ repository:
  - `user_search_history`: tối đa 80 dòng gần nhất của user, dùng cho personalization ở F4.

Output chi tiết:
- Frontend gọi `GET /api/v1/recommendations` với query params đã chuẩn hóa.
- Backend response thành công:
  - `items`: array tối đa 10 địa điểm.
  - Mỗi item tối thiểu gồm:
    - `id`: place id.
    - `name`: tên địa điểm.
    - `address`: địa chỉ hiển thị.
    - `latitude`, `longitude`: tọa độ nếu có.
    - `primary_type` hoặc `category`: loại địa điểm.
    - `rating`: điểm trung bình nếu có.
    - `review_count`: số review nếu có.
    - `thumbnail` hoặc `image_url`: ảnh đại diện nếu có.
    - `score`: điểm ranking nếu F4 đã cung cấp.
    - `explanation`: lý do gợi ý nếu F4 đã cung cấp.
- Backend side effect:
  - Nếu request có `query` hoặc filter có ý nghĩa, lưu vào `user_search_history`.
  - Sau khi lưu, trim lịch sử của user về tối đa 80 dòng gần nhất.
- Frontend output:
  - Render danh sách top 10.
  - Hiển thị trạng thái loading, empty, error.
  - Khi click một địa điểm, có thể mở detail/map/route tùy flow hiện có.

Việc nhỏ TV1:
- Hoàn thiện `_build_history_query` để filter-only search vẫn tạo history để đọc.
- Viết hàm/logic trim history dùng `max_search_history_per_user = 80`.
- Đảm bảo API chấp nhận đầy đủ params và truyền tiếp sang recommender.
- Ghi rõ TODO cho các trường response chưa có như `score`, `explanation`.

Việc nhỏ TV2:
- Implement `buildRecommendationFilterPayload(formValues)`.
- Quản lý state query + filter trong `Home`.
- Khi submit, gửi cả query và filter payload qua `fetchRecommendations`.
- Render top 10 và xử lý loading/empty/error.

Bàn giao cho nhóm trưởng:
- TV1: API contract mẫu, ví dụ request/response, danh sách file đã sửa.
- TV2: Màn hình demo với 3 case: chỉ query, chỉ filter, query + filter.

---

## F2. NLP Field Extraction

Owner:
- TV3.

Mục tiêu:
- Phân tích câu tự nhiên thành các trường filter có cấu trúc để F3/F4 sử dụng.
- Hỗ trợ tiếng Việt có dấu, không dấu và một số từ khóa tiếng Anh phổ biến.

Scope:
- `backend/app/recommendation/nlp_parser.py`
- Test liên quan trong `backend/app/tests/`

Input chi tiết:
- `query`: string bất kỳ do user nhập.
  - Ví dụ: `tôi muốn ăn rẻ gần đây tối nay`
  - Ví dụ: `quán cafe yên tĩnh cho cặp đôi gần đây`
  - Ví dụ: `gợi ý nơi đi với gia đình, trên 4 sao, đang mở cửa`
- Từ điển/keyword nội bộ:
  - Nhóm loại hình: ăn uống, cafe, giải trí, công viên, mua sắm, bảo tàng, bar.
  - Nhóm ngân sách: rẻ, bình dân, vừa tiền, cao cấp.
  - Nhóm đối tượng đi cùng: một mình, cặp đôi, gia đình, trẻ em, bạn bè.
  - Nhóm thời gian: sáng, trưa, chiều, tối, cuối tuần, ngày mai.
  - Nhóm khoảng cách: gần đây, trong 1km, trong 5km.
  - Nhóm yêu cầu trạng thái: đang mở cửa, mở cửa bây giờ.

Output chi tiết:
- Object/dict kết quả parse:
  - `intent`: string, ví dụ `recommend_place`, `find_food`, `find_activity`.
  - `entertainment_type`: string optional.
  - `budget_level`: string optional.
  - `companion_type`: string optional.
  - `time_slot`: string optional.
  - `location_hint`: string optional, phần text nói về vị trí nếu có.
  - `distance_hint_km`: number optional.
  - `require_open_now`: boolean.
  - `min_rating`: number optional.
  - `keywords`: array string, từ khóa còn lại để search text.
  - `confidence`: number từ 0 đến 1.
  - `missing_fields`: array string, những trường cần UI hỏi thêm nếu muốn.
- Không được throw lỗi với query rỗng/không hiểu; trả object rỗng có `confidence` thấp.

Việc nhỏ:
- Implement `parse_recommendation_language_contract(query)`.
- Implement `extract_filter_fields_from_text(query)`.
- Chuẩn hóa text: lowercase, bỏ dấu tiếng Việt, xóa khoảng trắng thừa.
- Viết ít nhất 20 câu mẫu và expected fields.
- Ghi TODO rõ cho phần sau này có thể thay rule-based bằng model NLP.

Bàn giao cho nhóm trưởng:
- Bảng 20 câu input và output parse kỳ vọng.
- File test parse pass.

---

## F3. Candidate Filtering

Owner:
- TV4.

Mục tiêu:
- Nhận candidate places và filter đã hợp nhất, lọc ra danh sách địa điểm hợp lệ trước khi xếp hạng.
- Filter phải dùng được cho cả input từ NLP và input từ UI.

Scope:
- `backend/app/recommendation/filters.py`
- `backend/app/recommendation/recommender.py`
- Các repository đọc place nếu cần bổ sung field

Input chi tiết:
- `places`: array place dict/object từ database/search layer.
  - Trường có thể có: `id`, `name`, `address`, `latitude`, `longitude`, `primary_type`, `types`, `rating`, `review_count`, `price_level`, `opening_hours`, `open_now`, `thumbnail`.
- `nlp_fields`: dict output của F2.
- `ui_filters`: dict từ F1.
- `user_location`: object optional:
  - `latitude`: number.
  - `longitude`: number.
- Filter hợp nhất cần xử lý:
  - `entertainment_type`
  - `budget_level`
  - `companion_type`
  - `start_time` hoặc `time_slot`
  - `max_distance_km`
  - `require_open_now`
  - `min_rating`
  - `preferred_types`

Output chi tiết:
- `filter_plan`: dict đã hợp nhất:
  - UI filter ưu tiên hơn NLP nếu cùng một trường.
  - Có `source` cho mỗi field nếu làm được: `ui`, `nlp`, `default`.
- `filtered_places`: array place sau khi lọc.
- Mỗi place nên giữ nguyên các field ban đầu và có thể thêm:
  - `distance_km`: number optional nếu tính được.
  - `filter_reasons`: array string optional, lý do place phù hợp.
- Nếu filter không có dữ liệu để áp dụng thì bỏ qua filter đó, không làm crash.

Việc nhỏ:
- Implement `build_filter_plan(nlp_fields, ui_filters)`.
- Implement `apply_budget_filter(places, budget_level)`.
- Implement `apply_companion_filter(places, companion_type)`.
- Hoàn thiện filter rating, distance, open now, type.
- Đảm bảo output vẫn đủ để F4 ranking.

Bàn giao cho nhóm trưởng:
- 5 input filter mẫu và danh sách output mong đợi.
- Ghi rõ filter nào đã làm, filter nào còn TODO.

---

## F4. Ranking + Personalization

Owner:
- TV5.

Mục tiêu:
- Xếp hạng địa điểm và trả top 10.
- Nếu user chưa có dữ liệu, dùng random baseline có seed để kết quả không nhảy lung tung.
- Nếu có dữ liệu, ưu tiên theo địa điểm đã pick trước, sau đó theo search history và favorite/saved places nếu có.

Scope:
- `backend/app/recommendation/ranking.py`
- `backend/app/recommendation/recommender.py`
- Repository đọc picks/favorites/search history nếu cần

Input chi tiết:
- `filtered_places`: array place từ F3.
- `user_context`: dict optional:
  - `user_id`: string.
  - `picked_places`: array place/user_place_pick gần nhất.
  - `recent_queries`: array search history tối đa 80 dòng.
  - `favorite_places`: array optional.
  - `current_location`: `latitude`, `longitude` optional.
- `query_context`: dict:
  - `raw_query`: string.
  - `nlp_fields`: dict.
  - `ui_filters`: dict.

Output chi tiết:
- Array tối đa 10 place đã sort giảm dần theo score.
- Mỗi item nên có thêm:
  - `score`: number từ 0 đến 1 hoặc thang điểm nội bộ có ghi rõ.
  - `score_parts`: object optional:
    - `random_baseline`
    - `pick_history`
    - `search_history`
    - `favorite`
    - `distance`
    - `rating`
  - `explanation`: string ngắn, ví dụ `Gần các nơi bạn từng chọn và phù hợp cafe yên tĩnh`.
- Thứ tự fallback:
  - Không có user context: random baseline + rating/distance nếu có.
  - Có pick history: cộng điểm cho địa điểm cùng type/khu vực/gần pick gần đây.
  - Có search history: cộng điểm cho địa điểm khớp từ khóa/type user hay tìm.
  - Có favorite: cộng điểm nếu cùng category hoặc gần favorite.

Việc nhỏ:
- Implement `score_random_baseline(place, seed_text)`.
- Implement `score_from_user_pick_history(place, picked_places)`.
- Implement `score_from_search_history(place, recent_queries)`.
- Implement `explain_score(place)`.
- Đảm bảo `recommend_places(..., limit=10)` không trả quá 10 item.

Bàn giao cho nhóm trưởng:
- Mô tả công thức điểm ban đầu.
- 3 bộ demo: user mới, user có pick history, user có search history.

---

## F5. Map Pick To Route

Owner:
- TV6.

Mục tiêu:
- Người dùng pick một marker địa điểm trên map hoặc click tọa độ tự do.
- Địa điểm/tọa độ đó trở thành destination ở trang route.
- Nếu pick place có `place_id`, backend ghi nhận pick để F4 dùng cho personalization.

Scope:
- `frontend/src/pages/MapView.jsx`
- `frontend/src/pages/RouteView.jsx`
- `frontend/src/context/AppContext.jsx`
- `backend/app/repositories/pick_repo.py`
- `backend/app/api/routes/recommendations.py`

Input chi tiết:
- Từ map marker:
  - `id`: string/number optional, place id trong database.
  - `name`: string.
  - `address`: string optional.
  - `latitude`: number.
  - `longitude`: number.
  - `primary_type` hoặc `category`: string optional.
- Từ map click tự do:
  - `latitude`: number.
  - `longitude`: number.
  - `label`: string optional, mặc định có thể là `Custom destination`.
- Từ route:
  - `origin`: tọa độ hiện tại/user chọn.
  - `destination`: object từ marker/click.
- Từ auth:
  - `user_id`: string optional để record pick.

Output chi tiết:
- Frontend:
  - `AppContext.selectedPlace` được set với object route destination chuẩn hóa:
    - `place_id`: id nếu có.
    - `name`: tên hiển thị.
    - `address`: địa chỉ nếu có.
    - `latitude`, `longitude`.
    - `source`: `map_marker` hoặc `map_click`.
  - Điều hướng sang `/route`.
  - Route page pre-fill destination và hiển marker destination.
- Backend:
  - Nếu có `place_id`, gọi `POST /api/v1/recommendations/picks/{place_id}`.
  - Lưu/upsert `user_place_picks` với newest timestamp.
- Lỗi cần xử lý:
  - Marker thiếu tọa độ: hiển lỗi UI, không navigate.
  - User chưa đăng nhập: vẫn route được, chỉ bỏ qua record pick.

Việc nhỏ:
- Implement `buildRouteDestinationFromMapPick(place)`.
- Chuẩn hóa object destination dùng chung cho map và route.
- UI phân biệt đang chọn origin hay destination.
- Gọi record pick sau khi pick marker có `place_id`.

Bàn giao cho nhóm trưởng:
- Demo 3 case: pick marker, pick tọa độ tự do, đổi destination.
- Ghi rõ object destination output để các tính năng khác dùng.

---

## F6. Media Upload + Review Avatar

Owner:
- TV7.

Mục tiêu:
- Hoàn thiện upload ảnh lên Supabase Storage cho avatar user, ảnh địa điểm, ảnh review.
- Review/comment hiển avatar người dùng, nếu thiếu thì dùng `avatars/default/default-avatar.jpg`.

Scope:
- `backend/app/api/routes/uploads.py`
- `backend/app/services/upload_storage.py`
- `backend/app/schemas/upload_schema.py`
- `frontend/src/services/uploadService.js`
- `frontend/src/pages/Profile.jsx`
- `frontend/src/components/review/ReviewForm.jsx`
- `frontend/src/components/review/ReviewList.jsx`
- `frontend/src/components/map/PlaceRequestForm.jsx`

Input chi tiết:
- Avatar upload:
  - File field: `file`.
  - Loại file cho phép: `image/jpeg`, `image/png`, `image/webp`.
  - User đã đăng nhập để gán avatar vào profile.
- Review image upload:
  - File field: `files` hoặc nhiều file tùy API hiện có.
  - `place_id`: string/number nếu cần gán ảnh với review/place.
  - Review form fields: `rating`, `content`, `image_urls`.
- Place image upload:
  - File địa điểm từ form request tạo/cập nhật địa điểm.
- Storage config:
  - Bucket avatar: `avatars`.
  - Bucket place: `places`.
  - Bucket review: `reviews`.
  - Default avatar path: `avatars/default/default-avatar.jpg`.

Output chi tiết:
- Backend upload response:
  - `url`: public URL ảnh trên Supabase Storage.
  - `path`: storage path nội bộ.
  - `bucket`: bucket đã upload.
  - `content_type`: MIME type.
  - `size`: kích thước bytes.
- Frontend:
  - Profile avatar cập nhật URL mới sau upload.
  - Review form gửi `image_urls` trong payload tạo review.
  - Review list hiển avatar user bên trái comment/review.
  - Nếu `user.avatar_url` rỗng hoặc ảnh lỗi, fallback sang public URL của `avatars/default/default-avatar.jpg`.
- Lỗi cần xử lý:
  - File quá dung lượng.
  - Sai định dạng.
  - Supabase Storage lỗi/quyền bucket sai.

Việc nhỏ:
- Hoàn thiện preview/remove ảnh review trước khi submit.
- Hiển lỗi upload thân thiện trên UI.
- Đảm bảo default avatar dùng public URL từ Supabase.
- Kiểm tra mobile layout review/comment không vỡ.

Bàn giao cho nhóm trưởng:
- Demo upload avatar, upload review images, fallback avatar.
- Danh sách env/bucket cần cấu hình.

---

## Checklist Bàn Giao Chung

Mỗi thành viên khi gửi code cần kèm:
- File đã sửa.
- Hàm mới đã thêm và Owner/Input/Output của từng hàm.
- Comment đầu file đã cập nhật đúng owner và đúng tính năng.
- API request/response mẫu nếu có.
- Case đã tự test.
- Việc còn TODO nếu chưa xong hết.

## Chuẩn Comment Trong Code

Comment đầu file:
- Owner: TV nào phụ trách file.
- File input: dữ liệu đầu vào của file/module.
- File output: dữ liệu đầu ra hoặc side effect của file/module.

Comment trong hàm:
- Owner: TV nào phụ trách hàm.
- Input: tham số, state, request body/query params, hoặc props mà hàm nhận.
- Output: return value, response, state update, database side effect, navigation.
- TODO: việc cần implement tiếp, nếu hàm đang là khung rỗng.

Ví dụ ngắn:
```text
Owner:
- TV5.

Input:
- filtered_places: danh sách địa điểm đã lọc từ TV4.
- recent_queries: tối đa 80 lịch sử tìm kiếm gần nhất.

Output:
- top 10 địa điểm đã có score và explanation.

TODO TV5:
- Thêm score_parts và công thức điểm chi tiết.
```

Nhóm trưởng sẽ:
- Kiểm tra contract giữa F1-F6.
- Chạy backend tests và frontend build.
- Test flow cuối: nhập ngôn ngữ/filter -> top 10 -> pick trên map -> route -> history/personalization.
