import { MessageSquarePlus, ShieldAlert, Star } from "lucide-react";
import { useMemo, useState } from "react";

import { createReview } from "../../services/reviewService";

const RATING_OPTIONS = [5, 4, 3, 2, 1];

export default function ReviewForm({ placeId, onSubmitted }) {
  const [rating, setRating] = useState(5);
  const [content, setContent] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const normalizedPlaceId = useMemo(() => {
    const numericId = Number(placeId);
    return Number.isInteger(numericId) && numericId > 0 ? numericId : null;
  }, [placeId]);

  const hasToken = typeof window !== "undefined" && Boolean(window.localStorage.getItem("access_token"));

  async function handleSubmit(event) {
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

      const result = await createReview({
        place_id: normalizedPlaceId,
        content: content.trim(),
        rating: Number(rating),
        image_urls: [],
      });

      setContent("");
      setRating(5);
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
