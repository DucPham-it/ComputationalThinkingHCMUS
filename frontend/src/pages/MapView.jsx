"use client";

/**
 * Map page.
 *
 * Intended purpose:
 * - show current user location
 * - show recommended place markers
 * - support marker click to open detail
 */

import MapContainer from "../components/map/MapContainer";
import MarkerList from "../components/map/MarkerList";
import { useState, useEffect } from "react";

export default function MapView({ places = [] }) {
    const [selectedPlace, setSelectedPlace] = useState(null);
    const [userLocation, setUserLocation] = useState(null);
    const [mapCenter, setMapCenter] = useState({ lat: 10.7769, lng: 106.7009 });

    // Get user's position when mount
    useEffect(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const userPos = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    setUserLocation(userPos);
                    setMapCenter(userPos);
                },
                (error) => {
                    console.log("Geolocation error:", error.message);
                }
            );
        }
    }, []);

    // when select a place
    const handlePlaceSelect = (place) => {
        const lat = place.lat ?? place.latitude;
        const lng = place.lng ?? place.longitude;

        setSelectedPlace(place);
        if (lat != null && lng != null) {
            setMapCenter({ lat, lng });
        }
    };

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Map */}
            <MapContainer
                center={mapCenter}
                zoom={13}
            >
                <MarkerList
                    places={places}
                    onPlaceSelect={handlePlaceSelect}
                />
            </MapContainer>

            {/* show selected postion's information*/}
            {selectedPlace && (
                <div style={{
                    padding: "16px",
                    background: "#fff",
                    borderRadius: "8px",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
                }}>
                    <h3 style={{ fontSize: "18px", fontWeight: "600", marginBottom: "8px" }}>
                        {selectedPlace.name}
                    </h3>
                    {selectedPlace.address && (
                        <p style={{ color: "#666", marginBottom: "8px" }}>
                            {selectedPlace.address}
                        </p>
                    )}
                    <div style={{ display: "flex", gap: "16px", color: "#666" }}>
                        {selectedPlace.rating && <span>Rating: {selectedPlace.rating}</span>}
                        {selectedPlace.distance_km && <span>Distance: {selectedPlace.distance_km} km</span>}
                    </div>
                </div>
            )}
        </div>
    );
}
