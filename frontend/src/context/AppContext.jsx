import { createContext, useEffect, useMemo, useState } from "react";

/**
 * Shared app-level UI state.
 *
 * Candidate fields to add later:
 * - selectedPlace
 * - currentLocation
 * - recommendationFilters
 * - weatherSummary
 */
export const AppContext = createContext(null);

const APP_STATE_STORAGE_KEY = "app_shared_state";
const DEFAULT_APP_STATE = {
  selectedPlace: null,
  currentLocation: null,
  recommendationPlaces: [],
};

function normalizeLocation(location) {
  if (!location) {
    return null;
  }

  const latitude = location.latitude ?? location.lat;
  const longitude = location.longitude ?? location.lng;

  if (latitude == null || longitude == null) {
    return null;
  }

  return {
    latitude,
    longitude,
  };
}

function readStoredAppState() {
  if (typeof window === "undefined") {
    return DEFAULT_APP_STATE;
  }

  const rawState = window.localStorage.getItem(APP_STATE_STORAGE_KEY);
  if (!rawState) {
    return DEFAULT_APP_STATE;
  }

  try {
    const parsedState = JSON.parse(rawState);
    return {
      selectedPlace: parsedState.selectedPlace ?? null,
      currentLocation: normalizeLocation(parsedState.currentLocation),
      recommendationPlaces: parsedState.recommendationPlaces ?? [],
    };
  } catch {
    window.localStorage.removeItem(APP_STATE_STORAGE_KEY);
    return DEFAULT_APP_STATE;
  }
}

export function AppProvider({ children }) {
  const storedState = readStoredAppState();
  const [selectedPlace, setSelectedPlace] = useState(storedState.selectedPlace);
  const [currentLocation, setCurrentLocation] = useState(storedState.currentLocation);
  const [recommendationPlaces, setRecommendationPlaces] = useState(
    storedState.recommendationPlaces
  );
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    window.localStorage.setItem(
      APP_STATE_STORAGE_KEY,
      JSON.stringify({
        selectedPlace,
        currentLocation,
        recommendationPlaces,
      })
    );
  }, [currentLocation, recommendationPlaces, selectedPlace]);

  function resetAppState() {
    setSelectedPlace(DEFAULT_APP_STATE.selectedPlace);
    setCurrentLocation(DEFAULT_APP_STATE.currentLocation);
    setRecommendationPlaces(DEFAULT_APP_STATE.recommendationPlaces);
    setHasSearched(false);

    if (typeof window !== "undefined") {
      window.localStorage.removeItem(APP_STATE_STORAGE_KEY);
    }
  }

  const value = useMemo(
    () => ({
      selectedPlace,
      setSelectedPlace,
      currentLocation,
      setCurrentLocation,
      recommendationPlaces,
      setRecommendationPlaces,
      hasSearched,
      setHasSearched,
      resetAppState
    }),
    [currentLocation, recommendationPlaces, selectedPlace, hasSearched]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
