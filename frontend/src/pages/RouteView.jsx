"use client";

/**
 * Route planning page.
 *
 * Input:
 * - start point and destination
 *
 * Output:
 * - map route, distance, estimated travel time, steps
 */

import MapContainer from "../components/map/MapContainer";
import RouteMap from "../components/map/RouteMap";
import { useState, useCallback } from "react";

// SVG Icons cho travel modes
const TravelModeIcons = {
    DRIVING: "M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z",
    WALKING: "M13.5 5.5c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zM9.8 8.9L7 23h2.1l1.8-8 2.1 2v6h2v-7.5l-2.1-2 .6-3C14.8 12 16.8 13 19 13v-2c-1.9 0-3.5-1-4.3-2.4l-1-1.6c-.4-.6-1-1-1.7-1-.3 0-.5.1-.8.1L6 8.3V13h2V9.6l1.8-.7",
    BICYCLING: "M15.5 5.5c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zM5 12c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8.5c-1.9 0-3.5-1.6-3.5-3.5s1.6-3.5 3.5-3.5 3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5zm5.8-10l2.4 2.4.8-.8c1.3 1.3 3 2.1 5 2.1V12c-1.4 0-2.7-.5-3.8-1.3L13 9.4l-3.3 3.3 2.1 2V19H10v-5.5l-1.2-1.2L7 18H4.5l2.5-6.5 2.8-2.8c.4-.4 1-.6 1.5-.6.6.1 1 .4 1.2.8l.8.8zM19 12c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8.5c-1.9 0-3.5-1.6-3.5-3.5s1.6-3.5 3.5-3.5 3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5z",
    TRANSIT: "M12 2c-4.42 0-8 .5-8 4v9.5C4 17.43 5.57 19 7.5 19L6 20.5v.5h12v-.5L16.5 19c1.93 0 3.5-1.57 3.5-3.5V6c0-3.5-3.58-4-8-4zM7.5 17c-.83 0-1.5-.67-1.5-1.5S6.67 14 7.5 14s1.5.67 1.5 1.5S8.33 17 7.5 17zm3.5-6H6V6h5v5zm5.5 6c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm1.5-6h-5V6h5v5z"
};

const TRAVEL_MODES = [
    { value: "DRIVING", label: "Xe hoi" },
    { value: "WALKING", label: "Di bo" },
    { value: "BICYCLING", label: "Xe dap" },
    { value: "TRANSIT", label: "Cong cong" }
];

export default function RouteView({
    origin = null,
    destination = null,
    waypoints = [],
    onRouteChange
}) {
    //defult travel mode
    const [travelMode, setTravelMode] = useState("DRIVING");
    //route info when caculated
    //null = can't caculated
    const [routeInfo, setRouteInfo] = useState(null);

    // Callback when route is caculated
    const handleRouteCalculated = useCallback((info) => {
        setRouteInfo(info);
        if (onRouteChange) {
            onRouteChange(info);
        }
    }, [onRouteChange]);

    //find center base on origin and destination
    const getMapCenter = () => {
        if (origin) return { lat: origin.lat, lng: origin.lng };
        if (destination) return { lat: destination.lat, lng: destination.lng };
        return { lat: 10.7769, lng: 106.7009 }; // Default: Ho Chi Minh City
    };

    //Data testing for caculate route
    const canShowRoute = origin && destination;

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Travel Mode Selection */}
            <div style={{
                display: "flex",
                gap: "8px",
                padding: "12px",
                background: "#fff",
                borderRadius: "8px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
            }}>
                {TRAVEL_MODES.map(mode => (
                    <button
                        key={mode.value}
                        onClick={() => setTravelMode(mode.value)}
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "6px",
                            padding: "8px 16px",
                            borderRadius: "6px",
                            border: travelMode === mode.value ? "2px solid #2196f3" : "1px solid #ddd",
                            background: travelMode === mode.value ? "#e3f2fd" : "#fff",
                            cursor: "pointer",
                            transition: "all 0.2s"
                        }}
                    >
                        <svg
                            width="18"
                            height="18"
                            viewBox="0 0 24 24"
                            fill={travelMode === mode.value ? "#2196f3" : "#666"}
                        >
                            <path d={TravelModeIcons[mode.value]} />
                        </svg>
                        <span style={{
                            fontSize: "14px",
                            fontWeight: "500",
                            color: travelMode === mode.value ? "#2196f3" : "#666"
                        }}>
                            {mode.label}
                        </span>
                    </button>
                ))}
            </div>

            {/* Map */}
            <MapContainer
                center={getMapCenter()}
                zoom={13}
            >
                {canShowRoute && (
                    <RouteMap
                        origin={{ lat: origin.lat, lng: origin.lng }}
                        destination={{ lat: destination.lat, lng: destination.lng }}
                        waypoints={waypoints}
                        travelMode={travelMode}
                        onRouteCalculated={handleRouteCalculated}
                    />
                )}
            </MapContainer>

            {/* Route Info Summary */}
            {routeInfo && (
                <div style={{
                    display: "flex",
                    gap: "24px",
                    padding: "16px",
                    background: "#f0f9ff",
                    borderRadius: "8px",
                    border: "1px solid #bae6fd"
                }}>
                    <div>
                        <div style={{ fontSize: "12px", color: "#666", marginBottom: "4px" }}>
                            Khoang cach
                        </div>
                        <div style={{ fontSize: "18px", fontWeight: "600", color: "#1a1a1a" }}>
                            {routeInfo.distance}
                        </div>
                    </div>
                    <div>
                        <div style={{ fontSize: "12px", color: "#666", marginBottom: "4px" }}>
                            Thoi gian
                        </div>
                        <div style={{ fontSize: "18px", fontWeight: "600", color: "#1a1a1a" }}>
                            {routeInfo.duration}
                        </div>
                    </div>
                </div>
            )}

            {/* Route Steps */}
            {routeInfo && routeInfo.steps && routeInfo.steps.length > 0 && (
                <div style={{
                    background: "#fff",
                    borderRadius: "8px",
                    padding: "16px",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                    maxHeight: "300px",
                    overflowY: "auto"
                }}>
                    <h3 style={{
                        fontSize: "16px",
                        fontWeight: "600",
                        marginBottom: "12px",
                        color: "#333"
                    }}>
                        Huong dan chi tiet
                    </h3>
                    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                        {routeInfo.steps.map((step, index) => (
                            <div
                                key={index}
                                style={{
                                    display: "flex",
                                    gap: "12px",
                                    paddingBottom: "12px",
                                    borderBottom: index < routeInfo.steps.length - 1 ? "1px solid #eee" : "none"
                                }}
                            >
                                <div style={{
                                    width: "24px",
                                    height: "24px",
                                    borderRadius: "50%",
                                    background: "#2196f3",
                                    color: "#fff",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    fontSize: "12px",
                                    fontWeight: "600",
                                    flexShrink: 0
                                }}>
                                    {index + 1}
                                </div>
                                <div>
                                    <div
                                        style={{ fontSize: "14px", color: "#333" }}
                                        dangerouslySetInnerHTML={{ __html: step.instructions }}
                                    />
                                    <div style={{
                                        fontSize: "12px",
                                        color: "#666",
                                        marginTop: "4px"
                                    }}>
                                        {step.distance} - {step.duration}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* annonce when have no data */}
            {!canShowRoute && (
                <div style={{
                    padding: "24px",
                    background: "#f5f5f5",
                    borderRadius: "8px",
                    textAlign: "center",
                    color: "#666"
                }}>
                    Vui long chon diem bat dau va diem den de xem lo trinh
                </div>
            )}
        </div>
    );
}