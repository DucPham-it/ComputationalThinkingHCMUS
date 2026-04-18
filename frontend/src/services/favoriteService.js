import api from "./api";

/**
 * Output:
 * - list of current user favorite places
 */
export async function fetchFavorites() {
  const response = await api.get("/favorites");
  return response.data;
}

export async function addFavorite(placeId) {
  await api.post(`/favorites/${placeId}`);
}

export async function removeFavorite(placeId) {
  await api.delete(`/favorites/${placeId}`);
}
