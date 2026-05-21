# Turn-by-Turn Navigation – Kế hoạch triển khai

## Nguyên tắc chính

> **Mỗi người CHỈ tạo/sửa file của riêng mình. Không ai chạm file của người khác.**
> Người 1–6 làm song song. Người 7 là integrator chính, ghép nối cuối cùng.

---

## Bảng tổng hợp phân công

| Người | Vai trò | Số file |
|---|---|---|
| **1** | Backend Route Data | 4 |
| **2** | GPS + Geo Math | 3 |
| **3** | Navigation UI | 6 |
| **4** | Voice + Helpers + Services | 4 |
| **5** | Navigation Engine | 1 |
| **6** | Map Integration + QA Support | 4 |
| **7** | Main Integration + Orchestration | 2 |

## Thứ tự làm việc

```
┌─ Người 1 (Backend + Contract)          ─┐
├─ Người 2 (GPS + Geo Math)               │
├─ Người 3 (Navigation UI)                ├──► SONG SONG
├─ Người 4 (Voice + Format + Service)     │
├─ Người 5 (Navigation Engine)            │
└─ Người 6 (Map components)              ─┘
                │
                ▼
Người 7 ──► Ghép nối (Controller + RouteView) ──► Test tích hợp ──► Nghiệm thu
```

**Người 1–6 làm song song.** Người 7 ghép cuối, Người 6 hỗ trợ debug.

---

## Người 1 — Backend Route Data

**Vai trò**: Backend API + route data provider.

### Files

| File | Loại | Đường dẫn |
|---|---|---|
| `routing_service.py` | **MODIFY** | `backend/app/services/routing_service.py` |
| `route_schema.py` | **MODIFY** | `backend/app/schemas/route_schema.py` |
| `api_contract_navigation.json` | **NEW** | `docs/api_contract_navigation.json` |
| `sample_navigation_response.json` | **NEW** | `docs/sample_navigation_response.json` |

### Công việc

- Extract OSRM: `geometry`, `maneuver_type/modifier`, `maneuver_location`, `distance_meters`, `duration_seconds`
- Sửa `_build_fallback_route()` bổ sung field mới với giá trị default
- Thêm field optional vào `RouteStep` schema
- Tạo API response mẫu + contract JSON cho team

### Không làm

 Frontend, UI, GPS, Map

### Bàn giao

- [ ] API response mẫu trước/sau khi sửa
- [ ] Mỗi step có `geometry` ≥ 2 tọa độ
- [ ] Contract + sample response đã commit

---

## Người 2 — GPS + Geo Math

**Vai trò**: GPS tracking + toán học navigation.

### Files

| File | Loại | Đường dẫn |
|---|---|---|
| `useGPSTracking.js` | **NEW** | `frontend/src/hooks/useGPSTracking.js` |
| `geomath.js` | **NEW** | `frontend/src/utils/geomath.js` |
| `geomath.test.js` | **NEW** | `frontend/tests/geomath.test.js` |

### Công việc

- `haversineDistance(pointA, pointB)` → mét
- `pointToSegmentDistance(point, segmentStart, segmentEnd)` → mét
- `snapToPolyline(point, polyline)` → `{ snappedPoint, distanceMeters, segmentIndex, progress }`
- `calculateBearing(from, to)` → góc 0-360°
- `polylineRemainingDistance(polyline, fromIndex)` → mét
- GPS `watchPosition` wrapper + noise filter (`accuracy > 100m` → bỏ)
- Unit test cho tất cả hàm geo

### Không làm

 UI, reroute, integration

### Bàn giao

- [ ] Test pass: `npm test geomath.test.js`
- [ ] JSDoc cho từng hàm

---

## Người 3 — Navigation UI

**Vai trò**: Pure UI developer.

### Files

