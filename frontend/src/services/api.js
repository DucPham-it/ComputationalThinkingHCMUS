/**
 * Shared Axios instance.
 *
 * Input:
 * - base URL from Vite environment
 *
 * Output:
 * - preconfigured Axios client for all frontend API calls
 */
import axios from "axios";

export const AUTH_UNAUTHORIZED_EVENT = "auth:unauthorized";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"
});

api.interceptors.request.use((config) => {
  const token = window.localStorage.getItem("access_token");

  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401 && typeof window !== "undefined") {
      window.localStorage.removeItem("access_token");
      window.localStorage.removeItem("auth_user");
      window.dispatchEvent(new Event(AUTH_UNAUTHORIZED_EVENT));
    }

    return Promise.reject(error);
  }
);

export default api;
