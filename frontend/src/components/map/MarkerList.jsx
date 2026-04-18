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
import { useState, useCallback, useEffect } from "react";
import PlacePopupCard from "./PlacePopupCard";

function buildMarkerIcon(color, scale = 9) {
    if (!window.google?.maps) {
        return undefined;
    }

    return {
        path: window.google.maps.SymbolPath.CIRCLE,
        scale,
        fillColor: color,
        fillOpacity: 1,
        strokeColor: "#ffffff",
        strokeWeight: 2,
    };
}

export default function MarkerList({
    places = [],
    onPlaceSelect,
    onPickPlace,
    onViewPlace,
    onSavePlace,
    onDismissPlace,
    primaryActionLabel,
    selectedPlaceId,
    selectionModeLabel,
    cancelActionLabel,
}) { //onPlaceSelect: Callback to notify the parent when the user clicks a marker
    const [selected, setSelected] = useState(null);
    const markerIcon = buildMarkerIcon("#dc2626");
    const selectedMarkerIcon = buildMarkerIcon("#f59e0b", 10);

    useEffect(() => {
        if (!selectedPlaceId) {
            setSelected(null);
            return;
        }

        const matchedPlace = places.find((place) => place.id === selectedPlaceId);
        if (matchedPlace) {
            setSelected(matchedPlace);
            return;
        }
        setSelected(null);
    }, [places, selectedPlaceId]);

    const handleMarkerClick = useCallback((place) => {
        setSelected(place);
        if (onPlaceSelect) onPlaceSelect(place);
    }, [onPlaceSelect]);

    const handleCloseClick = useCallback(() => {
        if (selected && onDismissPlace) {
            onDismissPlace(selected);
        }
        setSelected(null);
    }, [onDismissPlace, selected]);

    // Early return if no places
    if (!places || places.length === 0) {
        return null;
    }

    return (
        <>
            {places.map((place) => {
                const lat = place.lat ?? place.latitude;
                const lng = place.lng ?? place.longitude;

                if (lat == null || lng == null) {
                    return null;
                }

                return (
                    <Marker
                        key={place.id}
                        position={{ lat, lng }}
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
                                <PlacePopupCard
                                    place={place}
                                    onViewPlace={onViewPlace}
                                    onSavePlace={onSavePlace}
                                    onPrimaryAction={onPickPlace}
                                    onCancelSelection={onDismissPlace ? handleCloseClick : undefined}
                                    primaryActionLabel={primaryActionLabel}
                                    selectionModeLabel={selectionModeLabel}
                                    cancelActionLabel={cancelActionLabel}
                                />
                            </InfoWindow>
                        )}
                    </Marker>
                );
            })}
        </>
    );
}
