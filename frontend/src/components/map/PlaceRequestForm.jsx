import { useMemo, useState } from "react";
import { Send, X } from "lucide-react";

import { createPlaceRequest } from "../../services/placeRequestService";
import { uploadPlaceImages, uploadReviewImages } from "../../services/uploadService";

/**
 * Place create/update/delete request form with optional image upload.
 *
 * Owner:
 * - Existing place request image upload flow.
 * - Not part of TV7's current Review Rating Filter assignment.
 * - Place request approval flow remains shared/admin flow.
 *
 * File input:
 * - targetPlace: selected map place or temporary map point.
 * - onSubmitted/onCancel callbacks.
 * - Place form fields and optional place/review image files.
 *
 * File output:
 * - Uploads selected place/review image files to Supabase Storage.
 * - Sends createPlaceRequest payload with image URL arrays.
 */

function getDatabasePlaceId(place) {
  /**
   * Owner:
   * - TV6/TV7 shared helper.
   *
   * Input:
   * - place: targetPlace selected from map.
   *
   * Output:
   * - positive integer database id or null for temporary/external places.
   */
  const numericId = Number(place?.id);
  return Number.isInteger(numericId) && numericId > 0 ? numericId : null;
}

function parseUrls(rawValue) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - rawValue: textarea content containing URLs separated by newline or comma.
   *
   * Output:
   * - clean non-empty URL string array.
   */
  return String(rawValue || "")
    .split(/\r?\n|,/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function getFiles(formData, name) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - formData: submitted FormData.
   * - name: file input field name.
   *
   * Output:
   * - up to 8 non-empty File objects.
   */
  return formData
    .getAll(name)
    .filter((file) => file instanceof File && file.size > 0)
    .slice(0, 8);
}

