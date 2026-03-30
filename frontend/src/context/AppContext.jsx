import { createContext, useMemo, useState } from "react";

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

export function AppProvider({ children }) {
  const [selectedPlace, setSelectedPlace] = useState(null);

  const value = useMemo(
    () => ({
      selectedPlace,
      setSelectedPlace
    }),
    [selectedPlace]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
