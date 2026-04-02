/**
 * Placeholder for Google Maps JavaScript map.
 *
 * Input later:
 * - center coordinates
 * - place markers
 * - selected route polyline
 *
 * Output:
 * - rendered interactive map
 */
import { Marker, InfoWindow } from "@react-google-maps/api";
import { useState } from "react";

export default function MarkerList({ places }) {
    const [selected, setSelected] = useState(null);

    return (
        <>
            {places.map((place) => (
                <Marker
                    key={place.id}
                    position={{ lat: place.lat, lng: place.lng }}
                    onClick={() => setSelected(place)}
                />
            ))}

            {selected && (
                <InfoWindow
                    position={{ lat: selected.lat, lng: selected.lng }}
                    onCloseClick={() => setSelected(null)}
                >
                    <div>
                        <h3>{selected.name}</h3>
                        <p>⭐ {selected.rating} | {selected.distance_km} km</p>
                    </div>
                </InfoWindow>
            )}
        </>
    );
}