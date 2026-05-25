import api from "./api";

export async function fetchSocialFeed() {
  const response = await api.get("/social/feed");
  return response.data;
}

export async function fetchVisitedPlaces() {
  const response = await api.get("/social/visited-places");
  return response.data;
}

export async function recordVisitedPlace(payload) {
  const response = await api.post("/social/visited-places", payload);
  return response.data;
}

export async function createSocialPost(payload) {
  const response = await api.post("/social/posts", payload);
  return response.data;
}

export async function updateSocialPost(postId, payload) {
  const response = await api.put(`/social/posts/${postId}`, payload);
  return response.data;
}

export async function likeSocialPost(postId) {
  const response = await api.post(`/social/posts/${postId}/like`);
  return response.data;
}

export async function unlikeSocialPost(postId) {
  const response = await api.delete(`/social/posts/${postId}/like`);
  return response.data;
}

export async function addSocialComment(postId, payload) {
  const response = await api.post(`/social/posts/${postId}/comments`, payload);
  return response.data;
}

export async function shareSocialPost(postId) {
  const response = await api.post(`/social/posts/${postId}/share`);
  return response.data;
}

export async function unshareSocialPost(postId) {
  const response = await api.delete(`/social/posts/${postId}/share`);
  return response.data;
}

export async function fetchMySocialProfile() {
  const response = await api.get("/social/profile/me");
  return response.data;
}
