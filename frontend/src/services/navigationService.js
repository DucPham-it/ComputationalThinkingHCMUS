import { getRoute } from "./routeService";
import { extractStepsFromRoute } from "../utils/navigationHelpers";

function formatLocation(value) {
  if (!value) {
    return "";
  }

  if (typeof value === "string") {
    return value;
  }

  const latitude = value.latitude ?? value.lat;
  const longitude = value.longitude ?? value.lng;

  if (latitude === undefined || longitude === undefined) {
    return "";
  }

  return `${latitude},${longitude}`;
}

export async function requestReroute({ currentPosition, destination, travelMode }) {
  const origin = formatLocation(currentPosition);
  const dest = formatLocation(destination);

  if (!origin || !dest) {
    throw new Error("Invalid reroute arguments");
  }

  return getRoute({
    origin,
    destination: dest,
    travel_mode: travelMode ? String(travelMode).toLowerCase() : "driving",
  });
}

export function shouldReroute(isOffRoute, lastRerouteTime) {
  if (!isOffRoute) {
    return false;
  }

  if (!lastRerouteTime) {
    return true;
  }

  const elapsed = Date.now() - new Date(lastRerouteTime).getTime();
  return elapsed >= 15000;
}

export function buildNavigationSummary(routeInfo, currentStepIndex = 0) {
  const steps = extractStepsFromRoute(routeInfo);
  const currentStep = steps[currentStepIndex] || null;
  const nextStep = steps[currentStepIndex + 1] || null;

  return {
    origin: routeInfo?.origin || null,
    destination: routeInfo?.destination || null,
    distanceText: routeInfo?.distance_text || routeInfo?.distance || null,
    durationText: routeInfo?.duration_text || routeInfo?.duration || null,
    currentStep,
    nextStep,
    remainingSteps: steps.slice(currentStepIndex + 1),
    totalSteps: steps.length,
  };
}
