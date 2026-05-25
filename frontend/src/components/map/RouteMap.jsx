/**
 * Route polyline renderer driven entirely by backend route data.
 * Supports navigation mode with 3-color polyline rendering:
 *   - Past steps (gray #94a3b8)
 *   - Current step (dark blue #2563eb)
 *   - Future steps (light blue #93c5fd)
 */

import { useMemo } from "react";
import { Polyline } from "react-leaflet";

/** Color constants for navigation polylines */
const ROUTE_COLORS = {
  default: "#2563eb",
  past: "#94a3b8",
  current: "#2563eb",
  future: "#93c5fd",
};

// TODO: Chuẩn hóa point object thành mảng [lat, lng] cho Leaflet, hỗ trợ cả key latitude/lat và longitude/lng
function toLatLng(point) {
  return [point.latitude ?? point.lat, point.longitude ?? point.lng];
}

// TODO: [NGƯỜI 6] Trích xuất tọa độ geometry từ step. Ưu tiên step.geometry[], fallback sang maneuver_location, trả [] nếu không có
function getStepPositions(step) {
  if (!step) return [];
  if (Array.isArray(step.geometry) && step.geometry.length >= 2) {
    return step.geometry.map(toLatLng);
  }
  // Fallback: use maneuver_location as single point
  if (step.maneuver_location) {
    return [toLatLng(step.maneuver_location)];
  }
  return [];
}

// TODO: [NGƯỜI 6] Chia steps thành 3 đoạn polyline: past (đã đi), current (đang đi), future (chưa đi). Nối liền mạch giữa các đoạn
function buildSegments(steps, currentStepIndex) {
  const past = [];
  const current = [];
  const future = [];

  for (let i = 0; i < steps.length; i++) {
    const positions = getStepPositions(steps[i]);
    if (positions.length === 0) continue;

    if (i < currentStepIndex) {
      past.push(...positions);
    } else if (i === currentStepIndex) {
      // Connect past to current seamlessly
      if (past.length > 0) {
        current.push(past[past.length - 1]);
      }
      current.push(...positions);
    } else {
      // Connect current/past to future seamlessly
      if (future.length === 0) {
        if (current.length > 0) {
          future.push(current[current.length - 1]);
        } else if (past.length > 0) {
          future.push(past[past.length - 1]);
        }
      }
      future.push(...positions);
    }
  }

  return { past, current, future };
}

// TODO: [NGƯỜI 6 - SỬA] Thêm navigationMode + currentStepIndex + steps. Navigation: polyline 3 màu (xám/xanh đậm/xanh nhạt). Default mode: giữ nguyên polyline cũ (backward compatible)
export default function RouteMap({
  path = [],
  navigationMode = false,
  currentStepIndex = 0,
  steps = [],
}) {
  // Build navigation segments (memoized)
  const segments = useMemo(() => {
    if (!navigationMode || !Array.isArray(steps) || steps.length === 0) {
      return null;
    }
    return buildSegments(steps, currentStepIndex);
  }, [navigationMode, steps, currentStepIndex]);

  // === Default mode: single polyline (backward compatible) ===
  if (!navigationMode) {
    if (!Array.isArray(path) || path.length < 2) {
      return null;
    }

    return (
      <Polyline
        positions={path.map(toLatLng)}
        pathOptions={{
          color: ROUTE_COLORS.default,
          weight: 5,
          opacity: 0.82,
        }}
      />
    );
  }

  // === Navigation mode: 3-color polylines ===
  if (!segments) {
    return null;
  }

  return (
    <>
      {/* Past steps — gray, slightly transparent */}
      {segments.past.length >= 2 && (
        <Polyline
          positions={segments.past}
          pathOptions={{
            color: ROUTE_COLORS.past,
            weight: 6,
            opacity: 0.5,
            dashArray: "8, 6",
          }}
        />
      )}

      {/* Current step — dark blue, prominent */}
      {segments.current.length >= 2 && (
        <Polyline
          positions={segments.current}
          pathOptions={{
            color: ROUTE_COLORS.current,
            weight: 7,
            opacity: 0.95,
          }}
        />
      )}

      {/* Future steps — light blue */}
      {segments.future.length >= 2 && (
        <Polyline
          positions={segments.future}
          pathOptions={{
            color: ROUTE_COLORS.future,
            weight: 5,
            opacity: 0.7,
          }}
        />
      )}
    </>
  );
}
