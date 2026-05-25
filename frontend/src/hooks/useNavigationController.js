/**
 * Navigation Controller Hook - Bộ điều phối và liên kết GPS, Engine và Voice.
 *
 * Owner:
 * - Người 7 (TV7): Turn-by-Turn Navigation Integration.
 *
 * File input:
 * - config: Cấu hình bao gồm:
 *   - route: Đối tượng tuyến đường hiện tại từ backend.
 *   - onReroute: Callback kích hoạt tính toán lại đường đi.
 *   - onArrival: Callback kích hoạt khi đến đích.
 *   - onEnd: Callback khi kết thúc hành trình.
 *   - gpsOptions: Cấu hình Geolocation.
 *
 * File output:
 * - isTracking: Trạng thái GPS đang chạy hay không.
 * - gpsPosition: Tọa độ GPS hiện tại.
 * - gpsHeading: Hướng di chuyển GPS.
 * - gpsAccuracy: Độ chính xác định vị.
 * - navState: Trạng thái điều hướng hiện tại (NAV_STATES).
 * - currentStepIndex: Vị trí step hiện tại của hành trình.
 * - distanceToNextManeuver: Khoảng cách đến cú rẽ tiếp theo (mét).
 * - totalDistanceRemaining: Tổng khoảng cách còn lại (mét).
 * - navigationProps: Bộ props truyền vào NavigationPanel component.
 * - actions: Các hàm điều khiển (start, stop, pause, resume).
 */

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import useGPSTracking from "./useGPSTracking";
import useNavigationEngine, { NAV_STATES } from "./useNavigationEngine";
import { speakInstruction, cancelSpeech } from "../services/voiceGuidanceService";