| File | Loại | Đường dẫn |
|---|---|---|
| `NavigationPanel.jsx` | **NEW** | `frontend/src/components/navigation/NavigationPanel.jsx` |
| `NavigationBanner.jsx` | **NEW** | `frontend/src/components/navigation/NavigationBanner.jsx` |
| `NavigationBottomBar.jsx` | **NEW** | `frontend/src/components/navigation/NavigationBottomBar.jsx` |
| `NavigationStepIcon.jsx` | **NEW** | `frontend/src/components/navigation/NavigationStepIcon.jsx` |
| `NavigationOverview.jsx` | **NEW** | `frontend/src/components/navigation/NavigationOverview.jsx` |
| `navigation.css` | **NEW** | `frontend/src/components/navigation/navigation.css` |

### Công việc

- Full-screen navigation layout, banner (icon + instruction + distance), bottom bar (progress + remaining + End button + voice toggle)
- Step icon SVG (rẽ trái ↰, phải ↱, thẳng ↑, quay đầu ↩, đến nơi , vòng xuyến ⟳)
- Overview list (scrollable, highlight current, mờ past steps)
- Responsive mobile-first (375px), animation fade/slide, pulse

###  QUAN TRỌNG

> **Chỉ nhận props → render UI.** Không GPS, không API, không logic navigation. Dùng mock data để develop.

### Bàn giao

- [ ] Demo 4 trạng thái: bình thường, sắp rẽ (< 100m), off-route, arrived
- [ ] Responsive check 375px

---

## Người 4 — Voice + Helpers + Services

**Vai trò**: Voice guidance + helper utilities.

### Files

| File | Loại | Đường dẫn |
|---|---|---|
| `voiceGuidanceService.js` | **NEW** | `frontend/src/services/voiceGuidanceService.js` |
| `navigationFormat.js` | **NEW** | `frontend/src/utils/navigationFormat.js` |
| `navigationService.js` | **NEW** | `frontend/src/services/navigationService.js` |
| `navigationHelpers.js` | **NEW** | `frontend/src/utils/navigationHelpers.js` |

### Công việc

**Voice** (`voiceGuidanceService.js`):
- `speakInstruction(text)` – đọc tiếng Việt (`vi-VN`), queue, force cancel
- `translateManeuver(type, modifier)` – dịch: `turn+left` → "Rẽ trái", `arrive` → "Bạn đã đến nơi"...
- `buildVoiceInstruction(step)` → "Sau 200 mét, rẽ trái vào Nguyễn Huệ"
- `cancelSpeech()`, `isVoiceSupported()`, `isSpeaking()`

**Format** (`navigationFormat.js`):
- `formatDistanceVi(meters)`: `2300` → `"2,3 km"`
- `formatDurationVi(seconds)`: `3700` → `"1 giờ 2 phút"`
- `formatETA(date)`: → `"10:55"`
- `formatRemainingText(dist, dur)`: → `"Còn 2,3 km · 8 phút"`

**Service** (`navigationService.js`):
- `requestReroute({ currentPosition, destination, travelMode })` – gọi `getRoute()` từ `routeService.js`
- `shouldReroute(isOffRoute, lastRerouteTime)` – chỉ reroute nếu ≥ 15s
- `buildNavigationSummary(routeInfo, currentStepIndex)`

**Helpers** (`navigationHelpers.js`):
- `extractStepsFromRoute(routeInfo)` → chuẩn hóa mảng steps
- `buildFullPath(steps)` → nối geometry thành 1 polyline
- `getManeuverIcon(type, modifier)` → tên icon
- `isNavigationSupported()` → check browser support

### Không làm

 UI, Map, GPS tracking

### Bàn giao

- [ ] Demo voice đọc tiếng Việt
- [ ] Bảng maneuver đã translate (≥ 10 loại)

---

## Người 5 — Navigation Engine

**Vai trò**: Core navigation algorithm. **Làm song song với N1-4, N6.**

### Files

| File | Loại | Đường dẫn |
|---|---|---|
| `useNavigationEngine.js` | **NEW** | `frontend/src/hooks/useNavigationEngine.js` |

### Công việc

#### [NEW] `useNavigationEngine.js`

