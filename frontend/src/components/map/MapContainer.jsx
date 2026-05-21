/**
 * Leaflet map container using OpenStreetMap tiles.
 * Supports navigation mode with full-screen view and GPS follow.
 */

import { MapContainer as LeafletMapContainer, TileLayer, useMap, useMapEvents, ZoomControl } from "react-leaflet";
import { useEffect, useMemo, useRef } from "react";

const mapContainerStyle = {
  width: "100%",
  height: "500px",
  borderRadius: "8px",
};

const navigationMapContainerStyle = {
  width: "100%",
  height: "100vh",
  borderRadius: "0px",
};

const NAVIGATION_ZOOM = 17;

const defaultCenter = { latitude: 10.9804, longitude: 106.6519 };

// TODO: Trích xuất tọa độ từ point object, hỗ trợ cả key mới (latitude/longitude) và key cũ (lat/lng)
function resolveCoordinate(point, primaryKey, legacyKey) {
  return point?.[primaryKey] ?? point?.[legacyKey];
}

// TODO: Chuyển đổi giá trị sang số hữu hạn, trả về null nếu không hợp lệ (NaN, Infinity)
function toFiniteNumber(value) {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue : null;
}

// TODO: Chuyển đổi point object thành mảng [lat, lng] cho Leaflet, trả về null nếu tọa độ không hợp lệ
function resolveMapPoint(point) {
  const latitude = toFiniteNumber(resolveCoordinate(point, "latitude", "lat"));
  const longitude = toFiniteNumber(resolveCoordinate(point, "longitude", "lng"));

  if (latitude == null || longitude == null) {
    return null;
  }

  return [latitude, longitude];
}

// TODO: Component cập nhật view của map khi center hoặc zoom thay đổi (chỉ hoạt động ở mode bình thường)
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

// TODO: Tự động fitBounds map theo danh sách points, maxZoom 14, padding 32px (chỉ mode bình thường)
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

// TODO: Bắt sự kiện click trên map, trả về tọa độ {latitude, longitude} qua callback onMapClick
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

// TODO: [NGƯỜI 6] Auto-follow GPS khi navigation mode bật. Smooth pan map theo vị trí user, threshold 0.00001° tránh update thừa
function NavigationFollower({ followPosition, navigationMode }) {
  const map = useMap();
  const lastPositionRef = useRef(null);

  useEffect(() => {
    if (!navigationMode || !followPosition) {
      return;
    }

    const lat = resolveCoordinate(followPosition, "latitude", "lat");
    const lng = resolveCoordinate(followPosition, "longitude", "lng");

    if (lat == null || lng == null) {
      return;
    }

    const latNum = toFiniteNumber(lat);
    const lngNum = toFiniteNumber(lng);

    if (latNum == null || lngNum == null) {
      return;
    }

    // Avoid redundant updates if position hasn't changed significantly
    const last = lastPositionRef.current;
    if (
      last &&
      Math.abs(last[0] - latNum) < 0.00001 &&
      Math.abs(last[1] - lngNum) < 0.00001
    ) {
      return;
    }

    lastPositionRef.current = [latNum, lngNum];
    map.setView([latNum, lngNum], NAVIGATION_ZOOM, {
      animate: true,
      duration: 0.5,
    });
  }, [followPosition, navigationMode, map]);

  return null;
}

// TODO: [NGƯỜI 6 - SỬA] Thêm props navigationMode + followPosition. Navigation mode: height 100vh, zoom 17, ẩn zoom control, disable MapUpdater/MapBoundsUpdater
export default function MapContainer({
  children,
  center,
  zoom = 14,
  onMapClick,
  fitBoundsPoints = [],
  mapContainerClassName = "",
  navigationMode = false,
  followPosition = null,
}) {
  const resolvedCenter = center || defaultCenter;
  const effectiveZoom = navigationMode ? NAVIGATION_ZOOM : zoom;
  const effectiveStyle = navigationMode ? navigationMapContainerStyle : mapContainerStyle;
  const cardStyle = navigationMode ? styles.navigationCard : styles.card;

  return (
    <div className={`card ${mapContainerClassName}`} style={cardStyle}>
      <LeafletMapContainer
        center={[
          resolveCoordinate(resolvedCenter, "latitude", "lat"),
          resolveCoordinate(resolvedCenter, "longitude", "lng"),
        ]}
        zoom={effectiveZoom}
        zoomControl={false}
        scrollWheelZoom
        style={effectiveStyle}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {!navigationMode && <ZoomControl position="bottomright" />}
        {!navigationMode && <MapUpdater center={resolvedCenter} zoom={effectiveZoom} />}
        {!navigationMode && <MapBoundsUpdater points={fitBoundsPoints} />}
        <MapClickHandler onMapClick={onMapClick} />
        <NavigationFollower
          followPosition={followPosition}
          navigationMode={navigationMode}
        />
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
  navigationCard: {
    backgroundColor: "#fff",
    borderRadius: "0px",
    overflow: "hidden",
    boxShadow: "none",
    position: "relative",
  },
};
