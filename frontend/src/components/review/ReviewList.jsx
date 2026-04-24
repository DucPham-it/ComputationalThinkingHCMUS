import { MessageSquareText, Star } from "lucide-react";

/**
 * Review/comment list with user avatar display.
 *
 * Owner:
 * - TV7: Media Upload + Review Avatar.
 *
 * File input:
 * - reviews: array of review payloads from backend.
 * - emptyMessage: optional text when there are no reviews.
 *
 * File output:
 * - Review cards with avatar, name, date/place id, rating stars, content, images.
 * - Fallback avatar from Supabase Storage when user_avatar_url is missing/broken.
 */

const SUPABASE_PUBLIC_URL =
  import.meta.env.VITE_SUPABASE_URL || "https://thklzhorgokuvcvnuqtd.supabase.co";
const DEFAULT_AVATAR_URL = `${SUPABASE_PUBLIC_URL}/storage/v1/object/public/avatars/default/default-avatar.jpg`;

function renderStars(rating) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - rating: numeric review rating, expected 0..5.
   *
   * Output:
   * - array of 5 Star icon elements.
   */
  const safeRating = Math.max(0, Math.min(5, Number(rating) || 0));
  return Array.from({ length: 5 }, (_, index) => (
    <Star
      key={`${safeRating}-${index}`}
      size={14}
      fill={index < safeRating ? "currentColor" : "none"}
      style={{ color: index < safeRating ? "var(--color-accent)" : "var(--color-border)" }}
    />
  ));
}

function handleAvatarError(event) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - image error event from avatar img.
   *
   * Output:
   * - swaps broken avatar to DEFAULT_AVATAR_URL.
   * - hides image if the default avatar also fails.
   */
  if (event.currentTarget.src !== DEFAULT_AVATAR_URL) {
    event.currentTarget.src = DEFAULT_AVATAR_URL;
    return;
  }
  event.currentTarget.style.visibility = "hidden";
}

export default function ReviewList({
  reviews = [],
  emptyMessage = "No reviews yet. Be the first one to share your experience.",
}) {
  /**
   * Owner:
   * - TV7.
   *
   * Input:
   * - reviews: each review can contain id, place_id, user_name,
   *   user_avatar_url, reviewed_at, rating, content, image_urls.
   *
   * Output:
   * - JSX review list or empty-state card.
   */
  if (!reviews.length) {
    return (
      <div
        className="card"
        style={{
          display: "grid",
          placeItems: "center",
          textAlign: "center",
          minHeight: "220px",
          gap: "14px",
          background: "linear-gradient(180deg, rgba(255,255,255,0.9), var(--color-bg-soft))",
        }}
      >
        <div
          style={{
            width: "64px",
            height: "64px",
            borderRadius: "20px",
            background: "var(--color-primary-soft)",
            color: "var(--color-primary)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <MessageSquareText size={28} />
        </div>
        <div>
          <h3 style={{ marginBottom: "8px" }}>No reviews yet</h3>
          <p style={{ margin: 0 }}>{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gap: "16px" }}>
      {reviews.map((review) => (
        <article
          key={review.id}
          className="card"
          style={{
            padding: "20px",
            display: "grid",
            gap: "14px",
            background: "rgba(255,255,255,0.88)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: "16px", flexWrap: "wrap" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", minWidth: 0 }}>
              <img
                src={review.user_avatar_url || DEFAULT_AVATAR_URL}
                alt={review.user_name || "Reviewer avatar"}
                onError={handleAvatarError}
                style={{
                  width: "44px",
                  height: "44px",
                  borderRadius: "50%",
                  objectFit: "cover",
                  border: "1px solid var(--color-border)",
                  background: "var(--color-primary-soft)",
                  flexShrink: 0,
                }}
              />
              <div style={{ minWidth: 0 }}>
                <h3 style={{ margin: 0, fontSize: "1rem" }}>
                  {review.user_name || `Review #${review.id}`}
                </h3>
                <p style={{ margin: "4px 0 0 0", fontSize: "0.9rem" }}>
                  {review.reviewed_at || `Place ID: ${review.place_id}`}
                </p>
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
              {renderStars(review.rating)}
              <span style={{ marginLeft: "6px", fontWeight: 700, color: "var(--color-text)" }}>
                {review.rating}/5
              </span>
            </div>
          </div>

          <p style={{ margin: 0, color: "var(--color-text)", lineHeight: 1.7 }}>
            {review.content}
          </p>

          {review.image_urls?.length ? (
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              {review.image_urls.slice(0, 3).map((imageUrl) => (
                <img
                  key={imageUrl}
                  src={imageUrl}
                  alt={review.user_name || "Review image"}
                  style={{
                    width: "92px",
                    height: "92px",
                    objectFit: "cover",
                    borderRadius: "14px",
                    border: "1px solid var(--color-border)",
                  }}
                />
              ))}
            </div>
          ) : null}
        </article>
      ))}
    </div>
  );
}
