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

function readStoredAppState() {
  if (typeof window === "undefined") {
    return {
      selectedPlace: null,
      currentLocation: null,
      recommendationPlaces: [],
    };
  }

  const rawState = window.localStorage.getItem(APP_STATE_STORAGE_KEY);
  if (!rawState) {
    return {
      selectedPlace: null,
      currentLocation: null,
      recommendationPlaces: [],
    };
  }

  try {
    const parsedState = JSON.parse(rawState);
    return {
      selectedPlace: parsedState.selectedPlace ?? null,
      currentLocation: parsedState.currentLocation ?? null,
      recommendationPlaces: parsedState.recommendationPlaces ?? [],
    };
  } catch {
    window.localStorage.removeItem(APP_STATE_STORAGE_KEY);
    return {
      selectedPlace: null,
      currentLocation: null,
      recommendationPlaces: [],
    };
  }
}

export function AppProvider({ children }) {
  const storedState = readStoredAppState();
  const [selectedPlace, setSelectedPlace] = useState(storedState.selectedPlace);
  const [currentLocation, setCurrentLocation] = useState(storedState.currentLocation);
  const [recommendationPlaces, setRecommendationPlaces] = useState(
    storedState.recommendationPlaces
  );

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

  const value = useMemo(
    () => ({
      selectedPlace,
      setSelectedPlace,
      currentLocation,
      setCurrentLocation,
      recommendationPlaces,
      setRecommendationPlaces
    }),
    [currentLocation, recommendationPlaces, selectedPlace]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