Hook logic navigation chính:
- **Input**: `steps`, `fullPath`, `gpsPosition`, `isActive`
- **Output**: `currentStepIndex`, `currentStep`, `nextStep`, `distanceToNextTurn`, `isOffRoute` (> 50m ≥ 5s), `progress` (0-100%), `remainingDistance`, `remainingDuration`, `eta`, `hasArrived` (< 30m), `snappedPosition`
- **Logic**: GPS → snap polyline → tính distance → auto chuyển step → detect off-route → detect arrived
- Import `geomath.js` (N2) cho các hàm tính toán — nếu N2 chưa xong, tự mock hoặc viết inline

### Không làm

 Orchestration, voice integration, UI, Map, RouteView

### Bàn giao

- [ ] Hook hoạt động với mock GPS data
- [ ] Test: auto advance step, off-route detection, arrived detection
- [ ] JSDoc rõ ràng cho tất cả output fields

---

## Người 7 — Main Integration + Orchestration

**Vai trò**: Main Integrator. **Làm SAU khi N1-6 hoàn thành.**

### Files

| File | Loại | Đường dẫn |
|---|---|---|
| `useNavigationController.js` | **NEW** | `frontend/src/hooks/useNavigationController.js` |
| `RouteView.jsx` | **MODIFY** | `frontend/src/pages/RouteView.jsx` |

### Công việc

#### [NEW] `useNavigationController.js`

> **Orchestrator** – kết nối tất cả modules, tách logic khỏi RouteView.jsx.

- **Input**: `routeInfo`, `destination`, `travelMode`
- **Output**: `navigationActive`, `startNavigation()`, `endNavigation()`, `voiceEnabled`, `toggleVoice()`, `gps`, `engine`, `handleReroute()`, `navigationProps` (gom sẵn cho `<NavigationPanel>`)
- Import: `useGPSTracking` (N2), `useNavigationEngine` (N5), voice/service/helpers (N4)
- useEffect: voice khi chuyển step, cảnh báo off-route, thông báo arrived, auto reroute

#### [MODIFY] `RouteView.jsx`

Thay đổi **tối thiểu** (~30-40 dòng):
- `const nav = useNavigationController(routeInfo, destination, travelMode)`
- Nút " Start Navigation"
- `nav.navigationActive = true` → `<NavigationPanel>` bao quanh `<MapContainer>`
- `nav.navigationActive = false` → giữ nguyên behavior cũ

### Không làm

 Navigation algorithm (Người 5), Map rendering (Người 6), UI components (Người 3)

### Bàn giao

- [ ] Controller kết nối tất cả modules
- [ ] RouteView tích hợp hoàn chỉnh
- [ ] Backward-compatible verified
- [ ] Test luồng end-to-end: start → navigate → arrive

---

## Người 6 — Map Integration + QA Support

**Vai trò**: Integration support + map rendering + testing.

### Files

| File | Loại | Đường dẫn |
|---|---|---|
| `MapContainer.jsx` | **MODIFY** | `frontend/src/components/map/MapContainer.jsx` |
| `RouteMap.jsx` | **MODIFY** | `frontend/src/components/map/RouteMap.jsx` |
| `UserPositionMarker.jsx` | **NEW** | `frontend/src/components/map/UserPositionMarker.jsx` |
| `integration_test_checklist.md` | **NEW** | `docs/integration_test_checklist.md` |

### Công việc

#### [MODIFY] `MapContainer.jsx`
- Thêm props `navigationMode`, `followPosition`
- `navigationMode = true`: height `100vh`, zoom 17, auto `setView` theo GPS

