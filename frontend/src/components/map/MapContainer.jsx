/**
 * Map container component with Google Maps integration.
 *
 * Input:
 * - children: child components (MarkerList, RouteMap, etc.)
 * - center: { lat, lng } map center point
 * - zoom: zoom level (default: 14)
 * - onMapLoad: callback when map is loaded
 * - onMapClick: callback when map is clicked
 *
 * Output:
 * - Google Map with children rendered inside
 */

import { GoogleMap, useLoadScript } from "@react-google-maps/api";
import { useMemo, useCallback } from "react";

// Default map container style
const mapContainerStyle = {
    width: "100%",
    height: "500px",
    borderRadius: "8px"
};

// Default center:
const defaultCenter = { lat: 10.9804, lng: 106.6519 };

// Libraries needed for Directions API, Places, and Geometry
// "places"  → dùng cho Places API (tìm kiếm địa điểm)
// "geometry" → dùng để tính khoảng cách, vẽ hình học
const LIBRARIES = ["places", "geometry"];

// Map options
const defaultMapOptions = {
    zoomControl: true,
    streetViewControl: false,
    mapTypeControl: false,
    fullscreenControl: true,
    styles: [
        {
            //Hide google's poi
            featureType: "poi",
            elementType: "labels",
            stylers: [{ visibility: "off" }]
        }
    ]
};

export default function MapContainer({
    children,   //child component render inside map(MarkerList, RouteMap...)
    center,
    zoom = 14,
    onMapLoad,  //callback when map is loaded
    onMapClick, //callbalck when click on map
    mapContainerClassName = "",
    options = {}
}) {
    // Memoize libraries array to prevent re-renders
    const libraries = useMemo(() => LIBRARIES, []);

    //return isLoaded=true when scripts is ready, loadError when fail
    const { isLoaded, loadError } = useLoadScript({
        googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_KEY,
        libraries,
    });

    // Memoize map options
    const mapOptions = useMemo(() => ({
        ...defaultMapOptions,
        ...options
    }), [options]);

    // Handle map load callback
    const handleMapLoad = useCallback((map) => {
        if (onMapLoad) onMapLoad(map);
    }, [onMapLoad]);

    // Handle map click callback
    const handleMapClick = useCallback((event) => {
        if (onMapClick) {
            onMapClick({
                lat: event.latLng.lat(),
                lng: event.latLng.lng()
            });
        }
    }, [onMapClick]);

    // Error state: Google Maps script failed to load 
    // Usually caused by an invalid API key, exceeded quota, or no internet connection
    if (loadError) {
        return (
            <div className="card" style={styles.card}>
                <h3 style={styles.title}>Ban do</h3>
                <div style={styles.errorContainer}>
                    <ErrorIcon />
                    <p style={styles.errorText}>
                        Khong the tai ban do. Vui long kiem tra ket noi mang va thu lai.
                    </p>
                </div>
            </div>
        );
    }

    // Loading state: script is not ready yet  
    // Show a spinner to indicate that the content is loading
    if (!isLoaded) {
        return (
            <div className="card" style={styles.card}>
                <h3 style={styles.title}>Ban do</h3>
                <div style={styles.loadingContainer}>
                    <div style={styles.spinner}></div>
                    <p style={styles.loadingText}>Dang tai ban do...</p>
                </div>
                <style>{spinnerKeyframes}</style>
            </div>
        );
    }

    return (
        <div className={`card ${mapContainerClassName}`} style={styles.card}>
            <GoogleMap
                mapContainerStyle={mapContainerStyle}
                zoom={zoom}
                center={center || defaultCenter}    // use defaultCenter if cent = null
                onLoad={handleMapLoad}
                onClick={handleMapClick}
                options={mapOptions}
            >
                {children}  {/* children render inside map(MarkerList, RouteMap...) */}
            </GoogleMap>
        </div>
    );
}

// Error icon SVG - show when map can't load
const ErrorIcon = () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="#dc2626">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
    </svg>
);

// Keyframes for spinner loading
const spinnerKeyframes = `
    @keyframes spin {
        to { transform: rotate(360d eg); }
    }
`;

// Styles
const styles = {
    card: {
        backgroundColor: "#fff",
        borderRadius: "12px",
        overflow: "hidden",
        boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
    },
    title: {
        margin: 0,
        padding: "16px",
        fontSize: "18px",
        fontWeight: "600",
        color: "#1a1a1a",
        borderBottom: "1px solid #eee"
    },
    loadingContainer: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "400px",
        gap: "16px"
    },
    spinner: {
        width: "40px",
        height: "40px",
        border: "3px solid #f0f0f0",
        borderTopColor: "#4285F4",
        borderRadius: "50%",
        animation: "spin 1s linear infinite"
    },
    loadingText: {
        color: "#666",
        fontSize: "14px",
        margin: 0
    },
    errorContainer: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "400px",
        gap: "16px",
        padding: "24px"
    },
    errorText: {
        color: "#dc2626",
        fontSize: "14px",
        textAlign: "center",
        margin: 0
    }
};