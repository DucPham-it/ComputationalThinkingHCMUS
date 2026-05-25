import { formatDistanceVi } from "../utils/navigationFormat";

const VOICE_LANG = "vi-VN";
let speechQueue = [];
let currentUtterance = null;
let cachedViVoice = null;
let voicesLoaded = false;

function getSpeechSynthesis() {
  return typeof window !== "undefined" ? window.speechSynthesis : null;
}

function loadVoices() {
  const synthesis = getSpeechSynthesis();
  if (!synthesis) return;
  const voices = synthesis.getVoices();
  if (voices.length > 0) {
    cachedViVoice = voices.find(
      (v) => v.lang?.startsWith("vi") || v.name?.toLowerCase().includes("vietnam")
    ) || null;
    voicesLoaded = true;
  }
}

if (typeof window !== "undefined" && window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = loadVoices;
  loadVoices();
}

export function getAvailableVoices() {
  const synthesis = getSpeechSynthesis();
  if (!synthesis) return [];
  return synthesis.getVoices();
}

export function hasVietnameseVoice() {
  return cachedViVoice !== null;
}

function applyViVoice(utterance) {
  if (!voicesLoaded) loadVoices();
  if (cachedViVoice) utterance.voice = cachedViVoice;
  utterance.lang = VOICE_LANG;
  utterance.rate = 0.9;
  utterance.pitch = 1;
  utterance.volume = 1;
}

function speakNext() {
  const synthesis = getSpeechSynthesis();
  if (!synthesis || !speechQueue.length) {
    currentUtterance = null;
    return;
  }
  const text = speechQueue.shift();
  const utterance = new SpeechSynthesisUtterance(text);
  applyViVoice(utterance);
  utterance.onend = () => { currentUtterance = null; speakNext(); };
  utterance.onerror = () => { currentUtterance = null; speakNext(); };
  currentUtterance = utterance;
  synthesis.speak(utterance);
}

const MANEUVER_TRANSLATIONS = {
  arrive: "Bạn đã đến nơi",
  depart: "Bắt đầu",
  continue: "Đi thẳng",
  straight: "Đi thẳng",
  turn: "Rẽ",
  roundabout: "Vào vòng xuyến",
  rotary: "Đi vòng xoay",
  merge: "Nhập làn",
  ramp: "Đi vào làn đường",
  fork: "Rẽ vào ngã ba",
  end_of_road: "Cuối đường",
  uturn: "Quay đầu",
  exit_roundabout: "Ra khỏi vòng xuyến",
  turn_left: "Rẽ trái",
  turn_right: "Rẽ phải",
  sharp_left: "Rẽ gắt trái",
  sharp_right: "Rẽ gắt phải",
  slight_left: "Rẽ nhẹ trái",
  slight_right: "Rẽ nhẹ phải",
  merge_left: "Nhập làn trái",
  merge_right: "Nhập làn phải",
  off_ramp: "Ra khỏi đường cao tốc",
  on_ramp: "Lên đường cao tốc",
};

function normalizeManeuverKey(type, modifier) {
  if (!type) {
    return "continue";
  }

  const key = modifier ? `${type}_${modifier}` : type;
  return key;
}

export function isVoiceSupported() {
  const synthesis = getSpeechSynthesis();
  return (
    synthesis &&
    typeof SpeechSynthesisUtterance === "function" &&
    typeof synthesis.speak === "function"
  );
}

export function isSpeaking() {
  const synthesis = getSpeechSynthesis();
  return !!(synthesis && (synthesis.speaking || synthesis.pending || currentUtterance));
}

export function cancelSpeech() {
  const synthesis = getSpeechSynthesis();
  speechQueue = [];
  currentUtterance = null;
  if (synthesis) synthesis.cancel();
}

export function speakInstruction(text, options = { interrupt: false }) {
  if (!isVoiceSupported() || !text) return false;
  if (options.interrupt) cancelSpeech();
  speechQueue.push(text);
  const synthesis = getSpeechSynthesis();
  if (synthesis && !synthesis.speaking && !currentUtterance) speakNext();
  return true;
}

export function translateManeuver(type, modifier) {
  const key = normalizeManeuverKey(type, modifier);
  if (MANEUVER_TRANSLATIONS[key]) {
    return MANEUVER_TRANSLATIONS[key];
  }

  if (type === "turn") {
    return "Rẽ";
  }

  if (type === "continue") {
    return "Đi thẳng";
  }

  return "Tiếp tục";
}

export function buildVoiceInstruction(step) {
  if (!step) {
    return "";
  }

  const distanceText =
    step.distance_text ||
    (typeof step.distance === "number" ? formatDistanceVi(step.distance) : "") ||
    "";

  const type = step?.maneuver?.type || step?.type;
  const modifier = step?.maneuver?.modifier || step?.modifier;
  const name = step?.maneuver?.name || step?.name || "";
  const maneuverText = translateManeuver(type, modifier);

  if (maneuverText === "Bạn đã đến nơi") {
    return maneuverText;
  }

  const nameSuffix = name ? ` vào ${name}` : "";
  if (maneuverText === "Đi thẳng" && !nameSuffix) {
    return distanceText ? `Tiếp tục trong ${distanceText}` : "Tiếp tục";
  }

  if (distanceText) {
    return `Sau ${distanceText}, ${maneuverText}${nameSuffix}`;
  }

  return `${maneuverText}${nameSuffix}`;
}