#### [MODIFY] `RouteMap.jsx`
- Thêm props `navigationMode`, `currentStepIndex`, `steps`
- 3 Polyline: đã đi (xám #94a3b8), đang đi (xanh đậm #2563eb), chưa đi (xanh nhạt #93c5fd)

#### [NEW] `UserPositionMarker.jsx`
- Props: `position`, `heading`, `accuracy`
- CircleMarker xanh dương + vòng accuracy + pulse animation

#### [NEW] `integration_test_checklist.md`
- Test luồng chính, off-route, arrived, backward-compatible, edge cases

### Hỗ trợ Người 5

> Người 6 hỗ trợ Người 5 debug integration: test map rendering trong navigation mode, verify polyline đổi màu đúng, GPS follow hoạt động. (NẾU CẦN)

### Bàn giao

- [ ] Map full-screen navigation mode hoạt động
- [ ] Polyline 3 màu render đúng
- [ ] User marker + pulse animation
- [ ] Integration test checklist pass

---

## Tổng kết: Danh sách file theo từng người

### Người 1 — Backend Route Data (4 files)

| # | File | Đường dẫn | Loại |
|---|---|---|---|
| 1 | `routing_service.py` | `backend/app/services/routing_service.py` | **MODIFY** |
| 2 | `route_schema.py` | `backend/app/schemas/route_schema.py` | **MODIFY** |
| 3 | `api_contract_navigation.json` | `docs/api_contract_navigation.json` | **NEW** |
| 4 | `sample_navigation_response.json` | `docs/sample_navigation_response.json` | **NEW** |

### Người 2 — GPS + Geo Math (3 files)

| # | File | Đường dẫn | Loại |
|---|---|---|---|
| 1 | `useGPSTracking.js` | `frontend/src/hooks/useGPSTracking.js` | **NEW** |
| 2 | `geomath.js` | `frontend/src/utils/geomath.js` | **NEW** |
| 3 | `geomath.test.js` | `frontend/tests/geomath.test.js` | **NEW** |

### Người 3 — Navigation UI (6 files)

| # | File | Đường dẫn | Loại |
|---|---|---|---|
| 1 | `NavigationPanel.jsx` | `frontend/src/components/navigation/NavigationPanel.jsx` | **NEW** |
| 2 | `NavigationBanner.jsx` | `frontend/src/components/navigation/NavigationBanner.jsx` | **NEW** |
| 3 | `NavigationBottomBar.jsx` | `frontend/src/components/navigation/NavigationBottomBar.jsx` | **NEW** |
| 4 | `NavigationStepIcon.jsx` | `frontend/src/components/navigation/NavigationStepIcon.jsx` | **NEW** |
| 5 | `NavigationOverview.jsx` | `frontend/src/components/navigation/NavigationOverview.jsx` | **NEW** |
| 6 | `navigation.css` | `frontend/src/components/navigation/navigation.css` | **NEW** |

### Người 4 — Voice + Helpers + Services (4 files)

| # | File | Đường dẫn | Loại |
|---|---|---|---|
| 1 | `voiceGuidanceService.js` | `frontend/src/services/voiceGuidanceService.js` | **NEW** |
| 2 | `navigationFormat.js` | `frontend/src/utils/navigationFormat.js` | **NEW** |
| 3 | `navigationService.js` | `frontend/src/services/navigationService.js` | **NEW** |
| 4 | `navigationHelpers.js` | `frontend/src/utils/navigationHelpers.js` | **NEW** |

### Người 5 — Navigation Engine (1 file)

| # | File | Đường dẫn | Loại |
|---|---|---|---|
| 1 | `useNavigationEngine.js` | `frontend/src/hooks/useNavigationEngine.js` | **NEW** |

### Người 6 — Map Integration + QA Support (4 files)

| # | File | Đường dẫn | Loại |
|---|---|---|---|
| 1 | `MapContainer.jsx` | `frontend/src/components/map/MapContainer.jsx` | **MODIFY** |
| 2 | `RouteMap.jsx` | `frontend/src/components/map/RouteMap.jsx` | **MODIFY** |
| 3 | `UserPositionMarker.jsx` | `frontend/src/components/map/UserPositionMarker.jsx` | **NEW** |
| 4 | `integration_test_checklist.md` | `docs/integration_test_checklist.md` | **NEW** |

### Người 7 — Main Integration + Orchestration (2 files)

| # | File | Đường dẫn | Loại |
|---|---|---|---|
| 1 | `useNavigationController.js` | `frontend/src/hooks/useNavigationController.js` | **NEW** |
| 2 | `RouteView.jsx` | `frontend/src/pages/RouteView.jsx` | **MODIFY** |

### Tổng cộng

| Loại | Số lượng |
|---|---|
| File **MỚI** (NEW) | **19** |
| File **SỬA** (MODIFY) | **5** |
| **Tổng** | **24** |
