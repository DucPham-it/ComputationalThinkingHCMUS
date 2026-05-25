import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Heart, MapPin, Route, Trash2 } from "lucide-react";

import LoadingSpinner from "../components/common/LoadingSpinner";
import Error from "../components/common/Error";
import Empty from "../components/common/Empty";
import { fetchFavorites, removeFavorite } from "../services/favoriteService";
import { recordPlacePick } from "../services/mapPickService";
import { useApp } from "../hooks/useApp";
import { useAuth } from "../hooks/useAuth";

export default function Favorites() {
  const navigate = useNavigate();
  const { setSelectedPlace } = useApp();
  const { isAuthenticated } = useAuth();
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(isAuthenticated);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      setPlaces([]);
      setLoading(false);
      setError("");
      return;
    }

    async function loadFavorites() {
      try {
        setLoading(true);
        setError("");
        const data = await fetchFavorites();
        setPlaces(data.items ?? []);
      } catch (err) {
        console.error(err);
        setError("We couldn't load your saved places right now.");
      } finally {
        setLoading(false);
      }
    }

    loadFavorites();
  }, [isAuthenticated]);

  async function handleRemove(placeId) {
    try {
      await removeFavorite(placeId);
      setPlaces((currentPlaces) => currentPlaces.filter((place) => place.id !== placeId));
    } catch (err) {
      console.error(err);
      setError("We couldn't update your saved places right now.");
    }
  }

  function handleView(placeId) {
    navigate(`/places/${placeId}`);
  }

  function handlePick(place) {
    recordPlacePick(place.id).catch((err) => {
      console.error("Failed to record place pick", err);
    });
    setSelectedPlace(place);
    navigate("/route");
  }

  if (loading) {
    return <LoadingSpinner message="Loading your saved places..." />;
  }

  if (!isAuthenticated) {
    return (
      <Empty
        icon={Heart}
        title="Sign in required"
        message="Sign in before opening your saved places."
      />
    );
  }

  if (error) {
    return <Error message={error} />;
  }

  if (!places.length) {
    return (
      <Empty
        icon={Heart}
        title="No saved places yet"
        message="Save a place from Suggestion, Map, or the place detail page to keep it here."
      />
    );
  }

  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <div className="card dynamic-card saved-hero-card" style={{ display: "grid", gap: "8px" }}>
        <h1 style={{ marginBottom: 0 }}>Saved</h1>
        <p style={{ marginBottom: 0 }}>
          These are the places you saved for quick access later.
        </p>
      </div>

      <div className="grid grid-3">
        {places.map((place) => (
          <div
            key={place.id}
            className="card dynamic-card saved-place-card"
            style={{
              padding: 0,
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              background: "rgba(255, 255, 255, 0.96)",
            }}
          >
            <div
              style={{
                height: "140px",
                background: place.photo_url
                  ? `linear-gradient(rgba(15, 23, 42, 0.34), rgba(15, 23, 42, 0.18)), url(${place.photo_url}) center/cover`
                  : "linear-gradient(135deg, #bfdbfe 0%, #99f6e4 55%, #fde68a 100%)",
              }}
            />
            <div style={{ padding: "18px", display: "grid", gap: "12px", flex: 1 }}>
              <div>
                <h3 style={{ marginBottom: "8px", color: "var(--color-text)", fontWeight: 900 }}>
                  {place.name}
                </h3>
                <p style={{ marginBottom: 0, color: "var(--color-text-soft)", fontWeight: 650 }}>
                  {place.address}
                </p>
              </div>

              <div
                style={{
                  display: "flex",
                  gap: "14px",
                  flexWrap: "wrap",
                  color: "var(--color-text-soft)",
                  fontWeight: 700,
                }}
              >
                <span>Rating: {place.rating ?? "N/A"}</span>
                <span>Reviews: {place.review_count ?? 0}</span>
                <span style={{ textTransform: "capitalize" }}>{place.primary_type ?? "place"}</span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px", marginTop: "auto" }}>
                <button
                  className="btn-outline"
                  style={{ padding: "10px 12px", borderRadius: "12px", fontWeight: 700 }}
                  onClick={() => handleView(place.id)}
                >
                  View
                </button>
                <button
                  className="btn-primary"
                  style={{ padding: "10px 12px", borderRadius: "12px", fontWeight: 700 }}
                  onClick={() => handlePick(place)}
                >
                  <Route size={16} style={{ marginRight: "6px" }} />
                  Pick
                </button>
                <button
                  className="btn-outline"
                  style={{ padding: "10px 12px", borderRadius: "12px", fontWeight: 700, color: "#b91c1c" }}
                  onClick={() => handleRemove(place.id)}
                >
                  <Trash2 size={16} style={{ marginRight: "6px" }} />
                  Remove
                </button>
              </div>
              {place.latitude != null && place.longitude != null ? (
                <div
                  style={{
                    display: "flex",
                    gap: "8px",
                    color: "var(--color-text-soft)",
                    fontSize: "0.9rem",
                    fontWeight: 700,
                  }}
                >
                  <MapPin size={16} />
                  <span>
                    {place.latitude.toFixed(5)}, {place.longitude.toFixed(5)}
                  </span>
                </div>
              ) : null}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
