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

export default api;
