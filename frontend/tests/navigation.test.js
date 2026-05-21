import { describe, expect, test } from "vitest";
import {
  formatDistanceVi,
  formatDurationVi,
  formatETA,
  formatRemainingText,
} from "../src/utils/navigationFormat";
import {
  translateManeuver,
  buildVoiceInstruction,
} from "../src/services/voiceGuidanceService";

describe("navigationFormat utilities", () => {
  test("formatDistanceVi format meters correctly", () => {
    expect(formatDistanceVi(150)).toBe("150 m");
    expect(formatDistanceVi(1250)).toBe("1,3 km"); // 1250 meters formats with maximumFractionDigits: 1 -> 1,3 km (Vietnamese format uses comma)
    expect(formatDistanceVi(0)).toBe("0 m");
    expect(formatDistanceVi(null)).toBe("");
  });

  test("formatDurationVi format seconds correctly", () => {
    expect(formatDurationVi(45)).toBe("1 phút"); // minimum duration is 1 minute (rounded)
    expect(formatDurationVi(120)).toBe("2 phút");
    expect(formatDurationVi(3600)).toBe("1 giờ");
    expect(formatDurationVi(3720)).toBe("1 giờ 2 phút");
    expect(formatDurationVi(null)).toBe("");
  });

  test("formatETA formats dates correctly", () => {
    const fixedDate = new Date("2026-05-21T22:30:00");
    expect(formatETA(fixedDate)).toBe("22:30");
    expect(formatETA(null)).toBe("");
  });

  test("formatRemainingText joins distance and duration correctly", () => {
    expect(formatRemainingText(1250, 3720)).toBe("Còn 1,3 km · 1 giờ 2 phút");
    expect(formatRemainingText(150, null)).toBe("150 m");
    expect(formatRemainingText(null, null)).toBe("");
  });
});

describe("voiceGuidanceService utilities", () => {
  test("translateManeuver translates types and modifiers", () => {
    expect(translateManeuver("arrive", null)).toBe("Bạn đã đến nơi");
    expect(translateManeuver("turn", "left")).toBe("Rẽ trái");
    expect(translateManeuver("turn", "right")).toBe("Rẽ phải");
    expect(translateManeuver("uturn", null)).toBe("Quay đầu");
    expect(translateManeuver(null, null)).toBe("Đi thẳng");
  });

  test("buildVoiceInstruction constructs correct spoken guide phrases", () => {
    const stepArrive = {
      distance: 0,
      type: "arrive",
    };
    expect(buildVoiceInstruction(stepArrive)).toBe("Bạn đã đến nơi");

    const stepTurn = {
      distance: 500,
      type: "turn",
      modifier: "left",
      name: "Nguyễn Huệ",
    };
    // formatDistanceVi(500) -> "500 m"
    expect(buildVoiceInstruction(stepTurn)).toBe("Sau 500 m, Rẽ trái vào Nguyễn Huệ");

    const stepContinue = {
      distance: 200,
      type: "continue",
    };
    expect(buildVoiceInstruction(stepContinue)).toBe("Tiếp tục trong 200 m");

    expect(buildVoiceInstruction(null)).toBe("");
  });
});
