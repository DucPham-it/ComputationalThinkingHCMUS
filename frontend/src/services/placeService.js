/**
 * Place-related API calls.
 *
 * Owners:
 * - TV2: recommendation search/filter requests.
 * - TV6: map pick and coordinate resolution requests.
 *
 * These functions should stay thin: only call backend and return response data.
 * Any UI-specific transformation should happen in hooks or components.
 */
import api from "./api";

export async function fetchRecommendations(params) {
  /**
   * Owner:
   * - TV2.
   *
   * Input:
   * - params.query: free text query from user
   * - params.latitude/longitude: GPS or map context
   * - params.entertainment_type: category filter from UI or NLP override
   * - params.budget_level: low, medium, high
   * - params.companion_type: solo, couple, family, friends
   * - params.start_time: intended visit time
   * - params.max_distance_km: radius filter
   * - params.require_open_now: boolean
   * - params.min_rating: 0..5
   *
   * Output:
   * - { items: PlaceSummary[] } with at most 10 items
   * - each item is passed to RecommendationList, MapView, and route pick flow.
   */
  const response = await api.get("/recommendations", { params });
  return response.data;
}

export async function fetchPlaceDetail(id) {
  /**
   * Owner:
   * - Shared existing place detail flow.
   *
   * Input:
   * - place id from route param
   *
   * Output:
   * - detailed place payload for place detail page
   */
  const response = await api.get(`/places/${id}`);
  return response.data;
}

export async function recordPlacePick(placeId) {
  /**
   * Owner:
   * - TV6.
   *
   * Input:
   * - placeId: database id selected from MapView/RouteView.
   *
   * Output:
   * - backend returns HTTP 204.
   * - no response body is expected.
   */
  await api.post(`/recommendations/picks/${placeId}`);
}

export async function resolvePlaceFromCoordinates({ latitude, longitude }) {
  /**
   * Owner:
   * - TV6.
   *
   * Input:
   * - latitude: clicked map latitude.
   * - longitude: clicked map longitude.
   *
   * Output:
   * - place-like object with coordinates and view/save flags:
   *   { id, name, address, latitude, longitude, can_view, can_save,
   *     _canView, _canSave, _isLocalOnly }
   */
  const response = await api.post("/places/resolve-point", {
    latitude,
    longitude,
  });
  const data = response.data;
  return {
    ...data,
    _canView: data.can_view,
    _canSave: data.can_save,
    _isLocalOnly: data.is_local_only,
  };
}
