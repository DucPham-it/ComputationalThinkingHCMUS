import api from "./api";

/**
 * Recommendation API calls.
 *
 * Owner:
 * - TV2: Recommendation search/filter UI.
 *
 * File input:
 * - SearchBar query, FilterPanel payload, và optional browser/map location.
 *
 * File output:
 * - Recommendation response cho Home/usePlaces.
 * - Không có map-pick hoặc route side effects trong file này.
 */

/**
 * Chuyển đổi filter state từ UI thành query params cho backend.
 *
 * Owner: TV2.
 *
 * Input:
 * - formValues: object từ controlled FilterPanel:
 *   {
 *     entertainment_type: string  // "restaurant"|"cafe"|"museum"|"park"|"shopping"|"bar"
 *     budget_level:       string  // "cheap"|"medium"|"premium"
 *     companion_type:     string  // "solo"|"couple"|"family"|"friends"|"kids"
 *     start_time:         string  // ISO string hoặc time slot
 *     max_distance_km:    number  // khoảng cách tối đa (km)
 *     require_open_now:   boolean // true = chỉ lấy địa điểm đang mở
 *     min_rating:         number  // 0..5
 *   }
 *
 * Output:
 * - Object chứa các params được fetchRecommendations chấp nhận.
 * - Bỏ qua các giá trị rỗng/null/undefined/false để backend dùng NLP/defaults.
 * - Không bao giờ gửi max_distance_km = 0 (vô nghĩa về mặt địa lý).
 *
 * Examples:
 * - { budget_level: "cheap", companion_type: "couple" }
 *   → { budget_level: "cheap", companion_type: "couple" }
 * - { entertainment_type: "", min_rating: 0, require_open_now: false }
 *   → {}  (tất cả đều trống/falsy)
 */
export function buildRecommendationFilterPayload(formValues) {
  const payload = {};

  if (formValues.entertainment_type) {
    payload.entertainment_type = formValues.entertainment_type;
  }
  if (formValues.budget_level) {
    payload.budget_level = formValues.budget_level;
  }
  if (formValues.companion_type) {
    payload.companion_type = formValues.companion_type;
  }
  if (formValues.start_time) {
    payload.start_time = formValues.start_time;
  }
  if (
    formValues.max_distance_km !== undefined &&
    formValues.max_distance_km !== null &&
    formValues.max_distance_km > 0
  ) {
    payload.max_distance_km = formValues.max_distance_km;
  }
  if (formValues.require_open_now === true) {
    payload.require_open_now = true;
  }
  if (
    formValues.min_rating !== undefined &&
    formValues.min_rating !== null &&
    formValues.min_rating > 0
  ) {
    payload.min_rating = formValues.min_rating;
  }

  return payload;
}

/**
 * Gọi GET /api/v1/recommendations với query + filter params.
 *
 * Owner: TV2.
 *
 * Input:
 * - params.query:              free text query.
 * - params.latitude/longitude: GPS hoặc map context.
 * - params.entertainment_type, budget_level, companion_type,
 *   start_time, max_distance_km, require_open_now, min_rating:
 *   từ buildRecommendationFilterPayload.
 *
 * Output:
 * - { items: PlaceSummary[] } với tối đa 10 items.
 * - Mỗi item được truyền vào RecommendationList, MapView, và route pick flow.
 *
 * Usage:
 * - Query only:   fetchRecommendations({ query: "cafe yên tĩnh", latitude, longitude })
 * - Filter only:  fetchRecommendations({ ...filterPayload, latitude, longitude })
 * - Query+Filter: fetchRecommendations({ query, ...filterPayload, latitude, longitude })
 */
export async function fetchRecommendations(params) {
  const response = await api.get("/recommendations", { params });
  return response.data;
}
