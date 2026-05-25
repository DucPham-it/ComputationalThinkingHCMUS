/**
 * Utilities for geographic calculations used by turn-by-turn navigation.
 * All distance outputs are in meters.
 */

const EARTH_RADIUS_METERS = 6371000;

/**
 * Normalize point object to { latitude, longitude }.
 * Supports both { latitude, longitude } and { lat, lng }.
 *
 * @param {Object} point
 * @returns {{ latitude: number, longitude: number } | null}
 */
export function normalizePoint(point) {
  if (!point) return null;

  const latitude = Number(point.latitude ?? point.lat);
  const longitude = Number(point.longitude ?? point.lng);

  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    return null;
  }

  return { latitude, longitude };
}

/**
 * Convert degrees to radians.
 *
 * @param {number} degrees
 * @returns {number}
 */
function toRadians(degrees) {
  return (degrees * Math.PI) / 180;
}

/**
 * Convert radians to degrees.
 *
 * @param {number} radians
 * @returns {number}
 */
function toDegrees(radians) {
  return (radians * 180) / Math.PI;
}

/**
 * Calculate the great-circle distance between two GPS points using Haversine formula.
 *
 * @param {{latitude?: number, longitude?: number, lat?: number, lng?: number}} pointA
 * @param {{latitude?: number, longitude?: number, lat?: number, lng?: number}} pointB
 * @returns {number} Distance in meters. Returns Infinity if input is invalid.
 */
