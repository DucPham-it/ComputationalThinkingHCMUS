import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { MapPin, Phone, Star } from "lucide-react";

import LoadingSpinner from "../components/common/LoadingSpinner";
import Error from "../components/common/Error";
import Section from "../components/common/Section";
import ReviewList from "../components/review/ReviewList";
import ReviewForm from "../components/review/ReviewForm";
import { addFavorite } from "../services/favoriteService";
import { fetchPlaceDetail } from "../services/placeService";
import { recordPlacePick } from "../services/mapPickService";
import { fetchReviews } from "../services/reviewService";
import { useApp } from "../hooks/useApp";
import { formatRating } from "../utils/formatter";
import { buildRouteDestinationFromMapPick } from "./MapView";

/**
 * Place detail page.
 *
 * Input:
 * - route param id
 *
 * Output:
 * - detail block with address, description, hours, images, reviews summary
 */
export default function PlaceDetail() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { setSelectedPlace } = useApp();
  const [place, setPlace] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [actionSuccess, setActionSuccess] = useState("");
  const numericPlaceId = Number(id);
  const hasValidPlaceId = Number.isInteger(numericPlaceId) && numericPlaceId > 0;

  useEffect(() => {
    async function fetchData() {
      if (!hasValidPlaceId) {
        setPlace(null);
        setReviews([]);
        setError("This OSM-only point is not available as a database place detail.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");
        setActionError("");
        setActionSuccess("");

        const [placeRes, reviewRes] = await Promise.all([
          fetchPlaceDetail(numericPlaceId),
          fetchReviews(numericPlaceId),
        ]);

        setPlace(placeRes);
        setReviews(reviewRes.items ?? []);
      } catch (err) {
        setError("We couldn't load this place right now.");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [id, hasValidPlaceId, numericPlaceId]);

  async function handlePickPlace() {
    if (!place || !hasValidPlaceId) {
      return;
    }

    let destination;
    try {
      destination = buildRouteDestinationFromMapPick(place);
    } catch (error) {
      setActionError("This place is missing coordinates. Cannot navigate to route.");
      return;
    }

    try {
      setActionError("");
      setActionSuccess("");
      await recordPlacePick(numericPlaceId);
    } catch (err) {
      console.error("Failed to record place pick, proceeding to route anyway", err);
    }

    setSelectedPlace(destination);
    navigate("/route");
  }

  async function handleSavePlace() {
    if (!hasValidPlaceId) {
      return;
    }

    try {
      setActionError("");
      setActionSuccess("");
      await addFavorite(numericPlaceId);
      setActionSuccess("Place saved to your favorites.");
    } catch (err) {
      console.error("Failed to save favorite", err);
      const detail = err?.response?.data?.detail;
      setActionError(detail || "We could not save this place. Please log in and try again.");
    }
  }

  function handleReviewSubmitted(result) {
    if (result?.latest_review) {
      setReviews((currentReviews) => [result.latest_review, ...currentReviews]);
    }

    setPlace((currentPlace) => {
      if (!currentPlace) {
        return currentPlace;
      }

      return {
        ...currentPlace,
        rating: result?.average_rating ?? currentPlace.rating,
        review_count: result?.review_count ?? currentPlace.review_count,
      };
    });
  }

  if (loading) return <LoadingSpinner />;
  if (error) return <Error message={error} />;
  if (!place) return <Error message="Place details are unavailable." />;

  const heroImage = place.images?.[0] || place.photo_url || null;

  return (
    <div style={{ display: "grid", gap: "24px" }}>
      <Section
        title={place.name}
        subtitle={place.address}
        action={
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            <button
              className="btn-primary"
              style={{ padding: "10px 16px", borderRadius: "14px", fontWeight: 700 }}
              onClick={handlePickPlace}
            >
              Pick This Place
            </button>
            <button
              className="btn-outline"
              style={{ padding: "10px 16px", borderRadius: "14px", fontWeight: 700 }}
              onClick={handleSavePlace}
            >
              Save Place
            </button>
          </div>
        }
      >
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          {heroImage ? (
            <img
              src={heroImage}
              alt={place.name}
              style={{ width: "100%", height: "320px", objectFit: "cover", display: "block" }}
            />
          ) : (
            <div
              style={{
                minHeight: "220px",
                display: "grid",
                placeItems: "center",
                background: "linear-gradient(135deg, var(--color-primary-soft), #dbeafe)",
                color: "var(--color-primary)",
                fontWeight: 800,
                letterSpacing: "-0.02em",
              }}
            >
              {place.name}
            </div>
          )}

          <div style={{ padding: "24px", display: "grid", gap: "18px" }}>
            <div style={{ display: "flex", gap: "18px", flexWrap: "wrap" }}>
              <div className="card" style={{ padding: "14px 16px", display: "flex", alignItems: "center", gap: "10px" }}>
                <Star size={18} fill="var(--color-accent)" color="var(--color-accent)" />
                <div>
                  <strong style={{ display: "block" }}>{formatRating(place.rating)}</strong>
                  <span style={{ color: "var(--color-text-soft)", fontSize: "0.9rem" }}>
                    {place.review_count ?? reviews.length} community reviews
                  </span>
                </div>
              </div>

              <div className="card" style={{ padding: "14px 16px", display: "flex", alignItems: "center", gap: "10px" }}>
                <MapPin size={18} color="var(--color-primary)" />
                <div>
                  <strong style={{ display: "block" }}>{place.primary_type || "Place"}</strong>
                  <span style={{ color: "var(--color-text-soft)", fontSize: "0.9rem" }}>
                    {place.open_now == null ? "Open status unavailable" : place.open_now ? "Open now" : "Closed now"}
                  </span>
                </div>
              </div>

              {place.contact_phone ? (
                <div className="card" style={{ padding: "14px 16px", display: "flex", alignItems: "center", gap: "10px" }}>
                  <Phone size={18} color="var(--color-primary)" />
                  <div>
                    <strong style={{ display: "block" }}>Contact</strong>
                    <span style={{ color: "var(--color-text-soft)", fontSize: "0.9rem" }}>
                      {place.contact_phone}
                    </span>
                  </div>
                </div>
              ) : null}
            </div>

            <p style={{ margin: 0, color: "var(--color-text)", lineHeight: 1.8 }}>
              {place.description || "No detailed description is available for this place yet."}
            </p>

            {actionError ? (
              <p
                style={{
                  margin: 0,
                  padding: "12px 14px",
                  borderRadius: "14px",
                  background: "#fef2f2",
                  color: "#b91c1c",
                  border: "1px solid rgba(220, 38, 38, 0.15)",
                  fontWeight: 600,
                }}
              >
                {actionError}
              </p>
            ) : null}

            {actionSuccess ? (
              <p
                style={{
                  margin: 0,
                  padding: "12px 14px",
                  borderRadius: "14px",
                  background: "#ecfdf5",
                  color: "#047857",
                  border: "1px solid rgba(16, 185, 129, 0.18)",
                  fontWeight: 600,
                }}
              >
                {actionSuccess}
              </p>
            ) : null}
          </div>
        </div>
      </Section>

      <Section
        title="Reviews"
        subtitle="Reviews are loaded from the local database, including imported source reviews and new community feedback."
      >
        <ReviewList reviews={reviews} />
      </Section>

      <Section
        title="Write Your Review"
        subtitle="Your experience helps improve the recommendation quality for the next search."
      >
        <ReviewForm placeId={numericPlaceId} onSubmitted={handleReviewSubmitted} />
      </Section>
    </div>
  );
}
