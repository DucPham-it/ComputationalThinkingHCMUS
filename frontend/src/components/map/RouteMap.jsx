/**
 * Route display component.
 *
 * Input:
 * - origin: { lat, lng } starting point
 * - destination: { lat, lng } ending point
 * - waypoints: array of { lat, lng } intermediate stops (optional)
 * - travelMode: "DRIVING" | "WALKING" | "BICYCLING" | "TRANSIT" (default: DRIVING)
 * - onRouteCalculated: callback with route info (distance, duration, steps)
 *
 * Output:
 * - interactive route polyline on map
 * - turn-by-turn directions panel
 */

import { DirectionsRenderer } from "@react-google-maps/api";
import { useState, useEffect } from "react";

export default function RouteMap({
    origin,                 // Starting point
    destination,            // Destination 
    waypoints = [],         // Intermediate stops (default: none)
    travelMode = "DRIVING", // Travel mode
    onRouteCalculated       // Callback to return the calculated route to the parent
}) {
    const [directions, setDirections] = useState(null);
    const [error, setError] = useState(null);

    // Calculate route when origin, destination, or travelMode changes
    useEffect(() => {
        if (!origin || !destination) {
            setDirections(null);
            return;
        }

        // Check if Google Maps API is loaded
        if (!window.google || !window.google.maps) {
            setError("Google Maps chua duoc tai. Vui long thu lai.");
            return;
        }

        setError(null); //delete old error

        // DirectionsService: Google Maps API for calculating routes
        // Each call consumes 1 API request (counts toward your quota)
        const directionsService = new window.google.maps.DirectionsService();

        // Build waypoints array for Directions API
        // true = điểm dừng thật (có chỉ đường), false = chỉ qua
        const waypointsForApi = waypoints.map(wp => ({
            location: new window.google.maps.LatLng(wp.lat, wp.lng),
            stopover: true  // true = stopover (includes directions), false = pass-through
        }));

        // Call the API to calculate the route
        directionsService.route(
            {
                // Convert { lat, lng } into a LatLng object that Google Maps understands
                origin: new window.google.maps.LatLng(origin.lat, origin.lng),
                destination: new window.google.maps.LatLng(destination.lat, destination.lng),
                waypoints: waypointsForApi,
                travelMode: window.google.maps.TravelMode[travelMode],
                optimizeWaypoints: true,
            },
            (result, status) => {
                if (status === "OK") {
                    setDirections(result);

                    // Extract route info
                    const route = result.routes[0];

                    // Calculate total distance and duration for multi-leg routes
                    let totalDistance = 0;  //meter
                    let totalDuration = 0;  //sec
                    const allSteps = [];

                    // Extract step-by-step directions for each leg
                    route.legs.forEach((leg) => {
                        totalDistance += leg.distance.value;
                        totalDuration += leg.duration.value;
                        leg.steps.forEach((step) => {
                            allSteps.push({
                                instructions: step.instructions,
                                distance: step.distance.text,
                                duration: step.duration.text
                            });
                        });
                    });

                    // Package the route information and return it to the parent via callback
                    const info = {
                        distance: formatDistance(totalDistance),
                        duration: formatDuration(totalDuration),
                        steps: allSteps
                    };


                    if (onRouteCalculated) {
                        onRouteCalculated(info);
                    }
                } else { // Route calculation failed — convert the status code into a user-friendly message
                    setError(getErrorMessage(status));
                    setDirections(null);
                }
            }
        );
    }, [origin, destination, waypoints, travelMode, onRouteCalculated]);

    // Show error message
    if (error) {
        return null; // Error handled by parent component
    }

    // Render directions on map
    if (!directions) {
        return null;
    }


    // DirectionsRenderer: automatically renders the route on the map based on `directions`
    // Must be placed INSIDE <GoogleMap> (via MapContainer) to work properly
    return (
        <DirectionsRenderer
            directions={directions}
            options={{
                suppressMarkers: false,
                polylineOptions: {
                    strokeColor: "#4285F4",
                    strokeWeight: 5,
                    strokeOpacity: 0.8
                }
            }}
        />
    );
}

// Helper functions

//m to km
function formatDistance(meters) {
    if (meters >= 1000) {
        return (meters / 1000).toFixed(1) + " km";
    }
    return meters + " m";
}


//s to m to h
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours > 0) {
        return `${hours} gio ${minutes} phut`;
    }
    return `${minutes} phut`;
}

// Convert the Google Maps API status code
// Google returns standardized status codes when route calculation fails
function getErrorMessage(status) {
    const messages = {
        NOT_FOUND: "Khong tim thay duong di giua hai diem nay.",
        ZERO_RESULTS: "Khong co tuyen duong nao kha dung.",
        OVER_QUERY_LIMIT: "Vuot qua gioi han truy van. Vui long thu lai sau.",
        REQUEST_DENIED: "Yeu cau bi tu choi. Kiem tra API key.",
        INVALID_REQUEST: "Yeu cau khong hop le.",
        UNKNOWN_ERROR: "Co loi xay ra. Vui long thu lai."
    };
    return messages[status] || messages.UNKNOWN_ERROR;
}