export function haversineDistance(pointA, pointB) {
  const a = normalizePoint(pointA);
  const b = normalizePoint(pointB);

  if (!a || !b) {
    return Infinity;
  }

  const lat1 = toRadians(a.latitude);
  const lat2 = toRadians(b.latitude);
  const deltaLat = toRadians(b.latitude - a.latitude);
  const deltaLng = toRadians(b.longitude - a.longitude);

  const h =
    Math.sin(deltaLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(deltaLng / 2) ** 2;

  return 2 * EARTH_RADIUS_METERS * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
}

/**
 * Project a GPS point into a local meter-based coordinate system.
 * Used for short route segment calculations.
 *
 * @param {{latitude: number, longitude: number}} point
 * @param {{latitude: number, longitude: number}} origin
 * @returns {{x: number, y: number}}
 */
function projectToMeters(point, origin) {
  const latRad = toRadians(origin.latitude);

  return {
    x:
      toRadians(point.longitude - origin.longitude) *
      EARTH_RADIUS_METERS *
      Math.cos(latRad),
    y: toRadians(point.latitude - origin.latitude) * EARTH_RADIUS_METERS,
  };
}

/**
 * Convert local meter-based coordinate back to GPS point.
 *
 * @param {{x: number, y: number}} projected
 * @param {{latitude: number, longitude: number}} origin
 * @returns {{latitude: number, longitude: number}}
 */
function unprojectFromMeters(projected, origin) {
  const latRad = toRadians(origin.latitude);

  return {
    latitude: origin.latitude + toDegrees(projected.y / EARTH_RADIUS_METERS),
    longitude:
      origin.longitude +
      toDegrees(projected.x / (EARTH_RADIUS_METERS * Math.cos(latRad))),
  };
}

/**
 * Find the nearest point on a segment to a given GPS point.
 *
 * @param {{latitude?: number, longitude?: number, lat?: number, lng?: number}} point
 * @param {{latitude?: number, longitude?: number, lat?: number, lng?: number}} segmentStart
 * @param {{latitude?: number, longitude?: number, lat?: number, lng?: number}} segmentEnd
 * @returns {{
 *   snappedPoint: {latitude: number, longitude: number} | null,
 *   distanceMeters: number,
 *   progress: number
 * }}
 */
export function closestPointOnSegment(point, segmentStart, segmentEnd) {
  const p = normalizePoint(point);
  const a = normalizePoint(segmentStart);
  const b = normalizePoint(segmentEnd);

  if (!p || !a || !b) {
    return {
      snappedPoint: null,
      distanceMeters: Infinity,
      progress: 0,
    };
  }

  const projectedPoint = projectToMeters(p, a);
  const projectedStart = { x: 0, y: 0 };
  const projectedEnd = projectToMeters(b, a);

  const dx = projectedEnd.x - projectedStart.x;
  const dy = projectedEnd.y - projectedStart.y;
  const lengthSquared = dx * dx + dy * dy;

  if (lengthSquared === 0) {
    return {
      snappedPoint: a,
      distanceMeters: haversineDistance(p, a),
      progress: 0,
    };
  }

  const rawProgress =
    ((projectedPoint.x - projectedStart.x) * dx +
      (projectedPoint.y - projectedStart.y) * dy) /
    lengthSquared;

  const progress = Math.max(0, Math.min(1, rawProgress));

  const closestProjected = {
    x: projectedStart.x + progress * dx,
    y: projectedStart.y + progress * dy,
  };

  const snappedPoint = unprojectFromMeters(closestProjected, a);
  const distanceMeters = haversineDistance(p, snappedPoint);

  return {
    snappedPoint,
    distanceMeters,
    progress,
  };
}

/**
 * Calculate distance from a GPS point to a route segment.
 *
 * @param {{latitude?: number, longitude?: number, lat?: number, lng?: number}} point
 * @param {{latitude?: number, longitude?: number, lat?: number, lng?: number}} segmentStart
 * @param {{latitude?: number, longitude?: number, lat?: number, lng?: number}} segmentEnd
 * @returns {number} Distance in meters.
 */
export function pointToSegmentDistance(point, segmentStart, segmentEnd) {
  return closestPointOnSegment(point, segmentStart, segmentEnd).distanceMeters;
}

/**
 * Snap a GPS point to the nearest point on a route polyline.
 *
 * @param {{latitude?: number, longitude?: number, lat?: number, lng?: number}} point
 * @param {Array<{latitude?: number, longitude?: number, lat?: number, lng?: number}>} polyline
 * @returns {{
 *   snappedPoint: {latitude: number, longitude: number} | null,
 *   distanceMeters: number,
 *   segmentIndex: number,
 *   progress: number
 * }}
 */
export function snapToPolyline(point, polyline) {
  if (!Array.isArray(polyline) || polyline.length === 0) {
    return {
      snappedPoint: null,
      distanceMeters: Infinity,
      segmentIndex: -1,
      progress: 0,
    };
  }

  if (polyline.length === 1) {
    const onlyPoint = normalizePoint(polyline[0]);

    return {
      snappedPoint: onlyPoint,
      distanceMeters: haversineDistance(point, onlyPoint),
      segmentIndex: 0,
      progress: 0,
    };
  }

  let bestResult = {
    snappedPoint: null,
    distanceMeters: Infinity,
    segmentIndex: -1,
    progress: 0,
  };

  for (let index = 0; index < polyline.length - 1; index += 1) {
    const result = closestPointOnSegment(point, polyline[index], polyline[index + 1]);

    if (result.distanceMeters < bestResult.distanceMeters) {
      bestResult = {
        snappedPoint: result.snappedPoint,
        distanceMeters: result.distanceMeters,
        segmentIndex: index,
        progress: result.progress,
      };
    }
  }

  return bestResult;
}

/**
 * Calculate bearing from one GPS point to another.
 *
 * @param {{latitude?: number, longitude?: number, lat?: number, lng?: number}} from
 * @param {{latitude?: number, longitude?: number, lat?: number, lng?: number}} to
 * @returns {number} Bearing angle from 0 to 360 degrees. Returns 0 for invalid input.
 */
export function calculateBearing(from, to) {
  const start = normalizePoint(from);
  const end = normalizePoint(to);

  if (!start || !end) {
    return 0;
  }

  const lat1 = toRadians(start.latitude);
  const lat2 = toRadians(end.latitude);
  const deltaLng = toRadians(end.longitude - start.longitude);

  const y = Math.sin(deltaLng) * Math.cos(lat2);
  const x =
    Math.cos(lat1) * Math.sin(lat2) -
    Math.sin(lat1) * Math.cos(lat2) * Math.cos(deltaLng);

  return (toDegrees(Math.atan2(y, x)) + 360) % 360;
}

/**
 * Calculate remaining distance along a polyline from a segment index.
 *
 * @param {Array<{latitude?: number, longitude?: number, lat?: number, lng?: number}>} polyline
 * @param {number} fromIndex
 * @returns {number} Remaining distance in meters.
 */
export function polylineRemainingDistance(polyline, fromIndex = 0) {
  if (!Array.isArray(polyline) || polyline.length < 2) {
    return 0;
  }

  const safeStartIndex = Math.max(0, Math.min(fromIndex, polyline.length - 2));

  let totalDistance = 0;

  for (let index = safeStartIndex; index < polyline.length - 1; index += 1) {
    totalDistance += haversineDistance(polyline[index], polyline[index + 1]);
  }

  return totalDistance;
}

/**
 * Check whether a browser geolocation position is accurate enough for navigation.
 *
 * @param {{coords?: {accuracy?: number}}} position
 * @param {number} maxAccuracyMeters
 * @returns {boolean}
 */
export function isAccurateGpsPosition(position, maxAccuracyMeters = 100) {
  const accuracy = Number(position?.coords?.accuracy);

  if (!Number.isFinite(accuracy)) {
    return false;
  }

  return accuracy <= maxAccuracyMeters;
}