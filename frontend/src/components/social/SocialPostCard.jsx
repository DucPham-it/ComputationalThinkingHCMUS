import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Heart,
  MessageCircle,
  Pencil,
  Save,
  Share2,
  Star,
  X,
} from "lucide-react";

import {
  addSocialComment,
  likeSocialPost,
  shareSocialPost,
  unlikeSocialPost,
  unshareSocialPost,
  updateSocialPost,
} from "../../services/socialService";

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function avatarFallback(name) {
  return String(name || "U").trim().slice(0, 1).toUpperCase();
}

export default function SocialPostCard({ post, onPostUpdated }) {
  const [currentPost, setCurrentPost] = useState(post);
  const [busyAction, setBusyAction] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(post.content || "");
  const [editRating, setEditRating] = useState(post.rating || 5);
  const [commentText, setCommentText] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    setCurrentPost(post);
    setEditContent(post.content || "");
    setEditRating(post.rating || 5);
  }, [post]);

  function applyUpdatedPost(nextPost) {
    setCurrentPost(nextPost);
    onPostUpdated?.(nextPost);
  }

  async function runAction(actionName, action) {
    try {
      setBusyAction(actionName);
      setError("");
      const nextPost = await action();
      applyUpdatedPost(nextPost);
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || "This action could not be completed.");
    } finally {
      setBusyAction("");
    }
  }

  async function handleLike() {
    await runAction("like", () =>
      currentPost.viewer_has_liked
        ? unlikeSocialPost(currentPost.id)
        : likeSocialPost(currentPost.id)
    );
  }

  async function handleShare() {
    await runAction("share", () =>
      currentPost.viewer_has_shared
        ? unshareSocialPost(currentPost.id)
        : shareSocialPost(currentPost.id)
    );
  }

  async function handleCommentSubmit(event) {
    event.preventDefault();
    const content = commentText.trim();
    if (!content) return;
    await runAction("comment", () => addSocialComment(currentPost.id, { content }));
    setCommentText("");
  }

  async function handleEditSubmit(event) {
    event.preventDefault();
    await runAction("edit", () =>
      updateSocialPost(currentPost.id, {
        content: editContent.trim(),
        rating: Number(editRating),
      })
    );
    setIsEditing(false);
  }

  const authorName = currentPost.user_name || "Traveler";
  const avatarUrl = currentPost.user_avatar_url;
  const timelineLabel =
    currentPost.timeline_type === "share"
      ? `Shared ${formatDate(currentPost.shared_at)}`
      : formatDate(currentPost.created_at);

  return (
    <article className="card dynamic-card social-post-card" style={{ display: "grid", gap: "16px" }}>
      <header style={{ display: "flex", gap: "12px", alignItems: "center" }}>
        <div
          style={{
            width: "48px",
            height: "48px",
            borderRadius: "50%",
            background: avatarUrl
              ? `url(${avatarUrl}) center/cover`
              : "linear-gradient(135deg, #dbeafe 0%, #fef3c7 100%)",
            border: "1px solid var(--color-border)",
            display: "grid",
            placeItems: "center",
            color: "var(--color-primary)",
            fontWeight: 900,
            flexShrink: 0,
          }}
        >
          {avatarUrl ? null : avatarFallback(authorName)}
        </div>
        <div style={{ minWidth: 0, flex: 1 }}>
          <strong style={{ display: "block", color: "var(--color-text)" }}>{authorName}</strong>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              flexWrap: "wrap",
              color: "var(--color-text-soft)",
              fontSize: "0.9rem",
            }}
          >
            <Link to={`/places/${currentPost.place_id}`} style={{ color: "var(--color-primary)", fontWeight: 700 }}>
              {currentPost.place_name || "Place"}
            </Link>
            <span>{timelineLabel}</span>
          </div>
        </div>
        {currentPost.timeline_type === "share" ? (
          <span
            style={{
              padding: "6px 10px",
              borderRadius: "999px",
              background: "var(--color-primary-soft)",
              color: "var(--color-primary-dark)",
              fontWeight: 800,
              fontSize: "0.82rem",
            }}
          >
            Shared
          </span>
        ) : null}
      </header>

      {currentPost.place_photo_url ? (
        <Link
          className="social-post-photo"
          to={`/places/${currentPost.place_id}`}
          style={{
            display: "block",
            minHeight: "220px",
            borderRadius: "18px",
            background: `linear-gradient(rgba(15, 23, 42, 0.18), rgba(15, 23, 42, 0.18)), url(${currentPost.place_photo_url}) center/cover`,
          }}
          aria-label={currentPost.place_name || "Open place"}
        />
      ) : null}

      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "8px",
          width: "fit-content",
          padding: "8px 12px",
          borderRadius: "999px",
          background: "rgba(245, 158, 11, 0.12)",
          color: "#92400e",
          fontWeight: 900,
        }}
      >
        <Star size={17} fill="var(--color-accent)" color="var(--color-accent)" />
        {currentPost.rating}/5
      </div>

      {isEditing ? (
        <form onSubmit={handleEditSubmit} style={{ display: "grid", gap: "12px" }}>
          <textarea
            rows={4}
            value={editContent}
            onChange={(event) => setEditContent(event.target.value)}
            required
          />
          <select
            value={editRating}
            onChange={(event) => setEditRating(event.target.value)}
            aria-label="Post rating"
          >
            {[5, 4, 3, 2, 1].map((rating) => (
              <option key={rating} value={rating}>
                {rating}/5
              </option>
            ))}
          </select>
          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            <button
              type="submit"
              className="btn-primary"
              style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "10px 14px", borderRadius: "12px", fontWeight: 800 }}
              disabled={busyAction === "edit"}
            >
              <Save size={17} />
              Save
            </button>
            <button
              type="button"
              className="btn-outline"
              style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "10px 14px", borderRadius: "12px", fontWeight: 800 }}
              onClick={() => {
                setIsEditing(false);
                setEditContent(currentPost.content || "");
                setEditRating(currentPost.rating || 5);
              }}
            >
              <X size={17} />
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <p style={{ margin: 0, color: "var(--color-text)", lineHeight: 1.75, whiteSpace: "pre-wrap" }}>
          {currentPost.content}
        </p>
      )}

      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <button
          type="button"
          className={currentPost.viewer_has_liked ? "btn-primary" : "btn-outline"}
          style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "10px 14px", borderRadius: "12px", fontWeight: 800 }}
          onClick={handleLike}
          disabled={busyAction === "like"}
          title={currentPost.viewer_has_liked ? "Unlike this post" : "Like this post"}
        >
          <Heart size={17} fill={currentPost.viewer_has_liked ? "currentColor" : "none"} />
          {currentPost.like_count}
        </button>
        <button
          type="button"
          className={currentPost.viewer_has_shared ? "btn-primary" : "btn-outline"}
          style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "10px 14px", borderRadius: "12px", fontWeight: 800 }}
          onClick={handleShare}
          disabled={busyAction === "share"}
          title={currentPost.viewer_has_shared ? "Remove shared post from profile" : "Share to profile"}
        >
          <Share2 size={17} />
          {currentPost.share_count}
        </button>
        {currentPost.is_owner ? (
          <button
            type="button"
            className="btn-outline"
            style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "10px 14px", borderRadius: "12px", fontWeight: 800 }}
            onClick={() => setIsEditing(true)}
          >
            <Pencil size={17} />
            Edit
          </button>
        ) : null}
      </div>

      <div style={{ display: "grid", gap: "10px", borderTop: "1px solid var(--color-border)", paddingTop: "14px" }}>
        <strong style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--color-text)" }}>
          <MessageCircle size={18} />
          Comments {currentPost.comment_count}
        </strong>

        {currentPost.comments?.length ? (
          <div style={{ display: "grid", gap: "10px" }}>
            {currentPost.comments.map((comment) => (
              <div
                key={comment.id}
                style={{
                  padding: "10px 12px",
                  borderRadius: "14px",
                  background: "rgba(255, 255, 255, 0.72)",
                  border: "1px solid var(--color-border)",
                }}
              >
                <strong style={{ display: "block", color: "var(--color-text)", marginBottom: "4px" }}>
                  {comment.user_name || "Traveler"}
                </strong>
                <p style={{ margin: 0, color: "var(--color-text)" }}>{comment.content}</p>
              </div>
            ))}
          </div>
        ) : null}

        <form onSubmit={handleCommentSubmit} style={{ display: "flex", gap: "10px" }}>
          <input
            value={commentText}
            onChange={(event) => setCommentText(event.target.value)}
            placeholder="Write a comment"
            aria-label="Write a comment"
          />
          <button
            type="submit"
            className="btn-primary"
            style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", minWidth: "48px", padding: "0 14px", borderRadius: "14px" }}
            disabled={busyAction === "comment" || !commentText.trim()}
            title="Post comment"
          >
            <MessageCircle size={18} />
          </button>
        </form>
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
            fontWeight: 700,
          }}
        >
          {error}
        </p>
      ) : null}
    </article>
  );
}
