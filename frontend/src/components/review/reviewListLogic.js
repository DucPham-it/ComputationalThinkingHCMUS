/**
 * Review list display logic for rating filters and incremental comments.
 *
 * Owner:
 * - TV7: Review Rating Filter + Incremental Comments.
 *
 * File input:
 * - reviews: array of review payloads from backend.
 * - ratingFilter: "all" or a numeric star value from 1..5.
 * - visibleCount: current number of comments allowed to render.
 *
 * File output:
 * - normalized rating values.
 * - per-rating review counts.
 * - filtered review arrays.
 * - visible review slices.
 * - next visible count for "show more" behavior.
 *
 * Side effects:
 * - None. This file must stay pure so ReviewList can own UI state safely.
 */

export const INITIAL_VISIBLE_REVIEW_COUNT = 3;
export const REVIEW_LOAD_MORE_COUNT = 10;
export const RATING_FILTER_OPTIONS = ["all", 5, 4, 3, 2, 1];

export function normalizeReviewRating(value) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - value: review rating from API/UI, usually number or numeric string.
   *
   * Output:
   * - integer rating from 1..5.
   * - null when the input cannot be used as a review rating filter.
   */
  const numericRating = Number(value);
  if (!Number.isFinite(numericRating)) {
    return null;
  }

  if (!Number.isInteger(numericRating) || numericRating < 1 || numericRating > 5) {
    return null;
  }

  return numericRating;
}

export function countReviewsByRating(reviews = []) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - reviews: array of review payloads with a rating field.
   *
   * Output:
   * - object with total count in all and per-star counts in keys 1..5.
   */
  const counts = { all: reviews.length, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  reviews.forEach((review) => {
    const rating = normalizeReviewRating(review.rating);
    if (rating !== null) {
      counts[rating] += 1;
    }
  });
  return counts;
}

export function buildReviewRatingFilterOptions(reviews = []) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - reviews: array of review payloads used to count each rating bucket.
   *
   * Output:
   * - array of filter option objects for UI rendering:
   *   { value: "all" | 1 | 2 | 3 | 4 | 5, label: string, count: number }.
   */
  const counts = countReviewsByRating(reviews);
  return RATING_FILTER_OPTIONS.map((value) => ({
    value,
    label: value === "all" ? "All" : String(value),
    count: counts[value] ?? 0,
  }));
}

export function filterReviewsByRating(reviews = [], ratingFilter = "all") {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - reviews: array of review payloads.
   * - ratingFilter: "all" or a star value from 1..5.
   *
   * Output:
   * - all reviews when ratingFilter is "all".
   * - only reviews whose rating matches the selected star value otherwise.
   */
  if (ratingFilter === "all") {
    return reviews;
  }

  const selectedRating = normalizeReviewRating(ratingFilter);
  if (selectedRating === null) {
    return reviews;
  }

  return reviews.filter((review) => normalizeReviewRating(review.rating) === selectedRating);
}

export function getVisibleReviews(reviews = [], visibleCount = INITIAL_VISIBLE_REVIEW_COUNT) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - reviews: filtered review array.
   * - visibleCount: number of review cards allowed to render.
   *
   * Output:
   * - review slice from index 0 up to visibleCount.
   */
  const safeVisibleCount = Math.max(0, Number(visibleCount) || 0);
  return reviews.slice(0, safeVisibleCount);
}

export function getNextVisibleReviewCount(currentVisibleCount, totalReviewCount) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - currentVisibleCount: current visible review limit in ReviewList state.
   * - totalReviewCount: number of reviews after applying the active rating filter.
   *
   * Output:
   * - next visible review limit.
   * - increases by REVIEW_LOAD_MORE_COUNT.
   * - never exceeds totalReviewCount.
   */
  const safeCurrentCount = Math.max(0, Number(currentVisibleCount) || 0);
  const safeTotalCount = Math.max(0, Number(totalReviewCount) || 0);
  return Math.min(safeCurrentCount + REVIEW_LOAD_MORE_COUNT, safeTotalCount);
}
