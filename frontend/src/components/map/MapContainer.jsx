/**
 * Leaflet map container using OpenStreetMap tiles.
 */

import { MapContainer as LeafletMapContainer, TileLayer, useMap, useMapEvents } from "react-leaflet";
import { useEffect } from "react";

const mapContainerStyle = {
  width: "100%",
  height: "500px",
  borderRadius: "8px",
};

const defaultCenter = { latitude: 10.9804, longitude: 106.6519 };

function resolveCoordinate(point, primaryKey, legacyKey) {
  return point?.[primaryKey] ?? point?.[legacyKey];
}

function MapUpdater({ center, zoom }) {
  const map = useMap();

  useEffect(() => {
    if (!center) {
      return;
    }
    map.setView(
      [
        resolveCoordinate(center, "latitude", "lat"),
        resolveCoordinate(center, "longitude", "lng"),
      ],
      zoom,
      { animate: true }
    );
  }, [center, map, zoom]);

  return null;
}

function MapClickHandler({ onMapClick }) {
  useMapEvents({
    click(event) {
      if (!onMapClick) {
        return;
      }
      onMapClick({
        latitude: event.latlng.lat,
        longitude: event.latlng.lng,
      });
    },
  });

  return null;
}

export default function MapContainer({
  children,
  center,
  zoom = 14,
  onMapClick,
  mapContainerClassName = "",
}) {
  const resolvedCenter = center || defaultCenter;

  return (
    <div className={`card ${mapContainerClassName}`} style={styles.card}>
      <LeafletMapContainer
        center={[
          resolveCoordinate(resolvedCenter, "latitude", "lat"),
          resolveCoordinate(resolvedCenter, "longitude", "lng"),
        ]}
        zoom={zoom}
        scrollWheelZoom
        style={mapContainerStyle}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapUpdater center={resolvedCenter} zoom={zoom} />
        <MapClickHandler onMapClick={onMapClick} />
        {children}
      </LeafletMapContainer>
    </div>
  );
}

const styles = {
  card: {
    backgroundColor: "#fff",
    borderRadius: "12px",
    overflow: "hidden",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  },
};
