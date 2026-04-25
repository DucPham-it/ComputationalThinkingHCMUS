import api from "./api";

/**
 * Review API service.
 *
 * Owner:
 * - Existing review create/list flow.
 * - TV7 may use the query-param contract below if review filtering/pagination
 *   later moves from frontend display logic to backend API.
 *
 * File input:
 * - placeId: selected database place id.
 * - optional review list query options for future backend filtering.
 * - create review payload from ReviewForm.
 *
 * File output:
 * - review list payload for ReviewList.
 * - review submission payload with aggregate stats.
 */

export function buildReviewListParams(placeId, options = {}) {
  /**
   * Owner:
   * - TV7 owns the future review filter/pagination params.
   *
   * Input:
   * - placeId: selected place id.
   * - options.ratingFilter: optional "all" or star value 1..5.
   * - options.limit: optional number of reviews requested from backend.
   * - options.offset: optional number of reviews skipped by backend.
   *
   * Output:
   * - params object safe to pass to api.get("/reviews", { params }).
   * - Always includes place_id.
   * - Includes rating, limit, offset only when valid and useful.
   *
   * TODO TV7:
   * - Use this helper when backend supports server-side rating filter or
   *   pagination for very large review lists.
   */
  const params = { place_id: placeId };
  const rating = Number(options.ratingFilter);
  const limit = Number(options.limit);
  const offset = Number(options.offset);

  if (Number.isInteger(rating) && rating >= 1 && rating <= 5) {
    params.rating = rating;
  }

  if (Number.isInteger(limit) && limit > 0) {
    params.limit = limit;
  }

  if (Number.isInteger(offset) && offset >= 0) {
    params.offset = offset;
  }

  return params;
}

/**
 * Owner:
 * - Existing review list flow.
 * - TV7 can extend options after backend supports server-side filter/paging.
 *
 * Input:
 * - placeId: selected place id
 * - options: optional future query controls:
 *   ratingFilter, limit, offset.
 *
 * Output:
 * - review list payload
 */
export async function fetchReviews(placeId, options = {}) {
  const response = await api.get(`/reviews`, { params: buildReviewListParams(placeId, options) });
  return response.data;
}

/**
 * Owner:
 * - Existing review create flow.
 *
 * Input:
 * - { place_id, content, rating, image_urls }
 * - image_urls can include URLs returned by /uploads/review-images
 *
 * Output:
 * - review submission result with new aggregate stats
 */
export async function createReview(payload) {
  const response = await api.post(`/reviews`, payload);
  return response.data;
}
