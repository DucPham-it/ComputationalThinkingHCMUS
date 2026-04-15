import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { MapPin, Phone, Star } from "lucide-react";

import LoadingSpinner from "../components/common/LoadingSpinner";
import Error from "../components/common/Error";
import Section from "../components/common/Section";
import ReviewList from "../components/review/ReviewList";
import ReviewForm from "../components/review/ReviewForm";
import { fetchPlaceDetail } from "../services/placeService";
import { fetchReviews } from "../services/reviewService";

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
  const { id } = useParams();
  const [place, setPlace] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError("");

        const [placeRes, reviewRes] = await Promise.all([
          fetchPlaceDetail(id),
          fetchReviews(id),
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
  }, [id]);

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
          <Link
            to={`/reviews/${id}`}
            className="btn-outline"
            style={{ padding: "10px 16px", borderRadius: "14px", fontWeight: 700 }}
          >
            Open review page
          </Link>
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
                  <strong style={{ display: "block" }}>{place.rating ?? "N/A"}</strong>
                  <span style={{ color: "var(--color-text-soft)", fontSize: "0.9rem" }}>
                    {place.review_count ?? reviews.length} reviews
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
          </div>
        </div>
      </Section>

      <Section
        title="Reviews"
        subtitle="Read what other visitors thought before you decide to go."
      >
        <ReviewList reviews={reviews} />
      </Section>

      <Section
        title="Write Your Review"
        subtitle="Your experience helps improve the recommendation quality for the next search."
      >
        <ReviewForm placeId={id} onSubmitted={handleReviewSubmitted} />
      </Section>
    </div>
  );
}
