/**
 * Recommendation filters.
 *
 * Current state:
 * - static UI only
 *
 * TODO:
 * - lift state to Home page
 * - send budget, distance, weather preference, type, time slot to backend
 */
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
