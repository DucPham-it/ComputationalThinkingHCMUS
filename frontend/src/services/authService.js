import api from "./api";

/** Login request.
 * Input: { identifier, password }
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
 * Input: { user_name, email, password }
 * Output: auth response with account info
 */
export async function register(payload) {
  const response = await api.post("/auth/register", payload);
  if (response.data?.access_token) {
    window.localStorage.setItem("access_token", response.data.access_token);
  }
  return response.data;
}

/** Update current user profile.
 * Input: { first_name, last_name, birth_date, gender?, address? }
 * Output: auth response with updated user
 */
export async function updateProfile(payload) {
  const response = await api.put("/auth/profile", payload);
  return response.data;
}
