import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchPlaceDetail } from "../services/placeService";

/**
 * Place detail page.
 *
 * Input:
 * - route param id
 *
 * Output:
 * - detail block with address, description, hours, images, reviews summary
 */
export default function PlaceDetail() {
  const { id } = useParams();
  const [place, setPlace] = useState(null);

  useEffect(() => {
    fetchPlaceDetail(id).then(setPlace).catch(console.error);
  }, [id]);

  return (
    <div className="card">
      <h1>Place Detail</h1>
      <p>Selected place id: {id}</p>
      {place && (
        <>
          <p>Name: {place.name}</p>
          <p>Address: {place.address}</p>
          <p>Rating: {place.rating ?? "N/A"}</p>
          <p>Description: {place.description ?? "N/A"}</p>
        </>
      )}
    </div>
  );
}
