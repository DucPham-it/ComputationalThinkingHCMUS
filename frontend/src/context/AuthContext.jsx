import { createContext, useEffect, useMemo, useState } from "react";

/**
 * Authentication state container.
 */
export const AuthContext = createContext(null);

const USER_STORAGE_KEY = "auth_user";
const TOKEN_STORAGE_KEY = "access_token";

export function hasCompletedProfile(user) {
  return Boolean(user?.first_name && user?.last_name && user?.birth_date);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    if (typeof window === "undefined") {
      return null;
    }

    if (!window.localStorage.getItem(TOKEN_STORAGE_KEY)) {
      window.localStorage.removeItem(USER_STORAGE_KEY);
      return null;
    }

    const rawUser = window.localStorage.getItem(USER_STORAGE_KEY);
    if (!rawUser) {
      return null;
    }

    try {
      return JSON.parse(rawUser);
    } catch {
      window.localStorage.removeItem(USER_STORAGE_KEY);
      return null;
    }
  });

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    if (user) {
      window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
      return;
    }

    window.localStorage.removeItem(USER_STORAGE_KEY);
  }, [user]);

  function logout() {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY);
      window.localStorage.removeItem(USER_STORAGE_KEY);
    }
    setUser(null);
  }

  const value = useMemo(
    () => ({
      user,
      setUser,
      logout,
      isAuthenticated: Boolean(user),
      hasCompletedProfile: hasCompletedProfile(user)
    }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
