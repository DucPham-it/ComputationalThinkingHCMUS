import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import Error from "../components/common/Error";
import LoadingSpinner from "../components/common/LoadingSpinner";
import Section from "../components/common/Section";
import ReviewForm from "../components/review/ReviewForm";
import ReviewList from "../components/review/ReviewList";
import { fetchPlaceDetail } from "../services/placeService";
import { fetchReviews } from "../services/reviewService";

export default function ReviewPage() {
  const navigate = useNavigate();
  const { placeId: routePlaceId } = useParams();
  const [lookupValue, setLookupValue] = useState(routePlaceId || "");
  const [place, setPlace] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const activePlaceId = routePlaceId || "";

  useEffect(() => {
    setLookupValue(activePlaceId);
  }, [activePlaceId]);

  useEffect(() => {
    async function loadReviewData() {
      if (!activePlaceId) {
        setPlace(null);
        setReviews([]);
        setError("");
        return;
      }

      try {
        setLoading(true);
        setError("");

        const [placeResponse, reviewResponse] = await Promise.all([
          fetchPlaceDetail(activePlaceId),
          fetchReviews(activePlaceId),
        ]);

        setPlace(placeResponse);
        setReviews(reviewResponse.items ?? []);
      } catch (loadError) {
        setError("We couldn't load the review data for that place.");
      } finally {
        setLoading(false);
      }
    }

    loadReviewData();
  }, [activePlaceId]);

  function handleLookup(event) {
    event.preventDefault();
    const normalizedId = lookupValue.trim();

    if (!normalizedId) {
      navigate("/reviews");
      return;
    }

    navigate(`/reviews/${normalizedId}`);
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

  return (
    <div style={{ display: "grid", gap: "24px" }}>
      <Section
        title="Review Center"
        subtitle="Look up a place by ID, browse recent reviews, and post your own feedback."
      >
        <form
          className="card"
          onSubmit={handleLookup}
          style={{ display: "grid", gap: "14px" }}
        >
          <label htmlFor="review-place-id" style={{ fontWeight: 700 }}>
            Place ID
          </label>
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            <input
              id="review-place-id"
              value={lookupValue}
              onChange={(event) => setLookupValue(event.target.value)}
              placeholder="Enter a place ID"
              inputMode="numeric"
              style={{ flex: "1 1 240px" }}
            />
            <button
              type="submit"
              className="btn-primary"
              style={{ padding: "12px 20px", borderRadius: "14px", fontWeight: 700 }}
            >
              Load reviews
            </button>
          </div>
        </form>
      </Section>

      {!activePlaceId ? (
        <Section title="Select a Place" subtitle="Use a place ID from the recommendation list or place detail page.">
          <div className="card">
            <p style={{ margin: 0 }}>
              Enter a valid place ID above to read existing reviews and submit a new one.
            </p>
          </div>
        </Section>
      ) : null}

      {loading ? <LoadingSpinner message="Loading review details..." /> : null}
      {!loading && error ? <Error message={error} /> : null}

      {!loading && !error && activePlaceId && place ? (
        <>
          <Section
            title={place.name}
            subtitle={place.address}
          >
            <div className="card" style={{ display: "grid", gap: "12px" }}>
              <p style={{ margin: 0 }}>
                Rating: <strong style={{ color: "var(--color-text)" }}>{place.rating ?? "N/A"}</strong>
              </p>
              <p style={{ margin: 0 }}>
                Total reviews: <strong style={{ color: "var(--color-text)" }}>{place.review_count ?? reviews.length}</strong>
              </p>
            </div>
          </Section>

          <Section title="All Reviews" subtitle="Fresh feedback from people who have already been there.">
            <ReviewList reviews={reviews} />
          </Section>

          <Section title="Add Yours" subtitle="Post a review for this place directly from here.">
            <ReviewForm placeId={activePlaceId} onSubmitted={handleReviewSubmitted} />
          </Section>
        </>
      ) : null}
    </div>
  );
}
