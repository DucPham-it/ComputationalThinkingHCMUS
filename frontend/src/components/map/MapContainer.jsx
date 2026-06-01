/**
 * Leaflet map container using OpenStreetMap tiles.
 * Supports navigation mode with full-screen view and GPS follow.
 */

import { MapContainer as LeafletMapContainer, TileLayer, useMap, useMapEvents, ZoomControl } from "react-leaflet";
import { useEffect, useMemo, useRef, useState } from "react";
import { Navigation } from "lucide-react";
import { useApp } from "../../hooks/useApp";

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

function MapUpdater({ center, zoom }) {
  const map = useMap();
  const lat = center ? resolveCoordinate(center, "latitude", "lat") : null;
  const lng = center ? resolveCoordinate(center, "longitude", "lng") : null;

  useEffect(() => {
    if (lat == null || lng == null) {
      return;
    }
    map.setView([lat, lng], map.getZoom(), { animate: true });
  }, [lat, lng, map]);

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [boundsKey, map]);

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

// Locate/Recenter control button component
function LocateControl({ followPosition, onRecenter, navigationMode }) {
  const map = useMap();
  const { currentLocation, setCurrentLocation } = useApp();
  const [hovered, setHovered] = useState(false);

  const handleLocate = (e) => {
    e.stopPropagation();
    e.preventDefault();

    // Luôn ưu tiên quét vị trí mới với độ chính xác cao từ thiết bị
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          
          if (latitude == null || longitude == null || isNaN(latitude) || isNaN(longitude)) {
            console.error("Browser returned invalid coordinates:", latitude, longitude);
            alert("Trình duyệt trả về tọa độ không hợp lệ.");
            return;
          }

          // Hiển thị tọa độ nhận được để người dùng kiểm tra xem có bị sai lệch từ nguồn (nhà mạng/thiết bị) không
          alert(`Định vị thành công từ thiết bị!\n- Vĩ độ (Latitude): ${latitude}\n- Kinh độ (Longitude): ${longitude}\n\n(Lưu ý: Nếu tọa độ trên chỉ ra biển, có thể do trình duyệt/nhà mạng ước lượng sai vị trí IP hoặc thiết bị đang bật VPN/giả lập vị trí).`);

          const freshLoc = { latitude, longitude };
          
          if (setCurrentLocation) {
            setCurrentLocation(freshLoc);
          }
          
          map.setView([latitude, longitude], 17, { animate: true });
          if (onRecenter) {
            onRecenter(freshLoc);
          }
        },
        (error) => {
          console.warn("Locate Control: Fresh geolocation failed, using fallback:", error);
          
          // Dự phòng (fallback): Sử dụng vị trí lưu trong cache hoặc vị trí dẫn đường nếu lấy GPS mới thất bại
          const target = followPosition || currentLocation;
          if (target) {
            const lat = target.latitude ?? target.lat;
            const lng = target.longitude ?? target.lng;
            if (lat != null && lng != null) {
              map.setView([lat, lng], 17, { animate: true });
              if (onRecenter) {
                onRecenter({ latitude: lat, longitude: lng });
              }
              return;
            }
          }
          
          alert("Không thể lấy vị trí hiện tại của bạn. Vui lòng kiểm tra quyền truy cập vị trí trong cài đặt hệ thống và trình duyệt.");
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0, // Ép trình duyệt quét vị trí mới thay vì dùng cache của nó
        }
      );
    } else {
      // Dự phòng nếu trình duyệt không hỗ trợ Geolocation API
      const target = followPosition || currentLocation;
      if (target) {
        const lat = target.latitude ?? target.lat;
        const lng = target.longitude ?? target.lng;
        if (lat != null && lng != null) {
          map.setView([lat, lng], 17, { animate: true });
          if (onRecenter) {
            onRecenter({ latitude: lat, longitude: lng });
          }
          return;
        }
      }
      alert("Trình duyệt của bạn không hỗ trợ định vị GPS.");
    }
  };

  const bottomPosition = navigationMode ? "10px" : "80px";

  const buttonStyle = {
    position: "absolute",
    bottom: bottomPosition,
    right: "10px",
    zIndex: 1000,
    width: "34px",
    height: "34px",
    borderRadius: "4px",
    backgroundColor: hovered ? "#f4f4f4" : "#ffffff",
    border: "2px solid rgba(0,0,0,0.2)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    transition: "background-color 0.2s, transform 0.1s",
    outline: "none",
    padding: 0,
    boxSizing: "border-box",
  };

  return (
    <button
      onClick={handleLocate}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onMouseDown={(e) => {
        e.currentTarget.style.transform = "scale(0.95)";
      }}
      onMouseUp={(e) => {
        e.currentTarget.style.transform = "scale(1)";
      }}
      style={buttonStyle}
      title="Move map to current location"
      type="button"
    >
      <Navigation
        size={16}
        style={{
          transform: "rotate(45deg)",
          color: hovered ? "var(--color-primary, #2563eb)" : "#333333",
          fill: hovered ? "rgba(37, 99, 235, 0.15)" : "none",
          transition: "color 0.2s, fill 0.2s",
        }}
      />
    </button>
  );
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
  onRecenter = null,
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
        <LocateControl
          followPosition={followPosition}
          onRecenter={onRecenter}
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
