import api from "./api";

/**
 * Map pick and coordinate resolution API calls.
 *
 * Owner:
 * - TV6: Map Pick To Route.
 *
 * File input:
 * - Database place id picked from marker/card/route.
 * - Free map coordinates selected by user.
 *
 * File output:
 * - Stored pick interaction through backend.
 * - Place-like object resolved from clicked coordinates.
 */

export async function recordPlacePick(placeId) {
  /**
   * Owner:
   * - TV6.
   *
   * Input:
   * - placeId: database id selected from MapView/RouteView/PlaceCard.
   *
   * Output:
   * - backend returns HTTP 204.
   * - no response body is expected.
   *
   * Side effect:
   * - backend stores/updates user_place_picks for the current user.
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
