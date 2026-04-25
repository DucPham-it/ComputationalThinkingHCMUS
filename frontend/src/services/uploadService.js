import api from "./api";

/**
 * Upload API calls.
 *
 * Owner:
 * - Legacy/completed media upload flow.
 * - Not part of TV7's current Review Rating Filter assignment.
 *
 * File input:
 * - File or FileList objects selected from Profile, ReviewForm, PlaceRequestForm.
 *
 * File output:
 * - Supabase Storage public URLs returned by backend upload routes.
 */

function buildFilesPayload(files) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - files: FileList or File[] from a multiple file input.
   *
   * Output:
   * - FormData with non-empty files appended under key "files".
   */
  const formData = new FormData();
  Array.from(files || []).forEach((file) => {
    if (file?.size > 0) {
      formData.append("files", file);
    }
  });
  return formData;
}

export async function uploadAvatar(file) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - file: single avatar image selected in Profile.
   *
   * Output:
   * - AvatarUploadResponse:
   *   { url, filename, content_type, size_bytes, user }
   */
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/uploads/avatar", formData);
  return response.data;
}

export async function uploadPlaceImages(files) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - files: FileList/File[] of place images from PlaceRequestForm.
   *
   * Output:
   * - UploadedImagesResponse:
   *   { items, urls }
   */
  const response = await api.post("/uploads/place-images", buildFilesPayload(files));
  return response.data;
}

export async function uploadReviewImages(files) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - files: FileList/File[] of review images from ReviewForm/PlaceRequestForm.
   *
   * Output:
   * - UploadedImagesResponse:
   *   { items, urls }
   */
  const response = await api.post("/uploads/review-images", buildFilesPayload(files));
  return response.data;
}
