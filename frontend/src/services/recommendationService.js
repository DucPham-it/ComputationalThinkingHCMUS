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

export function normalizeBudgetLevel(value) {
  /**
   * Input:
   * - value: UI/NLP budget value. Accepts low/medium/high plus aliases
   *   cheap/premium.
   *
   * Output:
   * - backend canonical budget value: low, medium, high, or undefined.
   */
  const normalized = String(value || "").trim().toLowerCase();
  const aliases = {
    cheap: "low",
    budget: "low",
    premium: "high",
    expensive: "high",
    luxury: "high",
  };
  const canonical = aliases[normalized] || normalized;
  return ["low", "medium", "high"].includes(canonical) ? canonical : undefined;
}

export function buildRecommendationFilterPayload(formValues = {}) {
  /**
   * Owner:
   * - TV2.
   *
   * Input:
   * - formValues: controlled filter object:
   *   { entertainment_type, budget_level, companion_type, start_time,
   *     max_distance_km, require_open_now, min_rating }
   *
   * Output:
   * - params accepted by fetchRecommendations.
   * - empty values are omitted.
   * - budget_level is normalized to low/medium/high.
   */
  const payload = {};

  if (formValues.entertainment_type) {
    payload.entertainment_type = formValues.entertainment_type;
  }

  const budgetLevel = normalizeBudgetLevel(formValues.budget_level);
  if (budgetLevel) {
    payload.budget_level = budgetLevel;
  }

  if (formValues.companion_type) {
    payload.companion_type = formValues.companion_type;
  }
  if (formValues.start_time) {
    payload.start_time = formValues.start_time;
  }

  const maxDistanceKm = Number(formValues.max_distance_km);
  if (Number.isFinite(maxDistanceKm) && maxDistanceKm > 0) {
    payload.max_distance_km = maxDistanceKm;
  }

  if (formValues.require_open_now === true) {
    payload.require_open_now = true;
  }

  const minRating = Number(formValues.min_rating);
  if (Number.isFinite(minRating) && minRating > 0) {
    payload.min_rating = minRating;
  }

  return payload;
}

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
