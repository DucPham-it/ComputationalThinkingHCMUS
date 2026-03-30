import { formatRating } from "../../utils/formatter";

/**
 * Recommendation card.
 *
 * Input props:
 * - place: summary place object from backend
 *
 * Output:
 * - visual card with fields you requested in UI
 */
export default function PlaceCard({ place }) {
  return (
    <div className="card">
      <h3>{place.name}</h3>
      <p>{place.address}</p>
      <p>Rating: {formatRating(place.rating)}</p>
      <p>Distance: {place.distance_km ?? "N/A"} km</p>
      <p>Price level: {place.price_level ?? "N/A"}</p>
      <p>Open now: {place.open_now === null || place.open_now === undefined ? "N/A" : String(place.open_now)}</p>
      <p>Type: {place.primary_type ?? "N/A"}</p>
      <p>Score: {place.score ?? "N/A"}</p>
      <button>View detail</button>
    </div>
  );
}
