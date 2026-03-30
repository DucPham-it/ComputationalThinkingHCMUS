import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

/**
 * Output:
 * - auth context object
 */
export function useAuth() {
  return useContext(AuthContext);
}
