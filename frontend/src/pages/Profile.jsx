import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { MapPin, Settings, Share2, User, Users } from "lucide-react";

import Empty from "../components/common/Empty";
import Error from "../components/common/Error";
import LoadingSpinner from "../components/common/LoadingSpinner";
import SocialPostCard from "../components/social/SocialPostCard";
import { useAuth } from "../hooks/useAuth";
import { fetchMySocialProfile } from "../services/socialService";
import ProfileSettings from "./ProfileSettings";

function displayName(profileUser) {
  const fullName = [profileUser?.first_name, profileUser?.last_name].filter(Boolean).join(" ");
  return fullName || profileUser?.user_name || "Traveler";
}

function initialTabFromSearch(search, hasCompletedProfile) {
  const tab = new URLSearchParams(search).get("tab");
  if (!hasCompletedProfile) return "settings";
  return tab === "shared" || tab === "settings" ? tab : "posts";
}

export default function Profile() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, hasCompletedProfile } = useAuth();
  const [profile, setProfile] = useState(null);
  const [activeTab, setActiveTab] = useState(() =>
    initialTabFromSearch(location.search, hasCompletedProfile)
  );
  const [loading, setLoading] = useState(isAuthenticated);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    setActiveTab(initialTabFromSearch(location.search, hasCompletedProfile));
  }, [hasCompletedProfile, location.search]);

  async function loadProfile() {
    if (!isAuthenticated) return;
    try {
      setLoading(true);
      setError("");
      const payload = await fetchMySocialProfile();
      setProfile(payload);
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || "We couldn't load your profile right now.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProfile();
  }, [isAuthenticated]);

  const profileUser = profile?.user || user || {};
  const profileName = displayName(profileUser);
  const profileInitial = profileName.slice(0, 1).toUpperCase();
  const stats = profile?.stats || { post_count: 0, shared_count: 0, visited_count: 0 };

  const visibleItems = useMemo(() => {
    const items = profile?.items || [];
    if (activeTab === "shared") {
      return items.filter((item) => item.timeline_type === "share");
    }
    return items.filter((item) => item.timeline_type !== "share");
  }, [activeTab, profile?.items]);

  function handlePostUpdated(nextPost) {
    setProfile((currentProfile) => {
      if (!currentProfile) return currentProfile;
      const nextItems = currentProfile.items
        .map((item) => {
          if (item.id !== nextPost.id) return item;
          if (item.timeline_type === "share" && !nextPost.viewer_has_shared) {
            return null;
          }
          return {
            ...item,
            ...nextPost,
            timeline_type: item.timeline_type,
            shared_at: item.shared_at,
          };
        })
        .filter(Boolean);
      return { ...currentProfile, items: nextItems };
    });
  }

  function handleSettingsSaved() {
    setActiveTab("posts");
    loadProfile();
  }

  if (!isAuthenticated) {
    return (
      <Empty
        icon={User}
        title="Sign in required"
        message="Sign in before opening your profile."
      />
    );
  }

  if (loading && activeTab !== "settings") {
    return <LoadingSpinner message="Loading your profile..." />;
  }

  if (error && activeTab !== "settings") {
    return <Error message={error} />;
  }

  return (
    <div style={{ display: "grid", gap: "20px" }}>
      <section
        className="card dynamic-card profile-hero-card"
        style={{
          display: "grid",
          gap: "18px",
          padding: "24px",
        }}
      >
        <div style={{ display: "flex", gap: "18px", alignItems: "center", flexWrap: "wrap" }}>
          <div
            style={{
              width: "92px",
              height: "92px",
              borderRadius: "50%",
              background: profileUser.avatar_url
                ? `url(${profileUser.avatar_url}) center/cover`
                : "linear-gradient(135deg, #dbeafe 0%, #fef3c7 100%)",
              border: "1px solid var(--color-border)",
              display: "grid",
              placeItems: "center",
              color: "var(--color-primary)",
              fontSize: "2rem",
              fontWeight: 900,
              flexShrink: 0,
            }}
          >
            {profileUser.avatar_url ? null : profileInitial}
          </div>
          <div style={{ minWidth: 0, flex: 1 }}>
            <h1 style={{ marginBottom: "6px" }}>{profileName}</h1>
            <p style={{ marginBottom: 0, fontWeight: 700 }}>@{profileUser.user_name || user?.user_name}</p>
            {profileUser.address ? (
              <p
                style={{
                  margin: "8px 0 0",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                <MapPin size={16} />
                {profileUser.address}
              </p>
            ) : null}
          </div>
          <Link
            to="/social"
            className="btn-primary"
            style={{ padding: "12px 16px", borderRadius: "14px", fontWeight: 800 }}
          >
            Open Social
          </Link>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
            gap: "12px",
          }}
        >
          {[
            ["Posts", stats.post_count],
            ["Shared", stats.shared_count],
            ["Visited", stats.visited_count],
          ].map(([label, value]) => (
            <div
              key={label}
              className="profile-stat-card"
              style={{
                padding: "14px 16px",
                borderRadius: "16px",
                background: "rgba(255, 255, 255, 0.72)",
                border: "1px solid var(--color-border)",
              }}
            >
              <strong style={{ display: "block", color: "var(--color-text)", fontSize: "1.35rem" }}>
                {value}
              </strong>
              <span style={{ color: "var(--color-text-soft)", fontWeight: 700 }}>{label}</span>
            </div>
          ))}
        </div>
      </section>

      <div className="card" style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <button
          type="button"
          className={activeTab === "posts" ? "btn-primary" : "btn-outline"}
          style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "10px 14px", borderRadius: "12px", fontWeight: 800 }}
          onClick={() => setActiveTab("posts")}
        >
          <Users size={17} />
          Posts
        </button>
        <button
          type="button"
          className={activeTab === "shared" ? "btn-primary" : "btn-outline"}
          style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "10px 14px", borderRadius: "12px", fontWeight: 800 }}
          onClick={() => setActiveTab("shared")}
        >
          <Share2 size={17} />
          Shared
        </button>
        <button
          type="button"
          className={activeTab === "settings" ? "btn-primary" : "btn-outline"}
          style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "10px 14px", borderRadius: "12px", fontWeight: 800 }}
          onClick={() => setActiveTab("settings")}
        >
          <Settings size={17} />
          Settings
        </button>
      </div>

      {activeTab === "settings" ? (
        <ProfileSettings embedded onSaved={handleSettingsSaved} />
      ) : visibleItems.length ? (
        <div style={{ display: "grid", gap: "16px" }}>
          {visibleItems.map((post) => (
            <SocialPostCard
              key={`${post.timeline_type}-${post.id}`}
              post={post}
              onPostUpdated={handlePostUpdated}
            />
          ))}
        </div>
      ) : (
        <Empty
          icon={activeTab === "shared" ? Share2 : Users}
          title={activeTab === "shared" ? "No shared posts yet" : "No posts yet"}
          message={
            activeTab === "shared"
              ? "Shared posts from the social feed will show up here."
              : "Create a post from Social after completing a route."
          }
        />
      )}
    </div>
  );
}
