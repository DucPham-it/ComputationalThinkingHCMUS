import api from "./api";

/**
 * Input:
 * - city or later coordinates
 *
 * Output:
 * - weather summary for UI or recommendation explanation
 */
export async function fetchWeather(params) {
  const response = await api.get("/weather", { params });
  return response.data;
}
