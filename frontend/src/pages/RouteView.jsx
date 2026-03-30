import RouteMap from "../components/map/RouteMap";

/**
 * Route planning page.
 *
 * Input:
 * - start point and destination
 *
 * Output:
 * - map route, distance, estimated travel time, steps
 */
export default function RouteView() {
  return (
    <div className="grid">
      <h1>Route Planner</h1>
      <RouteMap />
    </div>
  );
}
