import { createContext, useMemo, useState } from "react";

/**
 * Authentication state container.
 *
 * TODO:
 * - persist JWT to localStorage or cookie
 * - expose login/logout helper methods
 */
export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const value = useMemo(
    () => ({
      user,
      setUser,
      isAuthenticated: Boolean(user)
    }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
