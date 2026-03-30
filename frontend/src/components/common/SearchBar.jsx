/**
 * Search input component.
 *
 * Input props:
 * - value: current query string
 * - onChange: callback(newValue)
 * - onSubmit: callback() when user clicks search
 *
 * Output:
 * - search UI element only, no direct API calls inside component
 */
export default function SearchBar({ value = "", onChange, onSubmit }) {
  return (
    <div className="card row">
      <input
        type="text"
        placeholder="Search destination, food, cinema, shopping..."
        value={value}
        onChange={(event) => onChange?.(event.target.value)}
      />
      <button onClick={onSubmit}>Search</button>
    </div>
  );
}
