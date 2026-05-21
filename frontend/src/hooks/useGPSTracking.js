/**
 * GPS Tracking Hook - Quản lý và theo dõi tọa độ GPS của thiết bị.
 *
 * Owner:
 * - Người 7 (TV7): Turn-by-Turn Navigation Integration.
 *
 * File input:
 * - options: Các tùy chọn cấu hình Geolocation (enableHighAccuracy, timeout, maximumAge, accuracyThreshold).
 *
 * File output:
 * - position: Tọa độ hiện tại của thiết bị { latitude, longitude, lat, lng }.
 * - accuracy: Độ chính xác của GPS (mét).
 * - heading: Hướng di chuyển hiện tại (độ, 0-360).
 * - speed: Tốc độ di chuyển hiện tại (m/s).
 * - error: Lỗi GPS nếu có.
 * - isTracking: Trạng thái đang theo dõi GPS hay không.
 * - startTracking: Hàm bắt đầu theo dõi.
 * - stopTracking: Hàm dừng theo dõi.
 */

import { useState, useEffect, useCallback, useRef } from "react";

export default function useGPSTracking(options = {}) {
  const {
    enableHighAccuracy = true,
    timeout = 10000,
    maximumAge = 0,
    accuracyThreshold = 100, // Noise filter: reject accuracy > 100m
  } = options;

  const [position, setPosition] = useState(null);
  const [accuracy, setAccuracy] = useState(null);
  const [heading, setHeading] = useState(null);
  const [speed, setSpeed] = useState(null);
  const [error, setError] = useState(null);
  const [isTracking, setIsTracking] = useState(false);

  const watchIdRef = useRef(null);

  /**
   * Dừng theo dõi GPS.
   *
   * Owner: Người 7 (TV7)
   * Input: Không có
   * Output: Hủy watchPosition hiện tại, cập nhật trạng thái isTracking = false
   */
  const stopTracking = useCallback(() => {
    if (watchIdRef.current !== null) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }
    setIsTracking(false);
  }, []);

  /**
   * Bắt đầu theo dõi GPS thông qua Geolocation API.
   *
   * Owner: Người 7 (TV7)
   * Input: Không có
   * Output: Kích hoạt watchPosition, cập nhật state position, accuracy, heading, speed, error
   */
  const startTracking = useCallback(() => {
    if (!navigator.geolocation) {
      setError(new Error("Geolocation is not supported by this browser."));
      return;
    }

    stopTracking();

    setIsTracking(true);
    setError(null);

    watchIdRef.current = navigator.geolocation.watchPosition(
      (pos) => {
        const coords = pos.coords;
        // Noise filter: reject accuracy > threshold
        if (accuracyThreshold && coords.accuracy > accuracyThreshold) {
          console.warn(`GPS update ignored due to low accuracy: ${coords.accuracy}m`);
          return;
        }

        setPosition({
          latitude: coords.latitude,
          longitude: coords.longitude,
          lat: coords.latitude,
          lng: coords.longitude,
        });
        setAccuracy(coords.accuracy);
        setHeading(coords.heading);
        setSpeed(coords.speed);
        setError(null);
      },
      (err) => {
        console.error("GPS Tracking Error:", err);
        setError(err);
      },
      { enableHighAccuracy, timeout, maximumAge }
    );
  }, [enableHighAccuracy, timeout, maximumAge, accuracyThreshold, stopTracking]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopTracking();
    };
  }, [stopTracking]);

  return {
    position,
    accuracy,
    heading,
    speed,
    error,
    isTracking,
    startTracking,
    stopTracking,
  };
}
