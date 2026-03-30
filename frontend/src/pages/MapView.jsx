import MapContainer from "../components/map/MapContainer";

/**
 * Map page.
 *
 * Intended purpose:
 * - show current user location
 * - show recommended place markers
 * - support marker click to open detail
 */
export default function MapView() {
  return (
    <div className="grid">
      <h1>Map View</h1>
      <MapContainer />
    </div>
  );
}
