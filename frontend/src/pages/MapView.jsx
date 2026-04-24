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
import PlaceRequestForm from "../components/map/PlaceRequestForm";
import { useState, useEffect } from "react";
import { CircleMarker, Tooltip } from "react-leaflet";
import { useNavigate } from "react-router-dom";
import { useApp } from "../hooks/useApp";
import { getCurrentBrowserLocation } from "../utils/geolocation";
import { addFavorite } from "../services/favoriteService";
import { recordPlacePick, resolvePlaceFromCoordinates } from "../services/placeService";

function buildTemporaryMapPlace(point, address = null) {
    const fallbackAddress = address || `${point.lat.toFixed(5)}, ${point.lng.toFixed(5)}`;
    return {
        id: `temp-map-${point.lat}-${point.lng}-${Date.now()}`,
        name: "Pinned point",
        address: fallbackAddress,
        latitude: point.lat,
        longitude: point.lng,
        photo_url: null,
        rating: null,
        review_count: 0,
        distance_km: null,
        _isTemporaryMapSelection: true,
        _isLocalOnly: true,
        _canView: false,
        _canSave: false,
    };
}

function sanitizePickedPlace(place) {
    if (!place) {
        return place;
    }

    const {
        _isTemporaryMapSelection,
        _isLocalOnly,
        _canView,
        _canSave,
        ...cleanPlace
    } = place;
    return cleanPlace;
}

function getDatabasePlaceId(place) {
    const numericId = Number(place?.id);
    return Number.isInteger(numericId) && numericId > 0 ? numericId : null;
}

export default function MapView({ places = [] }) {
    const navigate = useNavigate();
    const {
        currentLocation,
        setCurrentLocation,
        recommendationPlaces,
        setRecommendationPlaces,
        setSelectedPlace: setPickedPlace,
    } = useApp();
    const [mapCenter, setMapCenter] = useState({ lat: 10.7769, lng: 106.7009 });
    const [selectedPlaceId, setSelectedPlaceId] = useState(null);
    const [requestTargetPlace, setRequestTargetPlace] = useState(null);
    const mapPlaces = places.length ? places : recommendationPlaces;

    function mergePlaces(nextPlace) {
        const sourcePlaces = places.length ? places : recommendationPlaces;
        const mergedPlaces = [nextPlace, ...sourcePlaces.filter((place) => place.id !== nextPlace.id)];
        setRecommendationPlaces(mergedPlaces);
        return mergedPlaces;
    }

    function dismissPlace(place) {
        setSelectedPlaceId(null);

        if (!place?._isTemporaryMapSelection) {
            return;
        }

        setRecommendationPlaces((previousPlaces) =>
            previousPlaces.filter((item) => item.id !== place.id)
        );
    }

    function confirmPlace(place) {
        if (place._isTemporaryMapSelection) {
            setRecommendationPlaces((previousPlaces) =>
                previousPlaces.filter((item) => item.id !== place.id)
            );
        }
    }

    // Get user's position when mount
    useEffect(() => {
        let active = true;

        async function hydrateLocation() {
            if (currentLocation) {
                setMapCenter(currentLocation);
                return;
            }

            try {
                const userPos = await getCurrentBrowserLocation();
                if (!active) return;
                setCurrentLocation(userPos);
                setMapCenter(userPos);
            } catch (error) {
                console.log("Geolocation error:", error.message);
            }
        }

        hydrateLocation();
        return () => {
            active = false;
        };
    }, [currentLocation, setCurrentLocation]);

    // when select a place
    const handlePlaceSelect = (place) => {
        const lat = place.lat ?? place.latitude;
        const lng = place.lng ?? place.longitude;

        setSelectedPlaceId(place.id);
        if (lat != null && lng != null) {
            setMapCenter({ lat, lng });
        }
    };

    async function handleSavePlace(place) {
        const databasePlaceId = getDatabasePlaceId(place);
        if (place._canSave === false || place.can_save === false || databasePlaceId === null) {
            return;
        }

        try {
            await addFavorite(databasePlaceId);
            confirmPlace(place);
        } catch (error) {
            console.error("Failed to save place", error);
        }
    }

    function handleViewPlace(place) {
        const databasePlaceId = getDatabasePlaceId(place);
        if (place._canView === false || place.can_view === false || databasePlaceId === null) {
            return;
        }
        navigate(`/places/${databasePlaceId}`);
    }

    function handlePickPlace(place) {
        const databasePlaceId = getDatabasePlaceId(place);
        if (databasePlaceId !== null) {
            recordPlacePick(databasePlaceId).catch((error) => {
                console.error("Failed to record place pick", error);
            });
        }

        confirmPlace(place);
        setPickedPlace(sanitizePickedPlace(place));
        navigate("/route");
    }

    function handleSuggestChange(place) {
        setRequestTargetPlace(place);
    }

    async function handleMapClick(point) {
        try {
            const resolvedPlace = await resolvePlaceFromCoordinates({
                latitude: point.lat,
                longitude: point.lng,
            });
            const alreadyListed = mapPlaces.some((place) => place.id === resolvedPlace.id);
            const previewPlace = {
                ...resolvedPlace,
                _isTemporaryMapSelection: !alreadyListed,
            };
            mergePlaces(previewPlace);
            setSelectedPlaceId(previewPlace.id);
            if (
                typeof resolvedPlace.latitude === "number" &&
                typeof resolvedPlace.longitude === "number"
            ) {
                setMapCenter({
                    lat: resolvedPlace.latitude,
                    lng: resolvedPlace.longitude,
                });
            }
        } catch (error) {
            const fallbackPlace = buildTemporaryMapPlace(point);
            mergePlaces(fallbackPlace);
            setSelectedPlaceId(fallbackPlace.id);
            setMapCenter(point);
            console.error("Failed to resolve clicked point", error);
        }
    }

    const userMarkerStyle = {
        radius: 8,
        pathOptions: {
            color: "#ffffff",
            weight: 2,
            fillColor: "#2563eb",
            fillOpacity: 1,
        },
    };

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Map */}
            <MapContainer
                center={mapCenter}
                zoom={13}
                onMapClick={handleMapClick}
            >
                {currentLocation ? (
                    <CircleMarker
                        center={[currentLocation.lat, currentLocation.lng]}
                        radius={userMarkerStyle.radius}
                        pathOptions={userMarkerStyle.pathOptions}
                    >
                        <Tooltip>Your current location</Tooltip>
                    </CircleMarker>
                ) : null}
                <MarkerList
                    places={mapPlaces}
                    onPlaceSelect={handlePlaceSelect}
                    onViewPlace={handleViewPlace}
                    onSavePlace={handleSavePlace}
                    onPickPlace={handlePickPlace}
                    onSuggestChange={handleSuggestChange}
                    onDismissPlace={dismissPlace}
                    primaryActionLabel="Pick destination"
                    selectedPlaceId={selectedPlaceId}
                    selectionModeLabel="Preview on map"
                    cancelActionLabel="Cancel pin"
                />
            </MapContainer>
            <PlaceRequestForm
                targetPlace={requestTargetPlace}
                onCancel={() => setRequestTargetPlace(null)}
            />
        </div>
    );
}
