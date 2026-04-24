import api from "./api";

/**
 * Input:
 * - placeId: selected place id
 *
 * Output:
 * - review list payload
 */
export async function fetchReviews(placeId) {
  const response = await api.get(`/reviews`, { params: { place_id: placeId } });
  return response.data;
}

/**
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
