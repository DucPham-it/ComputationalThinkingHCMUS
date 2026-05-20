import { describe, expect, test } from "vitest";
import {
  calculateBearing,
  haversineDistance,
  isAccurateGpsPosition,
  pointToSegmentDistance,
  polylineRemainingDistance,
  snapToPolyline,
} from "../src/utils/geomath";

describe("geomath utilities", () => {
  test("haversineDistance returns distance in meters between two GPS points", () => {
    const pointA = { latitude: 10.8231, longitude: 106.6297 };
    const pointB = { latitude: 10.8232, longitude: 106.6297 };

    const distance = haversineDistance(pointA, pointB);

    expect(distance).toBeGreaterThan(10);
    expect(distance).toBeLessThan(15);
  });

  test("haversineDistance supports lat/lng field names", () => {
    const pointA = { lat: 10.8231, lng: 106.6297 };
    const pointB = { lat: 10.8232, lng: 106.6297 };

    const distance = haversineDistance(pointA, pointB);

    expect(distance).toBeGreaterThan(10);
    expect(distance).toBeLessThan(15);
  });

  test("pointToSegmentDistance returns near zero when point is on segment", () => {
    const point = { latitude: 10.0005, longitude: 106.0 };
    const segmentStart = { latitude: 10.0, longitude: 106.0 };
    const segmentEnd = { latitude: 10.001, longitude: 106.0 };

    const distance = pointToSegmentDistance(point, segmentStart, segmentEnd);

    expect(distance).toBeLessThan(1);
  });

  test("pointToSegmentDistance returns positive distance when point is away from segment", () => {
    const point = { latitude: 10.0005, longitude: 106.001 };
    const segmentStart = { latitude: 10.0, longitude: 106.0 };
    const segmentEnd = { latitude: 10.001, longitude: 106.0 };

    const distance = pointToSegmentDistance(point, segmentStart, segmentEnd);

    expect(distance).toBeGreaterThan(100);
  });

  test("snapToPolyline returns nearest segment index and snapped point", () => {
    const polyline = [
      { latitude: 10.0, longitude: 106.0 },
      { latitude: 10.001, longitude: 106.0 },
      { latitude: 10.002, longitude: 106.0 },
    ];

    const point = { latitude: 10.0014, longitude: 106.0002 };

    const result = snapToPolyline(point, polyline);

    expect(result.segmentIndex).toBe(1);
    expect(result.snappedPoint).not.toBeNull();
    expect(result.distanceMeters).toBeGreaterThan(0);
    expect(result.progress).toBeGreaterThanOrEqual(0);
    expect(result.progress).toBeLessThanOrEqual(1);
  });

  test("snapToPolyline handles empty polyline safely", () => {
    const result = snapToPolyline(
      { latitude: 10.0, longitude: 106.0 },
      []
    );

    expect(result.snappedPoint).toBeNull();
    expect(result.distanceMeters).toBe(Infinity);
    expect(result.segmentIndex).toBe(-1);
  });

  test("calculateBearing returns around 0 degrees for north direction", () => {
    const from = { latitude: 10.0, longitude: 106.0 };
    const to = { latitude: 10.001, longitude: 106.0 };

    const bearing = calculateBearing(from, to);

    expect(bearing).toBeGreaterThanOrEqual(0);
    expect(bearing).toBeLessThan(5);
  });

  test("calculateBearing returns around 90 degrees for east direction", () => {
    const from = { latitude: 10.0, longitude: 106.0 };
    const to = { latitude: 10.0, longitude: 106.001 };

    const bearing = calculateBearing(from, to);

    expect(bearing).toBeGreaterThan(85);
    expect(bearing).toBeLessThan(95);
  });

  test("polylineRemainingDistance returns remaining route distance", () => {
    const polyline = [
      { latitude: 10.0, longitude: 106.0 },
      { latitude: 10.001, longitude: 106.0 },
      { latitude: 10.002, longitude: 106.0 },
    ];

    const distance = polylineRemainingDistance(polyline, 0);

    expect(distance).toBeGreaterThan(200);
    expect(distance).toBeLessThan(230);
  });

  test("polylineRemainingDistance starts from selected segment index", () => {
    const polyline = [
      { latitude: 10.0, longitude: 106.0 },
      { latitude: 10.001, longitude: 106.0 },
      { latitude: 10.002, longitude: 106.0 },
    ];

    const distance = polylineRemainingDistance(polyline, 1);

    expect(distance).toBeGreaterThan(100);
    expect(distance).toBeLessThan(120);
  });

  test("isAccurateGpsPosition accepts accuracy less than or equal to 100m", () => {
    const gpsPosition = {
      coords: {
        accuracy: 50,
      },
    };

    expect(isAccurateGpsPosition(gpsPosition, 100)).toBe(true);
  });

  test("isAccurateGpsPosition rejects accuracy greater than 100m", () => {
    const gpsPosition = {
      coords: {
        accuracy: 150,
      },
    };

    expect(isAccurateGpsPosition(gpsPosition, 100)).toBe(false);
  });
});