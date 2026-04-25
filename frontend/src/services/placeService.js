/**
 * Place detail API calls.
 *
 * Owner:
 * - Shared existing place detail flow.
 *
 * File input:
 * - place id from route param or selected review/place page.
 *
 * File output:
 * - detailed place payload for PlaceDetail and ReviewPage.
 *
 * Conflict note:
 * - TV2 uses recommendationService.js for recommendation search/filter.
 * - TV6 uses mapPickService.js for pick recording and map coordinate resolve.
 */
import api from "./api";

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
