/**
 * Input props:
 * - markers: array of place markers
 *
 * Output:
 * - simple debug list of markers
 */
export default function MarkerList({ markers = [] }) {
  return (
    <div className="card">
      <h3>Markers</h3>
      <ul>
        {markers.map((marker) => (
          <li key={marker.id}>{marker.name}</li>
        ))}
      </ul>
    </div>
  );
}
