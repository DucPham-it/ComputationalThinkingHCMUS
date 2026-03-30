import api from "./api";

/**
 * Output:
 * - list of current user favorite places
 */
export async function fetchFavorites() {
  const response = await api.get("/favorites");
  return response.data;
}
