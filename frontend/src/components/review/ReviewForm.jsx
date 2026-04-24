import { ImagePlus, MessageSquarePlus, ShieldAlert, Star, X } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { createReview } from "../../services/reviewService";
import { uploadReviewImages } from "../../services/uploadService";

/**
 * Review creation form with optional image upload.
 *
 * Owner:
 * - TV7: Media Upload + Review Avatar.
 *
 * File input:
 * - placeId: database place id from PlaceDetail.
 * - onSubmitted: optional callback after review is created.
 * - User-selected review image files.
 *
 * File output:
 * - Uploads review images to Supabase Storage.
 * - Sends createReview payload with place_id, content, rating, image_urls.
 * - Renders preview/remove state and submit errors.
 */

const RATING_OPTIONS = [5, 4, 3, 2, 1];

export default function ReviewForm({ placeId, onSubmitted }) {
  const [rating, setRating] = useState(5);
  const [content, setContent] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [imageFiles, setImageFiles] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const imageInputRef = useRef(null);

  const normalizedPlaceId = useMemo(() => {
    const numericId = Number(placeId);
    return Number.isInteger(numericId) && numericId > 0 ? numericId : null;
  }, [placeId]);

  const hasToken = typeof window !== "undefined" && Boolean(window.localStorage.getItem("access_token"));

  useEffect(() => {
    const previewUrls = imageFiles.map((file) => URL.createObjectURL(file));
    setImagePreviews(previewUrls);
    return () => {
      previewUrls.forEach((url) => URL.revokeObjectURL(url));
    };
  }, [imageFiles]);

  function handleImageChange(event) {
    /**
     * Owner:
     * - TV7.
     *
     * Input:
     * - event.target.files from review image input.
     *
     * Output:
     * - imageFiles state with up to 8 non-empty files.
     */
    setImageFiles(Array.from(event.target.files || []).filter((file) => file.size > 0).slice(0, 8));
  }

  function removeImage(index) {
    /**
     * Owner:
     * - TV7.
     *
     * Input:
     * - index: preview/file index selected by user.
     *
     * Output:
     * - removes that file from imageFiles and clears file input value.
     */
    setImageFiles((currentFiles) => currentFiles.filter((_, fileIndex) => fileIndex !== index));
    if (imageInputRef.current) {
      imageInputRef.current.value = "";
    }
  }

  async function handleSubmit(event) {
    /**
     * Owner:
     * - TV7.
     *
     * Input:
     * - submit event from ReviewForm.
     * - rating/content/imageFiles component state.
     *
     * Output:
     * - uploads selected images first.
     * - creates review with image_urls.
     * - resets form and calls onSubmitted(result) on success.
     * - sets user-facing error on validation/upload/API failure.
     */
    event.preventDefault();

    if (!normalizedPlaceId) {
      setError("Place ID is missing or invalid.");
      return;
    }

    if (!content.trim()) {
      setError("Please write a short review before submitting.");
      return;
    }

    if (!hasToken) {
      setError("Please log in before submitting a review.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      setSuccess("");

      const uploadedImages = imageFiles.length ? await uploadReviewImages(imageFiles) : { urls: [] };
      const result = await createReview({
        place_id: normalizedPlaceId,
        content: content.trim(),
        rating: Number(rating),
        image_urls: uploadedImages.urls || [],
      });

      setContent("");
      setRating(5);
      setImageFiles([]);
      if (imageInputRef.current) {
        imageInputRef.current.value = "";
      }
      setSuccess(result.message || "Review submitted successfully.");
      onSubmitted?.(result);
    } catch (submitError) {
      const message =
        submitError?.response?.data?.detail ||
        submitError?.message ||
        "Unable to submit your review right now.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit} style={{ display: "grid", gap: "16px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <div
          style={{
            width: "42px",
            height: "42px",
            borderRadius: "14px",
            background: "var(--color-primary-soft)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "var(--color-primary)",
          }}
        >
          <MessageSquarePlus size={20} />
        </div>
        <div>
          <h3 style={{ margin: 0, fontSize: "1.1rem" }}>Write a Review</h3>
          <p style={{ margin: "4px 0 0 0", fontSize: "0.95rem" }}>
            Share a quick impression to help the next person decide faster.
          </p>
        </div>
      </div>

      {!hasToken && (
        <div
          style={{
            display: "flex",
            gap: "10px",
            alignItems: "flex-start",
            padding: "14px 16px",
            borderRadius: "16px",
            background: "#fff7ed",
            border: "1px solid rgba(249, 115, 22, 0.2)",
            color: "#9a3412",
          }}
        >
          <ShieldAlert size={18} style={{ flexShrink: 0, marginTop: "2px" }} />
          <p style={{ margin: 0, color: "inherit" }}>
            Review submission requires an authenticated session. For now, make sure an
            <code style={{ margin: "0 4px", fontWeight: 700 }}>access_token</code>
            is already available in local storage.
          </p>
        </div>
      )}

      <div style={{ display: "grid", gap: "8px" }}>
        <label htmlFor="review-rating" style={{ fontWeight: 600 }}>Rating</label>
        <div style={{ position: "relative" }}>
          <select
            id="review-rating"
            value={rating}
            onChange={(event) => setRating(event.target.value)}
            disabled={submitting}
          >
            {RATING_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value} star{value > 1 ? "s" : ""}
              </option>
            ))}
          </select>
          <Star
            size={16}
            style={{
              position: "absolute",
              right: "14px",
              top: "50%",
              transform: "translateY(-50%)",
              color: "var(--color-accent)",
              pointerEvents: "none",
            }}
            fill="currentColor"
          />
        </div>
      </div>

      <div style={{ display: "grid", gap: "8px" }}>
        <label htmlFor="review-content" style={{ fontWeight: 600 }}>Your review</label>
        <textarea
          id="review-content"
          rows={5}
          placeholder="What stood out to you about this place?"
          value={content}
          onChange={(event) => setContent(event.target.value)}
          disabled={submitting}
          style={{ resize: "vertical", minHeight: "150px" }}
        />
      </div>

      <div style={{ display: "grid", gap: "10px" }}>
        <label htmlFor="review-images" style={{ fontWeight: 600 }}>Review photos</label>
        <label
          htmlFor="review-images"
          className="btn-outline"
          style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            width: "fit-content",
            padding: "10px 14px",
            borderRadius: "14px",
            cursor: submitting ? "not-allowed" : "pointer",
          }}
        >
          <ImagePlus size={18} />
          Select photos
        </label>
        <input
          ref={imageInputRef}
          id="review-images"
          type="file"
          accept="image/png,image/jpeg,image/webp,image/gif"
          multiple
          onChange={handleImageChange}
          disabled={submitting}
          style={{ display: "none" }}
        />
        {imagePreviews.length ? (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
            {imagePreviews.map((previewUrl, index) => (
              <div
                key={previewUrl}
                style={{
                  width: "88px",
                  height: "88px",
                  position: "relative",
                  borderRadius: "12px",
                  overflow: "hidden",
                  background: `url(${previewUrl}) center/cover`,
                  border: "1px solid rgba(15, 23, 42, 0.12)",
                }}
              >
                <button
                  type="button"
                  onClick={() => removeImage(index)}
                  disabled={submitting}
                  aria-label="Remove photo"
                  style={{
                    position: "absolute",
                    right: "6px",
                    top: "6px",
                    width: "26px",
                    height: "26px",
                    borderRadius: "50%",
                    padding: 0,
                    display: "grid",
                    placeItems: "center",
                    background: "rgba(15, 23, 42, 0.72)",
                    color: "#fff",
                    border: 0,
                  }}
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        ) : null}
      </div>

      {error ? (
        <p
          style={{
            margin: 0,
            padding: "12px 14px",
            borderRadius: "14px",
            background: "#fef2f2",
            color: "#b91c1c",
            border: "1px solid rgba(220, 38, 38, 0.15)",
          }}
        >
          {error}
        </p>
      ) : null}

      {success ? (
        <p
          style={{
            margin: 0,
            padding: "12px 14px",
            borderRadius: "14px",
            background: "#ecfdf5",
            color: "#047857",
            border: "1px solid rgba(16, 185, 129, 0.18)",
          }}
        >
          {success}
        </p>
      ) : null}

      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <button
          type="submit"
          className="btn-primary"
          disabled={submitting || !normalizedPlaceId}
          style={{
            padding: "12px 22px",
            borderRadius: "16px",
            fontWeight: 700,
            minWidth: "180px",
          }}
        >
          {submitting ? "Submitting..." : "Submit review"}
        </button>
      </div>
    </form>
  );
}
