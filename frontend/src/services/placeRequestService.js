import api from "./api";

export async function createPlaceRequest(payload) {
  const response = await api.post("/place-requests", payload);
  return response.data;
}

export async function fetchMyPlaceRequests() {
  const response = await api.get("/place-requests/my");
  return response.data;
}

