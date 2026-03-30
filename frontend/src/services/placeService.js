/**
 * Place-related API calls.
 *
 * These functions should stay thin: only call backend and return response data.
 * Any UI-specific transformation should happen in hooks or components.
 */
import api from "./api";

export async function fetchRecommendations(params) {
  /**
   * Input:
   * - params.query: free text query from user
   * - later: GPS, budget, type, time, companion type, distance radius
   *
   * Output:
   * - { items: PlaceSummary[] }
   */
  const response = await api.get("/recommendations", { params });
  return response.data;
}

export async function fetchPlaceDetail(id) {
  /**
   * Input:
   * - place id from route param
   *
   * Output:
   * - detailed place payload for place detail page
   */
  const response = await api.get(`/places/${id}`);
  return response.data;
}
