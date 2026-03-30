import api from "./api";

/**
 * Input:
 * - { origin, destination, travel_mode? }
 *
 * Output:
 * - route summary and steps
 */
export async function getRoute(params) {
  const response = await api.get("/routes/plan", { params });
  return response.data;
}
