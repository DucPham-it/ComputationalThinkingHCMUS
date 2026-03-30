import PlaceCard from "../common/PlaceCard";

/**
 * Input props:
 * - places: recommendation result array
 *
 * Output:
 * - list/grid of place cards
 */
export default function RecommendationList({ places = [] }) {
  return (
    <div className="grid grid-3">
      {places.map((place) => (
        <PlaceCard key={place.id} place={place} />
      ))}
    </div>
  );
}
