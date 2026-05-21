/**
 * Navigation Engine Hook - Bộ não quản lý trạng thái và tiến trình điều hướng.
 *
 * Owner:
 * - Người 5 (TV5): Navigation Engine.
 *
 * File input:
 * - route: Đối tượng tuyến đường từ backend (chứa path, steps, distance).
 * - currentLocation: Tọa độ GPS hiện tại của thiết bị { latitude, longitude }.
 *
 * File output:
 * - state: Trạng thái hiện tại của phiên điều hướng.
 * - currentStepIndex: Vị trí điểm nút (waypoint) hiện tại trên tuyến đường.
 * - distanceToNextManeuver: Khoảng cách tới điểm rẽ/chuyển hướng tiếp theo.
 * - totalDistanceRemaining: Tổng khoảng cách ước tính tới đích.
 * - voicePrompt: Câu lệnh chỉ đường để hệ thống phát giọng nói.
 * - actions: Các hàm điều khiển (start, pause, resume, stop).
 */

import { useState, useEffect, useCallback, useRef } from "react";

// Các trạng thái của máy điều hướng.
export const NAV_STATES = {
  IDLE: "IDLE",
  STARTING: "STARTING",
  NAVIGATING: "NAVIGATING",
  PAUSED: "PAUSED",
  OFF_ROUTE: "OFF_ROUTE",
  ARRIVED: "ARRIVED",
};

// Đi lạc trên 50 mét sẽ báo lỗi.
const OFF_ROUTE_THRESHOLD = 50;

// Tính khoảng cách đường chim bay (mét).
function getDistanceInMeters(lat1, lon1, lat2, lon2) {
  if (lat1 == null || lon1 == null || lat2 == null || lon2 == null) return Infinity;
  const R = 6371e3;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a = Math.sin(dLat / 2) ** 2 + Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) ** 2;
  return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
}

// Tính khoảng cách lệch khỏi tuyến đường.
function getDistanceToSegmentMeters(p, a, b) {
  const R = 6371e3;
  const latMid = ((a.lat + b.lat) / 2) * Math.PI / 180;
  const mPerLat = R * Math.PI / 180;
  const mPerLon = (R * Math.PI / 180) * Math.cos(latMid);
  
  const px = p.lng * mPerLon; const py = p.lat * mPerLat;
  const ax = a.lng * mPerLon; const ay = a.lat * mPerLat;
  const bx = b.lng * mPerLon; const by = b.lat * mPerLat;
  
  const l2 = (ax - bx) ** 2 + (ay - by) ** 2;
  if (l2 === 0) return getDistanceInMeters(p.lat, p.lng, a.lat, a.lng);
  
  let t = Math.max(0, Math.min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / l2));
  return Math.sqrt((px - (ax + t * (bx - ax))) ** 2 + (py - (ay + t * (by - ay))) ** 2);
}

