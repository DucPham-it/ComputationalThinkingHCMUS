/**
 * Marker list component.
 *
 * Input:
 * - places: list of places with coordinates
 * - onPlaceSelect: callback when a place is selected (optional)
 *
 * Output:
 * - rendered markers on map with InfoWindow
 */

import { Marker, InfoWindow } from "@react-google-maps/api";
import { useState, useCallback } from "react";

// Star icon SVG component
const StarIcon = () => (
    <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="#facc15"
        style={{ flexShrink: 0 }}
    >
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
    </svg>
);

// Location pin icon SVG component
const LocationIcon = () => (
    <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="#ef4444"
        style={{ flexShrink: 0 }}
    >
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" />
    </svg>
);

// Custom marker icons
const markerIcon = {
    url: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
    scaledSize: { width: 40, height: 40 },
};

const selectedMarkerIcon = {
    url: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
    scaledSize: { width: 48, height: 48 },
};

export default function MarkerList({ places = [], onPlaceSelect }) { //onPlaceSelect: Callback to notify the parent when the user clicks a marker
    const [selected, setSelected] = useState(null);

    const handleMarkerClick = useCallback((place) => {
        setSelected(place);
        if (onPlaceSelect) onPlaceSelect(place);
    }, [onPlaceSelect]);

    const handleCloseClick = useCallback(() => {
        setSelected(null);
    }, []);

    // Early return if no places
    if (!places || places.length === 0) {
        return null;
    }

    return (
        <>
            {places.map((place) => (
                <Marker
                    key={place.id}
                    position={{ lat: place.lat, lng: place.lng }}
                    onClick={() => handleMarkerClick(place)}
                    icon={selected?.id === place.id ? selectedMarkerIcon : markerIcon} // Change the icon based on state: green if selected, red if default
                    animation={selected?.id === place.id ? 1 : undefined} // Animation bounce when marker is selected
                    title={place.name}
                >
                    {selected?.id === place.id && (
                        <InfoWindow
                            onCloseClick={handleCloseClick}
                            options={{ maxWidth: 250 }}
                        >
                            <div style={{ padding: "8px", minWidth: "150px" }}>
                                <h3 style={{
                                    margin: "0 0 8px 0",
                                    fontSize: "16px",
                                    fontWeight: "600",
                                    color: "#1a1a1a"
                                }}>
                                    {place.name}
                                </h3>
                                { /* Rating and distance — only show if data is available */ }
                                <div style={{
                                    display: "flex",
                                    gap: "12px",
                                    fontSize: "14px",
                                    color: "#666"
                                }}>
                                    { /* Only render if place.rating exists (not null/undefined/0) */ }
                                    {place.rating && (
                                        <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                                            <StarIcon />
                                            {place.rating}
                                        </span>
                                    )}
                                    {place.distance_km && (
                                        <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                                            <LocationIcon />
                                            {place.distance_km} km
                                        </span>
                                    )}
                                </div>
                                {place.address && (
                                    <p style={{
                                        margin: "8px 0 0 0",
                                        fontSize: "12px",
                                        color: "#888"
                                    }}>
                                        {place.address}
                                    </p>
                                )}
                            </div>
                        </InfoWindow>
                    )}
                </Marker>
            ))}
        </>
    );
}
