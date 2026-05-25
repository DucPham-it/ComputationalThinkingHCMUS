# F1 — Recommendation Request + Search History
## Tài liệu bàn giao nhóm trưởng

---

## TV1 — Backend

### Files đã sửa
| File | Thay đổi |
|------|----------|
| `backend/app/api/routes/recommendations.py` | Hoàn thiện `_build_history_query`, làm rõ logic trim, bổ sung docstring API contract, thêm TODO cho TV5 |
| `backend/app/repositories/search_history_repo.py` | Làm rõ toàn bộ docstring, giải thích SQL trim strategy, ghi chú dedup ở tầng đọc |

### API Contract

**Endpoint:** `GET /api/v1/recommendations`

**Query Params:**

| Param | Type | Required | Ví dụ |
|-------|------|----------|-------|
| `query` | string | No | `"cafe yên tĩnh gần đây"` |
| `entertainment_type` | string | No | `restaurant`, `cafe`, `museum`, `park`, `shopping`, `bar` |
| `budget_level` | string | No | `cheap`, `medium`, `premium` |
| `companion_type` | string | No | `solo`, `couple`, `family`, `friends`, `kids` |
| `start_time` | string (ISO) | No | `"2025-05-01T18:00:00"` |
| `max_distance_km` | float | No | `3.0` (default: 5.0) |
| `require_open_now` | boolean | No | `true` |
| `min_rating` | float | No | `4.0` |
| `latitude` | float | No | `10.7769` |
| `longitude` | float | No | `106.7009` |

**Auth:** Bearer token (JWT) — `require_completed_profile`

---

### Ví dụ Request / Response

**Case 1 — Query only:**
```
GET /api/v1/recommendations?query=cafe+y%C3%AAn+t%C4%A9nh&latitude=10.77&longitude=106.69
Authorization: Bearer <token>
```

**Case 2 — Filter only:**
```
GET /api/v1/recommendations?budget_level=cheap&companion_type=couple&require_open_now=true
Authorization: Bearer <token>
```

**Case 3 — Query + Filter:**
```
GET /api/v1/recommendations?query=qu%C3%A1n+%C4%83n&entertainment_type=restaurant&budget_level=medium&min_rating=4
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 42,
      "name": "The Workshop Coffee",
      "address": "27 Ngô Đức Kế, Quận 1, TP.HCM",
      "latitude": 10.7769,
      "longitude": 106.7009,
      "primary_type": "cafe",
      "category": "cafe",
      "rating": 4.5,
      "review_count": 120,
      "photo_url": "https://example.com/img.jpg",
      "distance_km": 1.2,
      "open_now": true,
      "price_level": 2,
      "score": null,
      "explanation": null
    }
  ]
}
```

> **TODO TV5 (F4):** Sau khi ranking module hoàn chỉnh, `score` và `explanation` sẽ được điền vào mỗi item. Các trường này đã khai báo sẵn trong `PlaceResponse` schema (`score: float | None = None`).

---

### Logic Search History

**Điều kiện lưu history:**
- Có `query` text → lưu nguyên text.
- Chỉ có filter → lưu dạng `"key:value key:value"` (ví dụ: `"budget_level:cheap companion_type:couple"`).
- Không có gì → không lưu (tránh noise).
- `max_distance_km` mặc định (5.0) không được lưu.

**Trim history:**
- Sau mỗi lần insert, SQL `ROW_NUMBER() OVER (ORDER BY searched_at DESC)` giữ lại 80 dòng gần nhất, xóa phần còn lại.
- Cấu hình qua `settings.max_search_history_per_user = 80` trong `config.py`.

---

## TV2 — Frontend

### Files đã sửa / implement

| File | Thay đổi |
|------|----------|
| `frontend/src/pages/Home.jsx` | Thêm `filters` state, wiring `FilterPanel`, `handleFilterApply`, `_doSearch` dùng chung cho 3 case |
| `frontend/src/components/recommendation/FilterPanel.jsx` | Implement đầy đủ controlled component với 6 filter fields + Apply/Reset |
| `frontend/src/components/recommendation/RecommendationList.jsx` | Thêm loading skeleton, error state, empty state, explanation badge |
| `frontend/src/services/recommendationService.js` | Implement `buildRecommendationFilterPayload`, tách khỏi FilterPanel.jsx |

> **Không sửa** `frontend/src/services/mapPickService.js` (đúng scope TV2).

---

### Demo — 3 Case

| Case | Thao tác | Params gửi lên |
|------|----------|----------------|
| **Query only** | Nhập `"cafe yên tĩnh"` → Enter | `{ query: "cafe yên tĩnh", latitude, longitude }` |
| **Filter only** | Chọn Budget=Cheap, Companion=Couple → Apply Filters | `{ budget_level: "cheap", companion_type: "couple", latitude, longitude }` |
| **Query + Filter** | Nhập `"quán ăn"` + chọn Type=Restaurant, Min Rating=4 → Apply Filters | `{ query: "quán ăn", entertainment_type: "restaurant", min_rating: 4, latitude, longitude }` |

### Luồng UI
```
SearchBar (query) ──→ handleSearch()  ──┐
                                        ├──→ _doSearch(query, filterPayload) ──→ fetchRecommendations(params)
FilterPanel        ──→ handleFilterApply()─┘           │
  (6 filter fields)                                     ▼
  onChange → setFilters()                    RecommendationList
  onApply  → handleFilterApply()            (loading / error / empty / grid)
```

### FilterPanel — Fields

| Field | Type | Values |
|-------|------|--------|
| `entertainment_type` | select | restaurant, cafe, museum, park, shopping, bar |
| `budget_level` | select | cheap, medium, premium |
| `companion_type` | select | solo, couple, family, friends, kids |
| `max_distance_km` | select | 1, 2, 5, 10, 20 km |
| `min_rating` | select | 3+, 3.5+, 4+, 4.5+ |
| `require_open_now` | checkbox | true / false |

### RecommendationList — States
- **Loading:** Hiện 6 skeleton card với shimmer animation.
- **Error:** Hiện error card màu đỏ nhạt với message.
- **Empty (searched):** "No places found — Try a different query or adjust filters."
- **Empty (not searched):** "No suggestions yet — Search or allow GPS."
- **Results:** Grid 3 cột PlaceCard. Nếu item có `explanation` (từ F4/TV5), hiện badge ✨ phía trên card.

---

## Dependency / Interface với các Feature khác

| Feature | Interface |
|---------|-----------|
| **F4 (TV5 - Ranking)** | `recommend_places()` trả `items`; TV5 bổ sung `score` và `explanation` vào mỗi item. Không cần sửa TV1 route. |
| **MapView** | `recommendationPlaces` trong `AppContext` — đã được `setRecommendationPlaces(items)` sau mỗi search. |
| **PlaceDetail** | `PlaceCard.handleClick()` → `navigate(/places/:id)` — không thay đổi. |
| **Route** | `PlaceCard.handlePick()` → `recordPlacePick()` + `navigate(/route)` — không thay đổi. |
