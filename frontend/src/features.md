# Feature Input/Output And TODO Checklist

Tai lieu nay di theo mo hinh owner theo tinh nang. Frontend chi la mot phan trong tung tinh nang, khong tach thanh nhom rieng vi khoi luong FE nhe hon.

Quy uoc comment trong file/hàm:
- Dau file ghi `Owner`, `File input`, `File output`.
- Ham public/helper quan trong ghi `Owner`, `Input`, `Output`, va `TODO TVx` neu chua implement.
- Output khong chi la return value; neu ham update state, goi API, navigate, hay ghi database thi phai ghi ro side effect do.

## F1. Recommendation Request + Filter UI

Owner:
- TV1: Backend API + search history.
- TV2: Frontend search/filter/result.

Input chi tiet:
- `query`: cau ngon ngu tu nhien, co the rong.
- `filters` tu UI:
  - `entertainment_type`
  - `budget_level`
  - `companion_type`
  - `start_time`
  - `max_distance_km`
  - `require_open_now`
  - `min_rating`
  - `latitude`
  - `longitude`
- `user_id` tu auth token neu da dang nhap.

Output chi tiet:
- Frontend goi `GET /api/v1/recommendations` voi query params da chuan hoa.
- Backend tra:
  - `items`: toi da 10 dia diem.
  - Moi dia diem gom toi thieu `id`, `name`, `address`, `latitude`, `longitude`, `rating`, `review_count`, `thumbnail`, `score` neu co.
- Side effect:
  - Neu co query/filter co y nghia, luu search history.
  - Moi user giu toi da 80 lich su gan nhat.

TODO:
- TV1: hoan thien API contract va luu history filter-only.
- TV1: dam bao trim history ve 80 dong/user.
- TV2: implement `buildRecommendationFilterPayload`.
- TV2: gui query + filter payload tu Home.
- TV2: render loading, empty, error va top 10 result.

## F2. NLP Recommendation Fields

Owner:
- TV3.

Input chi tiet:
- Text user nhap, tieng Viet co dau/khong dau hoac keyword tieng Anh.
- Vi du:
  - `toi muon an re gan day toi nay`
  - `cafe yen tinh cho cap doi tren 4 sao`
  - `noi vui cho gia dinh dang mo cua trong 5km`

Output chi tiet:
- Parsed object:
  - `intent`
  - `entertainment_type`
  - `budget_level`
  - `companion_type`
  - `time_slot`
  - `location_hint`
  - `distance_hint_km`
  - `require_open_now`
  - `min_rating`
  - `keywords`
  - `confidence`
  - `missing_fields`

TODO:
- TV3: implement `parse_recommendation_language_contract`.
- TV3: implement `extract_filter_fields_from_text`.
- TV3: viet 20 cau mau va expected output.

## F3. Candidate Filtering

Owner:
- TV4.

Input chi tiet:
- `places`: candidate places tu database/search layer.
- `nlp_fields`: output cua F2.
- `ui_filters`: output tu F1 frontend.
- `user_location`: `latitude`, `longitude` neu co.

Output chi tiet:
- `filter_plan`: cac filter da hop nhat, UI uu tien hon NLP.
- `filtered_places`: danh sach dia diem sau loc.
- Moi place co the them:
  - `distance_km`
  - `filter_reasons`

TODO:
- TV4: implement `build_filter_plan`.
- TV4: implement budget, companion, rating, distance, open-now filters.
- TV4: dam bao filter thieu du lieu thi bo qua, khong crash.

## F4. Ranking And Personalization

Owner:
- TV5.

Input chi tiet:
- `filtered_places` tu F3.
- `user_context`:
  - `picked_places`
  - `recent_queries` toi da 80 dong
  - `favorite_places` neu co
  - `current_location` neu co
- `query_context`:
  - `raw_query`
  - `nlp_fields`
  - `ui_filters`

Output chi tiet:
- Top 10 places da sort theo score.
- Moi place nen co:
  - `score`
  - `score_parts`
  - `explanation`

TODO:
- TV5: implement random baseline scoring.
- TV5: implement pick-history scoring.
- TV5: implement search-history scoring.
- TV5: implement explanation ngan cho moi result.

## F5. Map Pick To Route

Owner:
- TV6.

Input chi tiet:
- Marker place:
  - `id`
  - `name`
  - `address`
  - `latitude`
  - `longitude`
  - `primary_type` hoac `category`
- Hoac map click tu do:
  - `latitude`
  - `longitude`
  - `label`
- Auth user neu co de record pick.

Output chi tiet:
- `AppContext.selectedPlace` co dang:
  - `place_id`
  - `name`
  - `address`
  - `latitude`
  - `longitude`
  - `source`
- Route page nhan destination va pre-fill route.
- Neu co `place_id`, goi `POST /api/v1/recommendations/picks/{place_id}`.

TODO:
- TV6: implement `buildRouteDestinationFromMapPick`.
- TV6: chuan hoa destination object dung chung map/route.
- TV6: xu ly pick marker, pick toa do tu do, doi destination.

## F6. Media Upload + Review Avatar

Owner:
- TV7.

Input chi tiet:
- Avatar file: jpeg/png/webp, user da dang nhap.
- Review image files: jpeg/png/webp.
- Place image files tu place request form.
- Review payload: `rating`, `content`, `image_urls`.

Output chi tiet:
- Upload response:
  - `url`
  - `path`
  - `bucket`
  - `content_type`
  - `size`
- Review list:
  - Hien avatar user.
  - Neu avatar rong/loi, fallback `avatars/default/default-avatar.jpg`.
- Review form:
  - Gui `image_urls` sau khi upload thanh cong.

TODO:
- TV7: hoan thien preview/remove anh review.
- TV7: hien loi file qua dung luong/sai dinh dang.
- TV7: dam bao fallback avatar la public Supabase URL.
