/**
 * FilterPanel — Bộ lọc tìm kiếm địa điểm.
 *
 * Owner:
 * - TV2: Frontend search/filter/result wiring.
 *
 * Props:
 * - value: object filter hiện tại từ Home state.
 *   { entertainment_type, budget_level, companion_type, start_time,
 *     max_distance_km, require_open_now, min_rating }
 * - onChange: callback (newValue) => void — gọi khi user thay đổi bất kỳ filter nào.
 * - onApply: callback () => void — gọi khi user bấm "Apply Filters".
 * - disabled: boolean — disable toàn bộ controls khi chưa đăng nhập/profile.
 *
 * File output:
 * - Render controlled select/input/checkbox cho mỗi filter field.
 * - Gọi onChange mỗi khi một field thay đổi (controlled pattern).
 * - Gọi onApply khi user submit filter.
 * - Nút Reset để xóa toàn bộ filter về rỗng.
 */

const EMPTY_FILTERS = {
  entertainment_type: "",
  budget_level: "",
  companion_type: "",
  start_time: "",
  max_distance_km: "",
  require_open_now: false,
  min_rating: "",
};

const ENTERTAINMENT_TYPES = [
  { value: "restaurant", label: "🍽️ Restaurant" },
  { value: "cafe",       label: "☕ Cafe" },
  { value: "museum",     label: "🏛️ Museum" },
  { value: "park",       label: "🌳 Park" },
  { value: "shopping",   label: "🛍️ Shopping" },
  { value: "bar",        label: "🍺 Bar" },
];

const BUDGET_LEVELS = [
  { value: "cheap",   label: "💚 Cheap" },
  { value: "medium",  label: "💛 Medium" },
  { value: "premium", label: "💜 Premium" },
];

const COMPANION_TYPES = [
  { value: "solo",    label: "🧍 Solo" },
  { value: "couple",  label: "👫 Couple" },
  { value: "family",  label: "👨‍👩‍👧 Family" },
  { value: "friends", label: "👯 Friends" },
  { value: "kids",    label: "🧒 With kids" },
];

const DISTANCE_OPTIONS = [
  { value: "1",  label: "< 1 km" },
  { value: "2",  label: "< 2 km" },
  { value: "5",  label: "< 5 km" },
  { value: "10", label: "< 10 km" },
  { value: "20", label: "< 20 km" },
];

const MIN_RATING_OPTIONS = [
  { value: "3",   label: "⭐ 3+" },
  { value: "3.5", label: "⭐ 3.5+" },
  { value: "4",   label: "⭐ 4+" },
  { value: "4.5", label: "⭐ 4.5+" },
];

const selectStyle = {
  width: "100%",
  padding: "9px 12px",
  borderRadius: "10px",
  border: "1.5px solid var(--color-border)",
  background: "var(--color-bg)",
  color: "var(--color-text)",
  fontSize: "0.9rem",
  cursor: "pointer",
};

const labelStyle = {
  display: "block",
  fontSize: "0.8rem",
  fontWeight: 700,
  color: "var(--color-text-soft)",
  marginBottom: "6px",
  textTransform: "uppercase",
  letterSpacing: "0.05em",
};

export default function FilterPanel({ value = EMPTY_FILTERS, onChange, onApply, disabled = false }) {
  function handleChange(field, newValue) {
    if (onChange) onChange({ ...value, [field]: newValue });
  }

  function handleReset() {
    if (onChange) onChange({ ...EMPTY_FILTERS });
  }

  const hasActiveFilter = Object.entries(value).some(
    ([k, v]) => k !== "require_open_now" ? Boolean(v) : v === true
  );

  return (
    <div className="card" style={{ display: "grid", gap: "16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0 }}>Filters</h3>
        {hasActiveFilter && (
          <button
            className="btn-outline"
            style={{ padding: "4px 12px", fontSize: "0.8rem", borderRadius: "8px" }}
            onClick={handleReset}
            disabled={disabled}
          >
            Reset
          </button>
        )}
      </div>

      {/* Row 1: Type + Budget */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
        <div>
          <label style={labelStyle}>Type</label>
          <select
            style={selectStyle}
            value={value.entertainment_type}
            onChange={(e) => handleChange("entertainment_type", e.target.value)}
            disabled={disabled}
          >
            <option value="">Any type</option>
            {ENTERTAINMENT_TYPES.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={labelStyle}>Budget</label>
          <select
            style={selectStyle}
            value={value.budget_level}
            onChange={(e) => handleChange("budget_level", e.target.value)}
            disabled={disabled}
          >
            <option value="">Any budget</option>
            {BUDGET_LEVELS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Row 2: Companion + Distance */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
        <div>
          <label style={labelStyle}>Going with</label>
          <select
            style={selectStyle}
            value={value.companion_type}
            onChange={(e) => handleChange("companion_type", e.target.value)}
            disabled={disabled}
          >
            <option value="">Anyone</option>
            {COMPANION_TYPES.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={labelStyle}>Distance</label>
          <select
            style={selectStyle}
            value={value.max_distance_km}
            onChange={(e) => handleChange("max_distance_km", e.target.value)}
            disabled={disabled}
          >
            <option value="">Any distance</option>
            {DISTANCE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Row 3: Min Rating + Open Now */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", alignItems: "end" }}>
        <div>
          <label style={labelStyle}>Min Rating</label>
          <select
            style={selectStyle}
            value={value.min_rating}
            onChange={(e) => handleChange("min_rating", e.target.value)}
            disabled={disabled}
          >
            <option value="">Any rating</option>
            {MIN_RATING_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px", paddingBottom: "4px" }}>
          <input
            type="checkbox"
            id="require_open_now"
            checked={value.require_open_now}
            onChange={(e) => handleChange("require_open_now", e.target.checked)}
            disabled={disabled}
            style={{ width: "18px", height: "18px", cursor: "pointer", accentColor: "var(--color-primary)" }}
          />
          <label
            htmlFor="require_open_now"
            style={{ ...labelStyle, margin: 0, textTransform: "none", fontSize: "0.9rem", cursor: "pointer" }}
          >
            Open now only
          </label>
        </div>
      </div>

      {/* Apply button */}
      <button
        className="btn-primary"
        style={{ width: "100%", padding: "11px", borderRadius: "10px", fontWeight: 700 }}
        onClick={onApply}
        disabled={disabled}
      >
        Apply Filters
      </button>
    </div>
  );
}
