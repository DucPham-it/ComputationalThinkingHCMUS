/**
 * User position marker for navigation mode.
 * Renders a blue circle marker with:
 *   - A solid blue dot for user position
 *   - A semi-transparent accuracy radius ring
 *   - A CSS pulse animation for visual feedback
 *   - Optional heading indicator (bearing arrow)
 *
 * @param {{ latitude: number, longitude: number }} position - Current GPS position
 * @param {number} heading - Current bearing in degrees (0-360), optional
 * @param {number} accuracy - GPS accuracy in meters, optional
 */

import { useEffect, useRef } from "react";
import { CircleMarker, Circle, useMap } from "react-leaflet";

/** Inject pulse animation CSS into the document (once) */
const PULSE_STYLE_ID = "user-position-pulse-style";

// TODO: [NGƯỜI 6] Inject CSS animation pulse vào document (chỉ 1 lần). Tạo hiệu ứng nhấp nháy xanh cho vị trí user
function injectPulseStyles() {
  if (document.getElementById(PULSE_STYLE_ID)) return;

  const style = document.createElement("style");
  style.id = PULSE_STYLE_ID;
  style.textContent = `
    @keyframes user-position-pulse {
      0% {
        transform: scale(1);
        opacity: 0.8;
      }
      50% {
        transform: scale(1.8);
        opacity: 0.3;
      }
      100% {
        transform: scale(2.4);
        opacity: 0;
      }
    }

    .user-position-pulse-ring {
      position: absolute;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: rgba(37, 99, 235, 0.35);
      animation: user-position-pulse 2s ease-out infinite;
      pointer-events: none;
      transform-origin: center center;
      z-index: 400;
    }

    .user-position-dot {
      position: absolute;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #2563eb;
      border: 3px solid #ffffff;
      box-shadow: 0 0 8px rgba(37, 99, 235, 0.5), 0 2px 4px rgba(0, 0, 0, 0.2);
      z-index: 401;
      pointer-events: none;
    }

    .user-position-heading {
      position: absolute;
      width: 0;
      height: 0;
      border-left: 6px solid transparent;
      border-right: 6px solid transparent;
      border-bottom: 16px solid #2563eb;
      z-index: 402;
      pointer-events: none;
      filter: drop-shadow(0 0 2px rgba(37, 99, 235, 0.5));
    }
  `;
  document.head.appendChild(style);
}

// TODO: [NGƯỜI 6] Vẽ mũi tên hướng di chuyển (heading) bằng Leaflet DivIcon. Xoay theo góc bearing 0-360°
function HeadingOverlay({ position, heading }) {
  const map = useMap();
  const markerRef = useRef(null);

  useEffect(() => {
    if (heading == null || !position) return;

    const L = window.L;
    if (!L) return;

    const lat = position.latitude ?? position.lat;
    const lng = position.longitude ?? position.lng;

    if (lat == null || lng == null) return;

    // Create heading arrow as a DivIcon
    const icon = L.divIcon({
      className: "",
      html: `<div class="user-position-heading" style="transform: rotate(${heading}deg); transform-origin: center bottom;"></div>`,
      iconSize: [12, 16],
      iconAnchor: [6, 24], // anchor below the dot
    });

    const marker = L.marker([lat, lng], {
      icon,
      interactive: false,
      zIndexOffset: 1000,
    });

    marker.addTo(map);
    markerRef.current = marker;

    return () => {
      if (markerRef.current) {
        map.removeLayer(markerRef.current);
        markerRef.current = null;
      }
    };
  }, [position, heading, map]);

  return null;
}

// TODO: [NGƯỜI 6] Tạo vòng pulse animation tại vị trí user bằng DivIcon. Hiệu ứng expand + fade liên tục
function PulseOverlay({ position }) {
  const map = useMap();
  const markerRef = useRef(null);

  useEffect(() => {
    if (!position) return;

    const L = window.L;
    if (!L) return;

    const lat = position.latitude ?? position.lat;
    const lng = position.longitude ?? position.lng;

    if (lat == null || lng == null) return;

    const icon = L.divIcon({
      className: "",
      html: `<div class="user-position-pulse-ring"></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });

    const marker = L.marker([lat, lng], {
      icon,
      interactive: false,
      zIndexOffset: 999,
    });

    marker.addTo(map);
    markerRef.current = marker;

    return () => {
      if (markerRef.current) {
        map.removeLayer(markerRef.current);
        markerRef.current = null;
      }
    };
  }, [position, map]);

  return null;
}

// TODO: [NGƯỜI 6] Component chính: vẽ vị trí user trên map gồm blue dot + accuracy circle + pulse + heading arrow
export default function UserPositionMarker({
  position,
  heading = null,
  accuracy = null,
}) {
  // Inject styles on first render
  useEffect(() => {
    injectPulseStyles();
  }, []);

  if (!position) {
    return null;
  }

  const lat = position.latitude ?? position.lat;
  const lng = position.longitude ?? position.lng;

  if (lat == null || lng == null) {
    return null;
  }

  // Clamp accuracy for display (min 10m, max 500m)
  const displayAccuracy = accuracy
    ? Math.min(Math.max(accuracy, 10), 500)
    : null;

  return (
    <>
      {/* Accuracy radius circle — semi-transparent blue */}
      {displayAccuracy && (
        <Circle
          center={[lat, lng]}
          radius={displayAccuracy}
          pathOptions={{
            color: "#2563eb",
            fillColor: "#2563eb",
            fillOpacity: 0.08,
            weight: 1,
            opacity: 0.3,
            dashArray: "4, 4",
          }}
        />
      )}

      {/* Pulse animation overlay */}
      <PulseOverlay position={position} />

      {/* Main position dot — solid blue with white border */}
      <CircleMarker
        center={[lat, lng]}
        radius={8}
        pathOptions={{
          color: "#ffffff",
          fillColor: "#2563eb",
          fillOpacity: 1,
          weight: 3,
          opacity: 1,
        }}
      />

      {/* Heading indicator — triangle arrow */}
      {heading != null && (
        <HeadingOverlay position={position} heading={heading} />
      )}
    </>
  );
}
