import { Check, RotateCcw } from "lucide-react";

import { buildRecommendationFilterPayload as buildPayload } from "../../services/recommendationService";

export const EMPTY_RECOMMENDATION_FILTERS = {
  entertainment_type: "",
  budget_level: "",
  companion_type: "",
  start_time: "",
  max_distance_km: "",
  require_open_now: false,
  min_rating: "",
};

const ENTERTAINMENT_OPTIONS = [
  { value: "", label: "All types" },
  { value: "restaurant", label: "Restaurant" },
  { value: "cafe", label: "Cafe" },
  { value: "movie_theater", label: "Cinema" },
  { value: "park", label: "Park" },
  { value: "mall", label: "Mall" },
  { value: "museum", label: "Museum" },
  { value: "hotel", label: "Hotel" },
];

const BUDGET_OPTIONS = [
  { value: "", label: "Any budget" },
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
];

const COMPANION_OPTIONS = [
  { value: "", label: "Any group" },
  { value: "solo", label: "Solo" },
  { value: "couple", label: "Couple" },
  { value: "family", label: "Family" },
  { value: "friends", label: "Friends" },
];

const TIME_OPTIONS = [
  { value: "", label: "Any time" },
  { value: "morning", label: "Morning" },
  { value: "afternoon", label: "Afternoon" },
  { value: "evening", label: "Evening" },
  { value: "night", label: "Night" },
];

const DISTANCE_OPTIONS = [
  { value: "", label: "Any distance" },
  { value: "1", label: "Within 1 km" },
  { value: "3", label: "Within 3 km" },
  { value: "5", label: "Within 5 km" },
  { value: "10", label: "Within 10 km" },
];

const RATING_OPTIONS = [
  { value: "", label: "Any rating" },
  { value: "3", label: "3+ stars" },
  { value: "4", label: "4+ stars" },
  { value: "4.5", label: "4.5+ stars" },
];

/**
 * Recommendation filters.
 *
 * Owner:
 * - TV2: Frontend search/filter/result wiring.
 *
 * File input:
 * - value: controlled filter object from Home:
 *   { entertainment_type, budget_level, companion_type, start_time,
 *     max_distance_km, require_open_now, min_rating }.
 * - onChange: callback receiving the next controlled filter object.
 * - onApply: callback receiving backend-ready filter query params.
 * - disabled: disables controls while recommendation search is locked.
 *
 * File output:
 * - Controlled UI state changes via onChange.
 * - Backend query params via onApply/buildRecommendationFilterPayload:
 *   { entertainment_type, budget_level, companion_type, start_time,
 *     max_distance_km, require_open_now, min_rating }.
 */

export function buildRecommendationFilterPayload(formValues) {
  /**
   * Convert filter UI state into backend query params.
   *
   * Owner:
   * - TV2.
   *
   * Input:
   * - formValues: object from controlled filter controls:
   *   entertainment_type, budget_level, companion_type, start_time,
   *   max_distance_km, require_open_now, min_rating.
   *
   * Output:
   * - params accepted by fetchRecommendations.
   * - empty values are omitted so backend can fall back to NLP/defaults.
   * - budget aliases are normalized to low/medium/high.
   */
  return buildPayload(formValues);
}

export default function FilterPanel({
  value = EMPTY_RECOMMENDATION_FILTERS,
  onChange,
  onApply,
  disabled = false,
}) {
  const filters = { ...EMPTY_RECOMMENDATION_FILTERS, ...value };

  function updateField(field, nextValue) {
    onChange?.({
      ...filters,
      [field]: nextValue,
    });
  }

  function handleApply(event) {
    event.preventDefault();
    onApply?.(buildRecommendationFilterPayload(filters));
  }

  function handleReset() {
    onChange?.(EMPTY_RECOMMENDATION_FILTERS);
    onApply?.({});
  }

  return (
    <form className="card recommendation-filter" onSubmit={handleApply}>
      <h3 className="recommendation-filter-title">Filters</h3>

      <div className="recommendation-filter-grid">
        <label className="recommendation-filter-field">
          Type
          <select
            value={filters.entertainment_type}
            onChange={(event) => updateField("entertainment_type", event.target.value)}
            disabled={disabled}
          >
            {ENTERTAINMENT_OPTIONS.map((option) => (
              <option key={option.value || "all-types"} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="recommendation-filter-field">
          Budget
          <select
            value={filters.budget_level}
            onChange={(event) => updateField("budget_level", event.target.value)}
            disabled={disabled}
          >
            {BUDGET_OPTIONS.map((option) => (
              <option key={option.value || "any-budget"} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="recommendation-filter-field">
          Group
          <select
            value={filters.companion_type}
            onChange={(event) => updateField("companion_type", event.target.value)}
            disabled={disabled}
          >
            {COMPANION_OPTIONS.map((option) => (
              <option key={option.value || "any-group"} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="recommendation-filter-field">
          Time
          <select
            value={filters.start_time}
            onChange={(event) => updateField("start_time", event.target.value)}
            disabled={disabled}
          >
            {TIME_OPTIONS.map((option) => (
              <option key={option.value || "any-time"} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="recommendation-filter-field">
          Distance
          <select
            value={filters.max_distance_km}
            onChange={(event) => updateField("max_distance_km", event.target.value)}
            disabled={disabled}
          >
            {DISTANCE_OPTIONS.map((option) => (
              <option key={option.value || "any-distance"} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="recommendation-filter-field">
          Rating
          <select
            value={filters.min_rating}
            onChange={(event) => updateField("min_rating", event.target.value)}
            disabled={disabled}
          >
            {RATING_OPTIONS.map((option) => (
              <option key={option.value || "any-rating"} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <label className="recommendation-open-now">
        <input
          className="recommendation-open-now-checkbox"
          type="checkbox"
          checked={filters.require_open_now}
          onChange={(event) => updateField("require_open_now", event.target.checked)}
          disabled={disabled}
        />
        <span>Open now</span>
      </label>

      <div className="recommendation-filter-actions">
        <button className="btn-primary recommendation-filter-button" type="submit" disabled={disabled}>
          <Check size={18} />
          <span>Apply</span>
        </button>
        <button
          type="button"
          className="btn-outline recommendation-filter-button"
          onClick={handleReset}
          disabled={disabled}
        >
          <RotateCcw size={17} />
          <span>Reset</span>
        </button>
      </div>
    </form>
  );
}
