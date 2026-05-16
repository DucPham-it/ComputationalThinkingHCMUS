/**
 * Leaflet map container using OpenStreetMap tiles.
 */

import { MapContainer as LeafletMapContainer, TileLayer, useMap, useMapEvents, ZoomControl } from "react-leaflet";
import { useEffect, useMemo } from "react";

const mapContainerStyle = {
  width: "100%",
  height: "500px",
  borderRadius: "8px",
};

const defaultCenter = { latitude: 10.9804, longitude: 106.6519 };

function resolveCoordinate(point, primaryKey, legacyKey) {
  return point?.[primaryKey] ?? point?.[legacyKey];
}

function toFiniteNumber(value) {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue : null;
}

function resolveMapPoint(point) {
  const latitude = toFiniteNumber(resolveCoordinate(point, "latitude", "lat"));
  const longitude = toFiniteNumber(resolveCoordinate(point, "longitude", "lng"));

  if (latitude == null || longitude == null) {
    return null;
  }

  return [latitude, longitude];
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
      map.getZoom(),
      { animate: true }
    );
  }, [center, map]);

  return null;
}

function MapBoundsUpdater({ points = [] }) {
  const map = useMap();
  const boundsPoints = useMemo(
    () => points.map(resolveMapPoint).filter(Boolean),
    [points]
  );
  const boundsKey = boundsPoints.map((point) => point.join(",")).join("|");

  useEffect(() => {
    if (!boundsPoints.length) {
      return;
    }

    if (boundsPoints.length === 1) {
      map.setView(boundsPoints[0], map.getZoom(), { animate: true });
      return;
    }

    map.fitBounds(boundsPoints, {
      animate: true,
      maxZoom: 14,
      padding: [32, 32],
    });
  }, [boundsKey, boundsPoints, map]);

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
  fitBoundsPoints = [],
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
        zoomControl={false}
        scrollWheelZoom
        style={mapContainerStyle}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ZoomControl position="bottomright" />
        <MapUpdater center={resolvedCenter} zoom={zoom} />
        <MapBoundsUpdater points={fitBoundsPoints} />
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
