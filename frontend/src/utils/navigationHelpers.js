export function extractStepsFromRoute(routeInfo) {
  const rawSteps = routeInfo?.steps || [];
  return rawSteps.map((step, index) => {
    const maneuver = step?.maneuver || {};
    return {
      index,
      instruction: step?.instruction || maneuver?.instruction || "",
      distanceText: step?.distance_text || step?.distance || "",
      durationText: step?.duration_text || step?.duration || "",
      distanceMeters: typeof step?.distance === "number" ? step.distance : null,
      maneuverType: maneuver?.type || step?.type || "continue",
      modifier: maneuver?.modifier || step?.modifier || null,
      name: maneuver?.name || step?.name || "",
      icon: getManeuverIcon(maneuver?.type || step?.type, maneuver?.modifier || step?.modifier),
      geometry: step?.geometry || step?.path || null,
    };
  });
}

export function buildFullPath(steps) {
  if (!Array.isArray(steps)) {
    return [];
  }

  const fullPath = [];

  steps.forEach((step) => {
    const geometry = step?.geometry;
    if (!geometry) {
      return;
    }

    if (Array.isArray(geometry)) {
      geometry.forEach((item) => {
        if (!Array.isArray(item) || item.length < 2) {
          return;
        }
        const [longitude, latitude] = item;
        fullPath.push({ latitude, longitude });
      });
      return;
    }

    if (geometry.coordinates && Array.isArray(geometry.coordinates)) {
      geometry.coordinates.forEach((item) => {
        if (!Array.isArray(item) || item.length < 2) {
          return;
        }
        const [longitude, latitude] = item;
        fullPath.push({ latitude, longitude });
      });
      return;
    }

    if (Array.isArray(step?.path)) {
      step.path.forEach((item) => {
        if (!item || typeof item !== "object") {
          return;
        }
        fullPath.push({ latitude: item.latitude, longitude: item.longitude });
      });
    }
  });

  return fullPath;
}

export function getManeuverIcon(type, modifier) {
  const key = modifier ? `${type}_${modifier}` : type;
  switch (key) {
    case "turn_left":
      return "arrow-left";
    case "turn_right":
      return "arrow-right";
    case "turn_slight_left":
      return "arrow-small-left";
    case "turn_slight_right":
      return "arrow-small-right";
    case "turn_sharp_left":
      return "arrow-rotate-left";
    case "turn_sharp_right":
      return "arrow-rotate-right";
    case "roundabout":
    case "exit_roundabout":
      return "roundabout";
    case "uturn":
      return "uturn";
    case "merge":
    case "merge_left":
    case "merge_right":
      return "merge";
    case "fork":
      return "fork";
    case "ramp":
    case "on_ramp":
    case "off_ramp":
      return "ramp";
    case "arrive":
      return "finish";
    case "depart":
      return "start";
    case "continue":
    case "straight":
    default:
      return "arrow-up";
  }
}

export function isNavigationSupported() {
  return (
    typeof window !== "undefined" &&
    "speechSynthesis" in window &&
    typeof window.SpeechSynthesisUtterance === "function" &&
    "geolocation" in navigator
  );
}
