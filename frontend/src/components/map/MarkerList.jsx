/**
 * Marker list component for Leaflet.
 */

import { CircleMarker, Popup } from "react-leaflet";
import { useState, useCallback, useEffect } from "react";
import PlacePopupCard from "./PlacePopupCard";

function buildMarkerStyle(color, radius = 9) {
  return {
    radius,
    pathOptions: {
      color: "#ffffff",
      weight: 2,
      fillColor: color,
      fillOpacity: 1,
    },
  };
}

export default function MarkerList({
  places = [],
  onPlaceSelect,
  onPickPlace,
  onViewPlace,
  onSavePlace,
  onSuggestChange,
  onDismissPlace,
  primaryActionLabel,
  selectedPlaceId,
  selectionModeLabel,
  cancelActionLabel,
}) {
  const [selected, setSelected] = useState(null);
  const markerStyle = buildMarkerStyle("#dc2626");
  const selectedMarkerStyle = buildMarkerStyle("#f59e0b", 10);

  useEffect(() => {
    if (!selectedPlaceId) {
      setSelected(null);
      return;
    }

    const matchedPlace = places.find((place) => place.id === selectedPlaceId);
    setSelected(matchedPlace || null);
  }, [places, selectedPlaceId]);

  const handleMarkerClick = useCallback(
    (place) => {
      setSelected(place);
      onPlaceSelect?.(place);
    },
    [onPlaceSelect]
  );

  const handleCloseClick = useCallback(() => {
    if (selected && onDismissPlace) {
      onDismissPlace(selected);
    }
    setSelected(null);
  }, [onDismissPlace, selected]);

  if (!places.length) {
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

        const markerAppearance =
          selected?.id === place.id ? selectedMarkerStyle : markerStyle;

        return (
          <CircleMarker
            key={place.id}
            center={[lat, lng]}
            radius={markerAppearance.radius}
            pathOptions={markerAppearance.pathOptions}
            eventHandlers={{
              click: () => handleMarkerClick(place),
              popupclose: handleCloseClick,
            }}
          >
            {selected?.id === place.id ? (
              <Popup closeButton>
                <PlacePopupCard
                  place={place}
                  onViewPlace={onViewPlace}
                  onSavePlace={onSavePlace}
                  onSuggestChange={onSuggestChange}
                  onPrimaryAction={onPickPlace}
                  onCancelSelection={onDismissPlace ? handleCloseClick : undefined}
                  primaryActionLabel={primaryActionLabel}
                  selectionModeLabel={selectionModeLabel}
                  cancelActionLabel={cancelActionLabel}
                />
              </Popup>
            ) : null}
          </CircleMarker>
        );
      })}
    </>
  );
}
