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
  { value: "", label: "🔍 All types" },
  { value: "restaurant", label: "🍽️ Restaurant" },
  { value: "cafe", label: "☕ Cafe" },
  { value: "museum", label: "🏛️ Museum" },
  { value: "park", label: "🌳 Park" },
  { value: "shopping", label: "🛍️ Shopping" },
  { value: "bar", label: "🍺 Bar" },
  { value: "movie_theater", label: "🎬 Cinema" },
  { value: "mall", label: "🏢 Mall" },
  { value: "hotel", label: "🏨 Hotel" },
];

const BUDGET_OPTIONS = [
  { value: "", label: "💰 Any budget" },
  { value: "low", label: "💚 Cheap" },
  { value: "medium", label: "💛 Medium" },
  { value: "high", label: "💜 Premium" },
];

const COMPANION_OPTIONS = [
  { value: "", label: "👥 Anyone" },
  { value: "solo", label: "🧍 Solo" },
  { value: "couple", label: "👫 Couple" },
  { value: "family", label: "👨‍👩‍👧 Family" },
  { value: "friends", label: "👯 Friends" },
  { value: "kids", label: "🧒 With kids" },
];

const TIME_OPTIONS = [
  { value: "", label: "⏰ Any time" },
  { value: "morning", label: "🌅 Morning" },
  { value: "afternoon", label: "☀️ Afternoon" },
  { value: "evening", label: "🌆 Evening" },
  { value: "night", label: "🌃 Night" },
];

const DISTANCE_OPTIONS = [
  { value: "", label: "📍 Any distance" },
  { value: "1", label: "< 1 km" },
  { value: "2", label: "< 2 km" },
  { value: "3", label: "< 3 km" },
  { value: "5", label: "< 5 km" },
  { value: "10", label: "< 10 km" },
  { value: "20", label: "< 20 km" },
];

const RATING_OPTIONS = [
  { value: "", label: "⭐ Any rating" },
  { value: "3", label: "⭐ 3+" },
  { value: "3.5", label: "⭐ 3.5+" },
  { value: "4", label: "⭐ 4+" },
  { value: "4.5", label: "⭐ 4.5+" },
];

export function buildRecommendationFilterPayload(formValues) {
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
          Going with
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
          Min Rating
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
        <span>Open now only</span>
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
