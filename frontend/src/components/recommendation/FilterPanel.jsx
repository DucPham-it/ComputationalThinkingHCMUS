/**
 * Recommendation filters.
 *
 * Owner:
 * - TV2: Frontend search/filter/result wiring.
 *
 * File input:
 * - value: current filter state from Home, planned shape:
 *   { entertainment_type, budget_level, companion_type, start_time,
 *     max_distance_km, require_open_now, min_rating }
 * - onChange: callback to update Home filter state.
 *
 * File output:
 * - visual controls for filters sent to GET /recommendations:
 *   entertainment_type, budget_level, companion_type, start_time,
 *   max_distance_km, require_open_now, min_rating.
 * - buildRecommendationFilterPayload output used by recommendationService.fetchRecommendations.
 *
 * TODO TV2:
 * - lift state to Home page
 * - send budget, distance, type, time slot, companion, rating, open-now to backend
 */

export function buildRecommendationFilterPayload(formValues) {
  /**
   * TODO TV2: convert filter UI state into backend query params.
   *
   * Owner:
   * - TV2.
   *
   * Input:
   * - formValues: object from controlled filter controls:
   *   - entertainment_type: category selected by user
   *   - budget_level: cheap/medium/premium or low/medium/high after normalize
   *   - companion_type: solo/couple/family/friends/kids
   *   - start_time: ISO string or time slot
   *   - max_distance_km: number
   *   - require_open_now: boolean
   *   - min_rating: number 0..5
   *
   * Output:
   * - params accepted by fetchRecommendations:
   *   { entertainment_type, budget_level, companion_type, start_time,
   *     max_distance_km, require_open_now, min_rating }
   * - omit empty values so backend can fall back to NLP/defaults.
   */
}

export default function FilterPanel() {
  return (
    <div className="card">
      <h3>Filters</h3>
      <div className="row">
        <select>
          <option>Budget</option>
        </select>
        <select>
          <option>Distance</option>
        </select>
        <select>
          <option>Weather</option>
        </select>
      </div>
    </div>
  );
}
