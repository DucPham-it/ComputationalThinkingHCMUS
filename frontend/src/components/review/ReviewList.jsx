import { MessageSquareText, Star } from "lucide-react";

function renderStars(rating) {
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

export default function ReviewList({
  reviews = [],
  emptyMessage = "No reviews yet. Be the first one to share your experience.",
}) {
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
            <div>
              <h3 style={{ margin: 0, fontSize: "1rem" }}>
                {review.user_name || `Review #${review.id}`}
              </h3>
              <p style={{ margin: "4px 0 0 0", fontSize: "0.9rem" }}>
                {review.reviewed_at || `Place ID: ${review.place_id}`}
              </p>
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
