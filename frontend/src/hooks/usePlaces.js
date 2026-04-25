/**
 * Hook for loading recommendation list.
 *
 * Input:
 * - initialQuery: initial free-text query string
 *
 * Output:
 * - places array
 * - setPlaces state updater
 *
 * TODO later:
 * - return loading and error state
 * - accept structured filter object instead of only query
 */
import { useEffect, useState } from "react";
import { fetchRecommendations } from "../services/recommendationService";

export function usePlaces(initialQuery = "") {
  const [places, setPlaces] = useState([]);

  useEffect(() => {
    fetchRecommendations({ query: initialQuery })
      .then((data) => setPlaces(data.items ?? []))
      .catch(console.error);
  }, [initialQuery]);

  return { places, setPlaces };
}
