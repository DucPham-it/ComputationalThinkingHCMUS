import api from "./api";

export async function fetchAdminProfile() {
  const response = await api.get("/admin/me");
  return response.data;
}

export async function applyForAdminAccess() {
  const response = await api.post("/admin/apply");
  return response.data;
}

export async function fetchAdminMembers() {
  const response = await api.get("/admin/members");
  return response.data;
}

export async function approveAdminMember(userId) {
  const response = await api.post(`/admin/members/${userId}/approve`);
  return response.data;
}

export async function rejectAdminMember(userId) {
  const response = await api.post(`/admin/members/${userId}/reject`);
  return response.data;
}

export async function fetchPlaceRequests(statusFilter = "pending") {
  const response = await api.get("/admin/place-requests", {
    params: statusFilter ? { status_filter: statusFilter } : {},
  });
  return response.data;
}

export async function approvePlaceRequest(requestId, note = "") {
  const response = await api.post(`/admin/place-requests/${requestId}/approve`, { note });
  return response.data;
}

export async function rejectPlaceRequest(requestId, note = "") {
  const response = await api.post(`/admin/place-requests/${requestId}/reject`, { note });
  return response.data;
}

