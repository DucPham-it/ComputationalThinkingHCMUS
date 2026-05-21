"use client";

/**
 * Map page.
 *
 * Owner:
 * - TV6: Map Pick To Route.
 *
 * File input:
 * - AppContext.recommendationPlaces plus optional places prop.
 * - Browser GPS/currentLocation from AppContext.
 * - User clicks on markers or free map coordinates.
 *
 * File output:
 * - AppContext.selectedPlace for RouteView.
 * - Navigation to /route after destination pick.
 * - Optional POST /recommendations/picks/{place_id} for database-backed places.
 *
 * Intended purpose:
 * - show current user location.
 * - show recommended place markers.
 * - support marker click to open detail or pick as route destination.
 */

import MapContainer from "../components/map/MapContainer";
import MarkerList from "../components/map/MarkerList";
import PlaceRequestForm from "../components/map/PlaceRequestForm";
import { useState, useEffect, useMemo } from "react";
import { CircleMarker, Tooltip } from "react-leaflet";
import { useNavigate } from "react-router-dom";
import { useApp } from "../hooks/useApp";
import { getCurrentBrowserLocation } from "../utils/geolocation";
import { mergePlacesByKey } from "../utils/placeCollection";
import { addFavorite } from "../services/favoriteService";
import { recordPlacePick, resolvePlaceFromCoordinates } from "../services/mapPickService";

function buildTemporaryMapPlace(point, address = null) {
    /**
     * Owner:
     * - TV6.
     *
     * Input:
     * - point: map click point with latitude/longitude.
     * - address: optional resolved address text.
     *
     * Output:
     * - temporary place-like object that can be shown on map and picked for route.
     * - flags mark it as local-only, not viewable, and not saveable.
     */
    const fallbackAddress = address || `${point.latitude.toFixed(5)}, ${point.longitude.toFixed(5)}`;
    return {
        id: `temp-map-${point.latitude}-${point.longitude}-${Date.now()}`,
        name: "Pinned point",
        address: fallbackAddress,
        latitude: point.latitude,
        longitude: point.longitude,
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

function getDatabasePlaceId(place) {
    /**
     * Owner:
     * - TV6.
     *
     * Input:
     * - place: marker/resolved place object.
     *
     * Output:
     * - positive integer database id when available.
     * - null for temporary map points or external-only places.
     */
    const numericId = Number(place?.id);
    return Number.isInteger(numericId) && numericId > 0 ? numericId : null;
}

export function buildRouteDestinationFromMapPick(place) {
    /**
     * TODO TV6: normalize a map marker/place into route destination state.
     *
     * Owner:
     * - TV6.
     *
     * Input:
     * - place: marker payload from MarkerList or resolved map click:
     *   - id: database place id or temporary id
     *   - name: display name
     *   - address: address text
     *   - latitude/longitude
     *   - photo_url, primary_type, can_view, can_save when available
     *
     * Output:
     * - object for AppContext.selectedPlace:
     *   { place_id, id, name, address, latitude, longitude, photo_url,
     *     primary_type, source, can_view, can_save }
     *
     * Rule:
     * - Database-backed place should call recordPlacePick(place.id).
     * - Temporary map point should still navigate to Route, but cannot be saved/viewed.
     */
    const latitude = place?.latitude ?? place?.lat;
    const longitude = place?.longitude ?? place?.lng;

    if (latitude == null || longitude == null) {
        throw new Error("Missing coordinates");
    }

    const databasePlaceId = getDatabasePlaceId(place);
    const isTemporary = place?._isTemporaryMapSelection === true;

    return {
        place_id: databasePlaceId,
        id: place.id || `temp-map-${latitude}-${longitude}-${Date.now()}`,
        name: place.name || "Custom destination",
        address: place.address || null,
        latitude,
        longitude,
        photo_url: place.photo_url || null,
        primary_type: place.primary_type || place.category || null,
        source: isTemporary ? "map_click" : "map_marker",
        can_view: place.can_view ?? place._canView ?? databasePlaceId !== null,
        can_save: place.can_save ?? place._canSave ?? databasePlaceId !== null,
    };
}

export default function MapView({ places = [] }) {
    const navigate = useNavigate();
    const {
        currentLocation,
        setCurrentLocation,
        recommendationPlaces,
        setRecommendationPlaces,
        setSelectedPlace: setPickedPlace,
        hasSearched,
    } = useApp();
    const [mapCenter, setMapCenter] = useState(() => currentLocation || { latitude: 10.7769, longitude: 106.7009 });
    const [selectedPlaceId, setSelectedPlaceId] = useState(null);
    const [requestTargetPlace, setRequestTargetPlace] = useState(null);
    const mapPlaces = useMemo(
        () => mergePlacesByKey(recommendationPlaces, places),
        [places, recommendationPlaces]
    );
    const mapFitBoundsPoints = useMemo(() => {
        if (!hasSearched) {
            return [];
        }
        return mapPlaces.filter(p => !p._isTemporaryMapSelection);
    }, [hasSearched, mapPlaces]);

    function mergePlaces(nextPlace) {
        const mergedPlaces = mergePlacesByKey([nextPlace], mapPlaces);
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
    }, [setCurrentLocation]);

    // when select a place
    const handlePlaceSelect = (place) => {
        const latitude = place.latitude ?? place.lat;
        const longitude = place.longitude ?? place.lng;

        setSelectedPlaceId(place.id);
        if (latitude != null && longitude != null) {
            setMapCenter({ latitude, longitude });
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
        
        let destination;
        try {
            destination = buildRouteDestinationFromMapPick(place);
        } catch (error) {
            alert("This marker is missing coordinates. Cannot navigate to route.");
            return;
        }

        const databasePlaceId = getDatabasePlaceId(place);
        if (databasePlaceId !== null) {
            recordPlacePick(databasePlaceId).catch((error) => {
                console.error("Failed to record place pick", error);
            });
        }

        confirmPlace(place);
        setPickedPlace(destination);
        navigate("/route");
    }

    function handleSuggestChange(place) {
        setRequestTargetPlace(place);
    }

    async function handleMapClick(point) {
        // Clear any existing temporary map selection pins first to prevent clutter
        const fallbackPlace = buildTemporaryMapPlace(point);
        setRecommendationPlaces((prevPlaces) => {
            const cleared = prevPlaces.filter((item) => !item._isTemporaryMapSelection);
            return [fallbackPlace, ...cleared];
        });
        setSelectedPlaceId(fallbackPlace.id);

        try {
            const resolvedPlace = await resolvePlaceFromCoordinates({
                latitude: point.latitude,
                longitude: point.longitude,
            });
            
            setRecommendationPlaces((prevPlaces) => {
                const filtered = prevPlaces.filter(
                    (item) => item.id !== fallbackPlace.id && !item._isTemporaryMapSelection
                );
                const alreadyListed = mapPlaces.some((place) => place.id === resolvedPlace.id);
                const previewPlace = {
                    ...resolvedPlace,
                    _isTemporaryMapSelection: !alreadyListed,
                };
                return [previewPlace, ...filtered];
            });
            setSelectedPlaceId((prevId) => (prevId === fallbackPlace.id ? resolvedPlace.id : prevId));
        } catch (error) {
            console.error("Failed to resolve clicked point", error);
            // Fallback is already showing, nothing to do
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
                fitBoundsPoints={mapFitBoundsPoints}
                onRecenter={(pos) => setMapCenter(pos)}
            >
                {currentLocation ? (
                    <CircleMarker
                        center={[currentLocation.latitude, currentLocation.longitude]}
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
