import { useEffect, useState } from "react";

/**
 * Input:
 * - value: any state value to debounce
 * - delay: debounce time in ms
 *
 * Output:
 * - debounced value for search/API efficiency
 */
export function useDebounce(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
