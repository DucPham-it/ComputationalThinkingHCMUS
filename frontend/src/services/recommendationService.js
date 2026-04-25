import api from "./api";

/**
 * Recommendation API calls.
 *
 * Owner:
 * - TV2: Recommendation search/filter UI.
 *
 * File input:
 * - SearchBar query, FilterPanel payload, and optional browser/map location.
 *
 * File output:
 * - Recommendation response for Home/usePlaces.
 * - No map-pick or route side effects live in this file.
 */

export async function fetchRecommendations(params) {
  /**
   * Owner:
   * - TV2.
   *
   * Input:
   * - params.query: free text query from user.
   * - params.latitude/longitude: GPS or map context.
   * - params.entertainment_type: category filter from UI or NLP override.
   * - params.budget_level: low, medium, high.
   * - params.companion_type: solo, couple, family, friends.
   * - params.start_time: intended visit time.
   * - params.max_distance_km: radius filter.
   * - params.require_open_now: boolean.
   * - params.min_rating: 0..5.
   *
   * Output:
   * - { items: PlaceSummary[] } with at most 10 items.
   * - each item is passed to RecommendationList, MapView, and route pick flow.
   */
  const response = await api.get("/recommendations", { params });
  return response.data;
}
