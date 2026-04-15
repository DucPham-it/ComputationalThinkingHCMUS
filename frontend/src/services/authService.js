import api from "./api";

/** Login request.
 * Input: { email, password }
 * Output: auth response with message and optional token
 */
export async function login(payload) {
  const response = await api.post("/auth/login", payload);
  if (response.data?.access_token) {
    window.localStorage.setItem("access_token", response.data.access_token);
  }
  return response.data;
}

/** Register request.
 * Input: { email, password }
 * Output: auth response with account info
 */
export async function register(payload) {
  const response = await api.post("/auth/register", payload);
  if (response.data?.access_token) {
    window.localStorage.setItem("access_token", response.data.access_token);
  }
  return response.data;
}