export default function useNavigationController(config = {}) {
  const {
    route,
    onReroute,
    onArrival,
    onEnd,
    gpsOptions = {},
  } = config;

  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);

  // 1. Kích hoạt định vị GPS
  const gps = useGPSTracking(gpsOptions);

  // 2. Chuyển đổi định dạng route để phù hợp với useNavigationEngine
  // Engine yêu cầu route.path chứa các điểm rẽ (milestones) có gắn sẵn instruction để đọc giọng nói
  const engineRoute = useMemo(() => {
    if (!route || !route.steps || route.steps.length === 0) return null;

    const path = route.steps.map((step) => {
      let lat = 0;
      let lng = 0;

      // Trích xuất tọa độ từ maneuver_location (mặc định là [lng, lat] từ backend)
      if (step.maneuver_location) {
        lat = step.maneuver_location.latitude ?? step.maneuver_location.lat ?? step.maneuver_location[1] ?? 0;
        lng = step.maneuver_location.longitude ?? step.maneuver_location.lng ?? step.maneuver_location[0] ?? 0;
      } else if (step.geometry && step.geometry.length > 0) {
        // Lấy điểm bắt đầu của geometry
        const firstPoint = step.geometry[0];
        lat = firstPoint.latitude ?? firstPoint.lat ?? firstPoint[1] ?? 0;
        lng = firstPoint.longitude ?? firstPoint.lng ?? firstPoint[0] ?? 0;
      }

      return {
        latitude: lat,
        longitude: lng,
        lat: lat,
        lng: lng,
        instruction: step.instruction || step.instructions || "Tiếp tục đi thẳng",
      };
    });

    return {
      ...route,
      path: path,
    };
  }, [route]);

  // 3. Khởi động Navigation Engine bằng dữ liệu GPS
  const engine = useNavigationEngine(engineRoute, gps.position);

  const lastSpokenTimeRef = useRef(null);
  const lastRerouteTimeRef = useRef(0);
  const prevRouteRef = useRef(route);

  /**
   * Phát chỉ dẫn giọng nói bằng cách sử dụng backend gTTS API, 
   * tự động fallback sang Web Speech Synthesis của trình duyệt nếu bị chặn/lỗi.
   *
   * Owner: Người 7 (TV7)
   * Input: text (Nội dung cần phát âm)
   * Output: Phát âm thanh qua Audio/SpeechSynthesis
   */
  const playVoice = useCallback((text) => {
    if (!text) return;
    const apiBase = import.meta.env.VITE_API_BASE_URL || "/api/v1";
    const url = `${apiBase}/tts?text=${encodeURIComponent(text)}`;
    const audio = new Audio(url);
    
    audio.play().catch((e) => {
      console.warn("Backend TTS blocked or failed, falling back to Web Speech Synthesis:", e);
      speakInstruction(text, { interrupt: true });
    });
  }, []);

  // 4. Lắng nghe cập nhật từ Engine và phát giọng nói khi có voicePrompt mới
  useEffect(() => {
    if (isVoiceEnabled && engine.voicePrompt && engine.voicePrompt.text) {
      if (lastSpokenTimeRef.current !== engine.voicePrompt.t) {
        lastSpokenTimeRef.current = engine.voicePrompt.t;
        playVoice(engine.voicePrompt.text);
      }
    }
  }, [engine.voicePrompt, isVoiceEnabled, playVoice]);

  // Hủy giọng nói nếu tạm dừng hoặc tắt điều hướng
  useEffect(() => {
    if (engine.state === NAV_STATES.IDLE || engine.state === NAV_STATES.PAUSED) {
      cancelSpeech();
    }
  }, [engine.state]);

  // 5. Tự động Reroute khi phát hiện đi chệch hướng (OFF_ROUTE)
  useEffect(() => {
    if (engine.state === NAV_STATES.OFF_ROUTE && gps.position) {
      const now = Date.now();
      // Giới hạn tần suất tính lại đường để tránh spam API (tối thiểu cách nhau 10 giây)
      if (now - lastRerouteTimeRef.current > 10000) {
        lastRerouteTimeRef.current = now;
        if (onReroute) {
          onReroute(gps.position);
        }
      }
    }
  }, [engine.state, gps.position, onReroute]);

  // Tự động tiếp tục điều hướng khi nhận được route mới sau khi reroute thành công
  useEffect(() => {
    if (route && route !== prevRouteRef.current) {
      const oldState = engine.state;
      prevRouteRef.current = route;
      if (oldState === NAV_STATES.OFF_ROUTE || oldState === NAV_STATES.NAVIGATING) {
        // Reset lại mốc spoken để engine hoạt động bình thường trên tuyến mới
        engine.actions.start();
      }
    }
  }, [route, engine.state, engine.actions]);

  // 6. Xử lý khi đã đến đích (ARRIVED)
  useEffect(() => {
    if (engine.state === NAV_STATES.ARRIVED) {
      gps.stopTracking();
      if (onArrival) {
        onArrival();
      }
    }
  }, [engine.state, onArrival, gps]);

  // 7. Định nghĩa các hành động điều hướng (Actions)
  const startNavigation = useCallback(() => {
    gps.startTracking();
    engine.actions.start();
  }, [gps, engine.actions]);

  const stopNavigation = useCallback(() => {
    gps.stopTracking();
    engine.actions.stop();
    cancelSpeech();
    if (onEnd) {
      onEnd();
    }
  }, [gps, engine.actions, onEnd]);

  const pauseNavigation = useCallback(() => {
    engine.actions.pause();
    cancelSpeech();
  }, [engine.actions]);

  const resumeNavigation = useCallback(() => {
    engine.actions.resume();
  }, [engine.actions]);

  // 8. Tính toán các giá trị hiển thị trên UI (navigationProps)
  const navigationProps = useMemo(() => {
    if (!route) return null;

    // Định dạng tổng khoảng cách còn lại
    let remainingDistance = "0 km";
    if (engine.totalDistanceRemaining !== null) {
      remainingDistance = engine.totalDistanceRemaining >= 1000
        ? `${(engine.totalDistanceRemaining / 1000).toFixed(1)} km`
        : `${engine.totalDistanceRemaining} m`;
    }

    // Định dạng tổng thời gian còn lại (tỷ lệ thuận với khoảng cách còn lại)
    let remainingTime = "0 phút";
    if (engine.totalDistanceRemaining !== null && route.distanceKm) {
      const routeDistanceMeters = route.distanceKm * 1000;
      const ratio = Math.max(0, Math.min(1, engine.totalDistanceRemaining / (routeDistanceMeters || 1)));
      const remainingSeconds = Math.round((route.durationSeconds || 0) * ratio);
      const remainingMins = Math.ceil(remainingSeconds / 60);

      if (remainingMins >= 60) {
        const hours = Math.floor(remainingMins / 60);
        const mins = remainingMins % 60;
        remainingTime = `${hours} giờ ${mins} phút`;
      } else {
        remainingTime = `${remainingMins} phút`;
      }
    }

    // Tính phần trăm tiến trình đi được
    const totalSteps = route.steps?.length || 0;
    const progress = totalSteps > 0
      ? Math.min(100, Math.max(0, (engine.currentStepIndex / totalSteps) * 100))
      : 0;

    return {
      steps: route.steps || [],
      currentStepIndex: engine.currentStepIndex,
      progress,
      remainingDistance,
      remainingTime,
      onEnd: stopNavigation,
      isVoiceOn: isVoiceEnabled,
      onToggleVoice: () => setIsVoiceEnabled((currentValue) => !currentValue),
      voiceControlled: true,
    };
  }, [route, engine.totalDistanceRemaining, engine.currentStepIndex, stopNavigation, isVoiceEnabled]);

  return {
    isTracking: gps.isTracking,
    gpsPosition: gps.position,
    gpsHeading: gps.heading,
    gpsAccuracy: gps.accuracy,
    navState: engine.state,
    currentStepIndex: engine.currentStepIndex,
    distanceToNextManeuver: engine.distanceToNextManeuver,
    totalDistanceRemaining: engine.totalDistanceRemaining,
    isVoiceEnabled,
    setIsVoiceEnabled,
    navigationProps,
    actions: {
      start: startNavigation,
      stop: stopNavigation,
      pause: pauseNavigation,
      resume: resumeNavigation,
    },
  };
}