export default function useNavigationEngine(route, currentLocation) {
  // Quản lý trạng thái vận hành hiện tại.
  const [navState, setNavState] = useState(NAV_STATES.IDLE);
  
  // Vị trí đoạn đường đang đi.
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  
  // Khoảng cách hiển thị ra UI.
  const [distanceToNextManeuver, setDistanceToNextManeuver] = useState(null);
  const [totalDistanceRemaining, setTotalDistanceRemaining] = useState(null);
  
  // Câu lệnh cho hệ thống phát giọng nói.
  const [voicePrompt, setVoicePrompt] = useState(null);

  // Lưu mốc đã nói để tránh nói lắp.
  const spokenMilestones = useRef({ 500: false, 100: false, 20: false });

  // Xóa cờ khi chuyển sang bước rẽ mới.
  useEffect(() => {
    spokenMilestones.current = { 500: false, 100: false, 20: false };
  }, [currentStepIndex]);

  // Bắt đầu hoặc làm lại lộ trình.
  const startNavigation = useCallback(() => {
    if (!route?.path?.length) return;
    setNavState(NAV_STATES.STARTING);
    setCurrentStepIndex(0);
    spokenMilestones.current = { 500: false, 100: false, 20: false }; 

    setTimeout(() => {
      setNavState(NAV_STATES.NAVIGATING);
      setVoicePrompt({ text: "Bắt đầu điều hướng. Hãy đi theo tuyến đường.", t: Date.now() });
    }, 500);
  }, [route]);

  // Tạm dừng việc báo đường.
  const pauseNavigation = useCallback(() => {
    if (navState === NAV_STATES.NAVIGATING) setNavState(NAV_STATES.PAUSED);
  }, [navState]);

  // Tiếp tục việc báo đường.
  const resumeNavigation = useCallback(() => {
    if (navState === NAV_STATES.PAUSED) setNavState(NAV_STATES.NAVIGATING);
  }, [navState]);

  // Dừng hẳn và dọn dẹp biến.
  const stopNavigation = useCallback(() => {
    setNavState(NAV_STATES.IDLE);
    setCurrentStepIndex(0);
    setDistanceToNextManeuver(null);
    setTotalDistanceRemaining(null);
    setVoicePrompt(null);
  }, []);

  // Vòng lặp chính xử lý GPS.
  useEffect(() => {
    // Bỏ qua nếu chưa chạy.
    if (navState !== NAV_STATES.NAVIGATING || !currentLocation || !route?.path) {
      return;
    }

    const path = route.path;
    const currentTarget = path[currentStepIndex];
    const prevTarget = currentStepIndex > 0 ? path[currentStepIndex - 1] : path[0];
    const finalDestination = path[path.length - 1];

    if (!currentTarget || !finalDestination) return;

    // Chuẩn hóa format tọa độ.
    const userPoint = {
      lat: currentLocation.latitude ?? currentLocation.lat,
      lng: currentLocation.longitude ?? currentLocation.lng,
    };
    const targetPoint = {
      lat: currentTarget.latitude ?? currentTarget.lat,
      lng: currentTarget.longitude ?? currentTarget.lng,
    };
    const prevPoint = {
      lat: prevTarget.latitude ?? prevTarget.lat,
      lng: prevTarget.longitude ?? prevTarget.lng,
    };

    // Tính khoảng cách đến đích.
    const dTarget = getDistanceInMeters(userPoint.lat, userPoint.lng, targetPoint.lat, targetPoint.lng);
    const dFinal = getDistanceInMeters(userPoint.lat, userPoint.lng, finalDestination.latitude ?? finalDestination.lat, finalDestination.longitude ?? finalDestination.lng);

    setDistanceToNextManeuver(Math.round(dTarget));
    setTotalDistanceRemaining(Math.round(dFinal));

    // Chốt trạng thái đã đến nơi.
    if (dFinal < 30) {
      setNavState(NAV_STATES.ARRIVED);
      setVoicePrompt({ text: "Bạn đã đến nơi an toàn.", t: Date.now() });
      return;
    }

    // Báo lỗi đi lạc hướng.
    const crossTrackDistance = getDistanceToSegmentMeters(userPoint, prevPoint, targetPoint);
    if (crossTrackDistance > OFF_ROUTE_THRESHOLD) {
      setNavState(NAV_STATES.OFF_ROUTE);
      setVoicePrompt({ text: "Bạn đã đi chệch hướng. Đang tính toán lại.", t: Date.now() });
      return;
    }

    // Đọc giọng nói theo mốc khoảng cách.
    const instructionText = currentTarget.instruction || "Tiếp tục đi thẳng";

    if (dTarget <= 500 && dTarget > 100 && !spokenMilestones.current[500]) {
      spokenMilestones.current[500] = true;
      setVoicePrompt({ text: `Trong 500 mét nữa, ${instructionText.toLowerCase()}`, t: Date.now() });
    } 
    else if (dTarget <= 100 && dTarget > 20 && !spokenMilestones.current[100]) {
      spokenMilestones.current[100] = true;
      setVoicePrompt({ text: `Trong 100 mét nữa, ${instructionText.toLowerCase()}`, t: Date.now() });
    }
    else if (dTarget <= 20 && !spokenMilestones.current[20]) {
      spokenMilestones.current[20] = true;
      setVoicePrompt({ text: instructionText, t: Date.now() });
    }

    // Chuyển mốc sau khi đọc xong.
    if (dTarget < 20 && currentStepIndex < path.length - 1) {
      setCurrentStepIndex((prev) => prev + 1);
    }

  }, [currentLocation, navState, route, currentStepIndex]);

  // Trả dữ liệu ra ngoài.
  return {
    state: navState,
    currentStepIndex,
    distanceToNextManeuver,
    totalDistanceRemaining,
    voicePrompt,
    actions: { 
      start: startNavigation, 
      pause: pauseNavigation, 
      resume: resumeNavigation, 
      stop: stopNavigation 
    },
  };
}