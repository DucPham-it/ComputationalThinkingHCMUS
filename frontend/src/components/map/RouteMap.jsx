/**
 * Route polyline renderer driven entirely by backend route data.
 */

import { Polyline } from "react-leaflet";

export default function RouteMap({ path = [] }) {
  if (!Array.isArray(path) || path.length < 2) {
    return null;
  }

  return (
    <Polyline
      positions={path.map((point) => [point.lat, point.lng])}
      pathOptions={{
        color: "#2563eb",
        weight: 5,
        opacity: 0.82,
      }}
    />
  );
}