export default function PlaceRequestForm({ targetPlace, onSubmitted, onCancel }) {
  const databasePlaceId = getDatabasePlaceId(targetPlace);
  const defaultRequestType = databasePlaceId ? "update" : "create";
  const [requestType, setRequestType] = useState(defaultRequestType);
  const [status, setStatus] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const coordinates = useMemo(() => ({
    latitude: targetPlace?.latitude ?? targetPlace?.lat ?? "",
    longitude: targetPlace?.longitude ?? targetPlace?.lng ?? "",
  }), [targetPlace]);

  async function handleSubmit(event) {
    /**
     * Owner:
     * - TV7 for image upload behavior.
     *
     * Input:
     * - submit event from place request form.
     * - requestType state and targetPlace props.
     * - form fields for place data, review data, image URLs, image files.
     *
     * Output:
     * - uploads files to Supabase Storage.
     * - merges manually-entered URLs with uploaded URLs.
     * - submits createPlaceRequest payload.
     * - sets status message and calls onSubmitted on success.
     */
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const placeImageFiles = requestType === "delete" ? [] : getFiles(formData, "place_images");
    const reviewImageFiles = getFiles(formData, "review_images");
    const placeImageUrls = parseUrls(formData.get("place_image_urls"));
    const reviewImageUrls = parseUrls(formData.get("review_image_urls"));

    const payload = {
      request_type: requestType,
      place_id: databasePlaceId,
      title: String(formData.get("title") || "").trim() || null,
      category: String(formData.get("category") || "").trim() || null,
      address_text: String(formData.get("address_text") || "").trim() || null,
      latitude: formData.get("latitude") ? Number(formData.get("latitude")) : null,
      longitude: formData.get("longitude") ? Number(formData.get("longitude")) : null,
      price_range: String(formData.get("price_range") || "").trim() || null,
      price_level: formData.get("price_level") ? Number(formData.get("price_level")) : null,
      website: String(formData.get("website") || "").trim() || null,
      phone: String(formData.get("phone") || "").trim() || null,
      descriptions: String(formData.get("descriptions") || "").trim() || null,
      request_note: String(formData.get("request_note") || "").trim() || null,
      review_content: String(formData.get("review_content") || "").trim() || null,
      review_rating: formData.get("review_rating") ? Number(formData.get("review_rating")) : null,
      place_image_urls: placeImageUrls,
      review_image_urls: reviewImageUrls,
    };

    try {
      setSubmitting(true);
      setStatus("");
      if (placeImageFiles.length || reviewImageFiles.length) {
        setStatus("Uploading images...");
      }

      const [uploadedPlaceImages, uploadedReviewImages] = await Promise.all([
        placeImageFiles.length ? uploadPlaceImages(placeImageFiles) : Promise.resolve({ urls: [] }),
        reviewImageFiles.length ? uploadReviewImages(reviewImageFiles) : Promise.resolve({ urls: [] }),
      ]);

      payload.place_image_urls = [...placeImageUrls, ...(uploadedPlaceImages.urls || [])];
      payload.review_image_urls = [...reviewImageUrls, ...(uploadedReviewImages.urls || [])];

      await createPlaceRequest(payload);
      setStatus("Request submitted. An approved admin can review it now.");
      onSubmitted?.();
    } catch (error) {
      setStatus(error?.response?.data?.detail || "Could not submit this request. Please log in and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!targetPlace) {
    return null;
  }

  return (
    <form className="card" onSubmit={handleSubmit} style={{ display: "grid", gap: "16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: "12px", alignItems: "flex-start" }}>
        <div>
          <h2 style={{ margin: 0 }}>Suggest a place change</h2>
          <p style={{ margin: "6px 0 0 0" }}>
            Submit a new place, an edit, or a delete request for admin approval.
          </p>
        </div>
        <button type="button" className="btn-outline" onClick={onCancel} style={{ padding: "8px 12px", borderRadius: "12px" }}>
          <X size={16} />
        </button>
      </div>

      <div style={{ display: "grid", gap: "12px", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
        <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
          Request type
          <select value={requestType} onChange={(event) => setRequestType(event.target.value)}>
            <option value="create">Add new place</option>
            <option value="update" disabled={!databasePlaceId}>Suggest edit</option>
            <option value="delete" disabled={!databasePlaceId}>Suggest delete</option>
          </select>
        </label>

        <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
          Place name
          <input name="title" defaultValue={targetPlace.name || ""} disabled={requestType === "delete"} />
        </label>

        <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
          Category
          <input name="category" defaultValue={targetPlace.primary_type || targetPlace.category || ""} disabled={requestType === "delete"} />
        </label>

        <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
          Phone
          <input name="phone" defaultValue={targetPlace.contact_phone || ""} disabled={requestType === "delete"} />
        </label>
      </div>

      <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
        Address
        <textarea name="address_text" rows={2} defaultValue={targetPlace.address || ""} disabled={requestType === "delete"} />
      </label>

      <div style={{ display: "grid", gap: "12px", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
        <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
          Latitude
          <input name="latitude" type="number" step="any" defaultValue={coordinates.latitude} disabled={requestType === "delete"} />
        </label>
        <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
          Longitude
          <input name="longitude" type="number" step="any" defaultValue={coordinates.longitude} disabled={requestType === "delete"} />
        </label>
        <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
          Price range
          <input name="price_range" placeholder="₫₫" defaultValue={targetPlace.price_range || ""} disabled={requestType === "delete"} />
        </label>
        <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
          Price level
          <input name="price_level" type="number" min="0" max="4" defaultValue={targetPlace.price_level ?? ""} disabled={requestType === "delete"} />
        </label>
      </div>

      <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
        Website
        <input name="website" defaultValue={targetPlace.website || ""} disabled={requestType === "delete"} />
      </label>

      <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
        Description / edit details
        <textarea name="descriptions" rows={3} defaultValue={targetPlace.description || ""} disabled={requestType === "delete"} />
      </label>

      <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
        Request note
        <textarea name="request_note" rows={3} placeholder="Tell admins what should be changed and why." />
      </label>

      <div style={{ display: "grid", gap: "12px", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
        <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
          Review rating
          <select name="review_rating" defaultValue="">
            <option value="">No review rating</option>
            {[5, 4, 3, 2, 1].map((rating) => (
              <option key={rating} value={rating}>{rating} stars</option>
            ))}
          </select>
        </label>
        <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
          Place image URLs
          <textarea name="place_image_urls" rows={3} placeholder="One URL per line" />
        </label>
      </div>

      <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
        Place image files
        <input
          name="place_images"
          type="file"
          accept="image/png,image/jpeg,image/webp,image/gif"
          multiple
          disabled={requestType === "delete" || submitting}
        />
      </label>

      <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
        Review content
        <textarea name="review_content" rows={3} placeholder="Optional review to attach if admin approves." />
      </label>

      <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
        Review image URLs
        <textarea name="review_image_urls" rows={3} placeholder="One URL per line" />
      </label>

      <label style={{ display: "grid", gap: "8px", fontWeight: 700 }}>
        Review image files
        <input
          name="review_images"
          type="file"
          accept="image/png,image/jpeg,image/webp,image/gif"
          multiple
          disabled={submitting}
        />
      </label>

      {status ? (
        <p style={{ margin: 0, padding: "12px 14px", borderRadius: "14px", background: "#eff6ff", color: "var(--color-primary-dark)", fontWeight: 700 }}>
          {status}
        </p>
      ) : null}

      <button className="btn-primary" type="submit" disabled={submitting} style={{ padding: "14px 18px", borderRadius: "16px", fontWeight: 800 }}>
        <Send size={18} style={{ marginRight: "8px" }} />
        {submitting ? "Submitting..." : "Submit for admin review"}
      </button>
    </form>
  );
}
