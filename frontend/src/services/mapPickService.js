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
  try {
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
  } catch (error) {
    console.warn("Lỗi khi gọi API resolve-point, sử dụng điểm dự phòng:", error);
    const fallbackData = {
      id: `fallback:${latitude}:${longitude}`,
      name: "Điểm tùy chọn",
      address: `${latitude}, ${longitude}`,
      latitude,
      longitude,
      can_view: false,
      can_save: false,
      is_local_only: true,
    };
    return {
      ...fallbackData,
      _canView: fallbackData.can_view,
      _canSave: fallbackData.can_save,
      _isLocalOnly: fallbackData.is_local_only,
    };
  }
}
