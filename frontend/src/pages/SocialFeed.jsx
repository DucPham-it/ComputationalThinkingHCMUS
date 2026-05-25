import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { CheckCircle, MapPin, Plus, Search, Send, Users, X } from "lucide-react";

import Empty from "../components/common/Empty";
import Error from "../components/common/Error";
import LoadingSpinner from "../components/common/LoadingSpinner";
import SocialPostCard from "../components/social/SocialPostCard";
import { useAuth } from "../hooks/useAuth";
import {
  createSocialPost,
  fetchSocialFeed,
  fetchVisitedPlaces,
} from "../services/socialService";

function formatVisitedLabel(visitedPlace) {
  const date = visitedPlace.visited_at ? new Date(visitedPlace.visited_at) : null;
  const dateLabel =
    date && !Number.isNaN(date.getTime())
      ? new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(date)
      : "recently";
  return `${visitedPlace.place_name} - ${dateLabel}`;
}

function normalizeSearchText(value) {
  return String(value || "")
    .trim()
    .toLowerCase();
}

export default function SocialFeed() {
  const { isAuthenticated, hasCompletedProfile } = useAuth();
  const [posts, setPosts] = useState([]);
  const [visitedPlaces, setVisitedPlaces] = useState([]);
  const [selectedVisitedPlaceId, setSelectedVisitedPlaceId] = useState("");
  const [visitedSearch, setVisitedSearch] = useState("");
  const [feedSearch, setFeedSearch] = useState("");
  const [content, setContent] = useState("");
  const [rating, setRating] = useState(5);
  const [isComposerOpen, setIsComposerOpen] = useState(false);
  const [loading, setLoading] = useState(isAuthenticated && hasCompletedProfile);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");

  useEffect(() => {
    if (!isAuthenticated || !hasCompletedProfile) {
      setLoading(false);
      setPosts([]);
      setVisitedPlaces([]);
      return;
    }

    async function loadSocialData() {
      try {
        setLoading(true);
        setError("");
        const [feedPayload, visitedPayload] = await Promise.all([
          fetchSocialFeed(),
          fetchVisitedPlaces(),
        ]);
        const nextVisitedPlaces = visitedPayload || [];
        setPosts(feedPayload.items || []);
        setVisitedPlaces(nextVisitedPlaces);
        setSelectedVisitedPlaceId((currentValue) => currentValue || String(nextVisitedPlaces[0]?.id || ""));
      } catch (requestError) {
        setError(
          requestError?.response?.data?.detail || "We couldn't load the social feed right now."
        );
      } finally {
        setLoading(false);
      }
    }

    loadSocialData();
  }, [hasCompletedProfile, isAuthenticated]);

  const selectedVisitedPlace = useMemo(
    () =>
      visitedPlaces.find((visitedPlace) => String(visitedPlace.id) === String(selectedVisitedPlaceId)),
    [selectedVisitedPlaceId, visitedPlaces]
  );

  const filteredVisitedPlaces = useMemo(() => {
    const keyword = normalizeSearchText(visitedSearch);
    if (!keyword) {
      return visitedPlaces;
    }

    return visitedPlaces.filter((visitedPlace) => {
      const searchableText = normalizeSearchText(
        [
          visitedPlace.place_name,
          visitedPlace.place_address,
          visitedPlace.route_destination,
          visitedPlace.distance_text,
        ].filter(Boolean).join(" ")
      );
      return searchableText.includes(keyword);
    });
  }, [visitedPlaces, visitedSearch]);

  const filteredPosts = useMemo(() => {
    const keyword = normalizeSearchText(feedSearch);
    if (!keyword) {
      return posts;
    }

    return posts.filter((post) => {
      const searchableText = normalizeSearchText(
        [
          post.content,
          post.user_name,
          post.place_name,
          post.place_address,
          post.timeline_type === "share" ? "shared" : "post",
          ...(post.comments || []).map((comment) => comment.content),
        ].filter(Boolean).join(" ")
      );
      return searchableText.includes(keyword);
    });
  }, [feedSearch, posts]);

  function handlePostUpdated(nextPost) {
    setPosts((currentPosts) =>
      currentPosts.map((post) => (post.id === nextPost.id ? { ...post, ...nextPost } : post))
    );
  }

  function openComposer() {
    setFormError("");
    setIsComposerOpen(true);
  }

  function closeComposer() {
    setFormError("");
    setIsComposerOpen(false);
  }

  async function handleCreatePost(event) {
    event.preventDefault();
    const trimmedContent = content.trim();
    if (!selectedVisitedPlaceId) {
      setFormError("Mark a place as visited before creating a post.");
      return;
    }
    if (!trimmedContent) {
      setFormError("Write something about this place before posting.");
      return;
    }

    try {
      setSubmitting(true);
      setFormError("");
      const newPost = await createSocialPost({
        visited_place_id: Number(selectedVisitedPlaceId),
        content: trimmedContent,
        rating: Number(rating),
      });
      setPosts((currentPosts) => [newPost, ...currentPosts]);
      setContent("");
      setRating(5);
      setIsComposerOpen(false);
    } catch (requestError) {
      setFormError(
        requestError?.response?.data?.detail || "We couldn't publish this post right now."
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (!isAuthenticated) {
    return (
      <Empty
        icon={Users}
        title="Sign in required"
        message="Sign in before opening the social feed."
      />
    );
  }

  if (!hasCompletedProfile) {
    return (
      <div className="card" style={{ display: "grid", gap: "12px", marginTop: "24px" }}>
        <h1 style={{ marginBottom: 0 }}>Complete Profile</h1>
        <p style={{ marginBottom: 0 }}>
          Your social profile needs the basic profile fields first.
        </p>
        <Link
          to="/profile?tab=settings"
          className="btn-primary"
          style={{ width: "fit-content", padding: "12px 16px", borderRadius: "14px", fontWeight: 800 }}
        >
          Open Settings
        </Link>
      </div>
    );
  }

  if (loading) {
    return <LoadingSpinner message="Loading social feed..." />;
  }

  if (error) {
    return <Error message={error} />;
  }

  return (
    <div style={{ display: "grid", gap: "20px" }}>
      <div
        className="card"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "16px",
          flexWrap: "wrap",
        }}
      >
        <div style={{ display: "grid", gap: "8px" }}>
          <h1 style={{ marginBottom: 0 }}>Social</h1>
          <p style={{ marginBottom: 0 }}>
            Share reviews from places you have marked as visited.
          </p>
        </div>
        <button
          type="button"
          className="btn-primary"
          style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            padding: "12px 16px",
            borderRadius: "14px",
            fontWeight: 800,
          }}
          onClick={openComposer}
        >
          <Plus size={18} />
          Create Post
        </button>
      </div>

      {isComposerOpen ? (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Create post"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 2000,
            display: "grid",
            placeItems: "center",
            padding: "20px",
            background: "rgba(15, 23, 42, 0.42)",
            backdropFilter: "blur(10px)",
          }}
          onClick={closeComposer}
        >
          <form
            className="card"
            onSubmit={handleCreatePost}
            style={{
              width: "min(100%, 760px)",
              maxHeight: "min(90vh, 780px)",
              overflowY: "auto",
              display: "grid",
              gap: "14px",
              background: "rgba(255, 255, 255, 0.96)",
            }}
            onClick={(event) => event.stopPropagation()}
          >
        <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
          <CheckCircle size={20} color="var(--color-primary)" />
          <strong style={{ color: "var(--color-text)" }}>Create Post</strong>
          <button
            type="button"
            className="btn-outline"
            style={{
              marginLeft: "auto",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: "38px",
              height: "38px",
              borderRadius: "12px",
            }}
            onClick={closeComposer}
            title="Close"
          >
            <X size={18} />
          </button>
        </div>

        {visitedPlaces.length ? (
          <>
            <div style={{ display: "grid", gap: "10px" }}>
              <label
                style={{
                  display: "grid",
                  gap: "8px",
                  color: "var(--color-text)",
                  fontWeight: 800,
                }}
              >
                Visited Places
                <span
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    padding: "0 14px",
                    borderRadius: "16px",
                    border: "1px solid var(--color-border)",
                    background: "rgba(255, 255, 255, 0.9)",
                  }}
                >
                  <Search size={18} color="var(--color-text-soft)" />
                  <input
                    value={visitedSearch}
                    onChange={(event) => setVisitedSearch(event.target.value)}
                    placeholder="Search visited places"
                    aria-label="Search visited places"
                    style={{
                      border: "none",
                      background: "transparent",
                      boxShadow: "none",
                      paddingLeft: 0,
                    }}
                  />
                </span>
              </label>

              <div
                role="listbox"
                aria-label="Choose a visited place"
                style={{
                  maxHeight: "260px",
                  overflowY: "auto",
                  display: "grid",
                  gap: "8px",
                  padding: "4px",
                }}
              >
                {filteredVisitedPlaces.length ? (
                  filteredVisitedPlaces.map((visitedPlace) => {
                    const active = String(visitedPlace.id) === String(selectedVisitedPlaceId);
                    return (
                      <button
                        key={visitedPlace.id}
                        type="button"
                        role="option"
                        aria-selected={active}
                        onClick={() => setSelectedVisitedPlaceId(String(visitedPlace.id))}
                        style={{
                          display: "grid",
                          gap: "6px",
                          width: "100%",
                          padding: "12px 14px",
                          borderRadius: "14px",
                          border: active
                            ? "1.5px solid var(--color-primary)"
                            : "1px solid var(--color-border)",
                          background: active
                            ? "var(--color-primary-soft)"
                            : "rgba(255, 255, 255, 0.72)",
                          color: "var(--color-text)",
                          textAlign: "left",
                        }}
                      >
                        <span
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "8px",
                            fontWeight: 900,
                          }}
                        >
                          <MapPin size={16} color="var(--color-primary)" />
                          {formatVisitedLabel(visitedPlace)}
                        </span>
                        <span
                          style={{
                            color: "var(--color-text-soft)",
                            fontSize: "0.9rem",
                            lineHeight: 1.45,
                          }}
                        >
                          {visitedPlace.place_address}
                        </span>
                      </button>
                    );
                  })
                ) : (
                  <div
                    style={{
                      padding: "14px",
                      borderRadius: "14px",
                      background: "rgba(255, 255, 255, 0.72)",
                      border: "1px solid var(--color-border)",
                      color: "var(--color-text-soft)",
                      fontWeight: 700,
                    }}
                  >
                    No visited places match this search.
                  </div>
                )}
              </div>
            </div>

            {selectedVisitedPlace ? (
              <div
                style={{
                  padding: "12px 14px",
                  borderRadius: "14px",
                  background: "rgba(255, 255, 255, 0.72)",
                  border: "1px solid var(--color-border)",
                  color: "var(--color-text-soft)",
                  fontWeight: 700,
                }}
              >
                {selectedVisitedPlace.distance_text
                  ? `${selectedVisitedPlace.distance_text} to ${selectedVisitedPlace.place_name}`
                  : `${selectedVisitedPlace.place_name} is marked as visited`}
              </div>
            ) : null}

            <textarea
              rows={4}
              value={content}
              onChange={(event) => setContent(event.target.value)}
              placeholder="How was this place?"
              required
            />

            <div style={{ display: "grid", gap: "8px", maxWidth: "220px" }}>
              <strong style={{ color: "var(--color-text)" }}>Rating</strong>
              <select
                value={rating}
                onChange={(event) => setRating(event.target.value)}
                aria-label="Rating"
              >
                {[5, 4, 3, 2, 1].map((value) => (
                  <option key={value} value={value}>
                    {value}/5
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              className="btn-primary"
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                width: "fit-content",
                padding: "12px 16px",
                borderRadius: "14px",
                fontWeight: 800,
              }}
              disabled={submitting}
            >
              <Send size={18} />
              {submitting ? "Posting..." : "Post"}
            </button>
          </>
        ) : (
          <div style={{ display: "grid", gap: "12px" }}>
            <p style={{ marginBottom: 0 }}>
              Your visited place list is empty. Only places already marked as visited will appear here.
            </p>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                width: "fit-content",
                padding: "12px 16px",
                borderRadius: "14px",
                background: "rgba(255, 255, 255, 0.72)",
                border: "1px solid var(--color-border)",
                color: "var(--color-text-soft)",
                fontWeight: 800,
              }}
            >
              <MapPin size={18} />
              No visited places yet
            </div>
          </div>
        )}

        {formError ? (
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
            {formError}
          </p>
        ) : null}
          </form>
        </div>
      ) : null}

      {posts.length ? (
        <>
          <div className="card" style={{ display: "grid", gap: "10px" }}>
            <label
              style={{
                display: "grid",
                gap: "8px",
                color: "var(--color-text)",
                fontWeight: 800,
              }}
            >
              Search Feed
              <span
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  padding: "0 14px",
                  borderRadius: "16px",
                  border: "1px solid var(--color-border)",
                  background: "rgba(255, 255, 255, 0.9)",
                }}
              >
                <Search size={18} color="var(--color-text-soft)" />
                <input
                  value={feedSearch}
                  onChange={(event) => setFeedSearch(event.target.value)}
                  placeholder="Search posts, authors, places"
                  aria-label="Search posts, authors, places"
                  style={{
                    border: "none",
                    background: "transparent",
                    boxShadow: "none",
                    paddingLeft: 0,
                  }}
                />
              </span>
            </label>
            <span style={{ color: "var(--color-text-soft)", fontWeight: 700 }}>
              {filteredPosts.length} of {posts.length} posts
            </span>
          </div>

          {filteredPosts.length ? (
            <div style={{ display: "grid", gap: "16px" }}>
              {filteredPosts.map((post) => (
                <SocialPostCard key={post.id} post={post} onPostUpdated={handlePostUpdated} />
              ))}
            </div>
          ) : (
            <Empty
              icon={Search}
              title="No matching posts"
              message="Try another post, author, or place keyword."
            />
          )}
        </>
      ) : (
        <Empty
          icon={Users}
          title="No posts yet"
          message="The first travel story will appear here once someone posts from a visited place."
        />
      )}
    </div>
  );
}
