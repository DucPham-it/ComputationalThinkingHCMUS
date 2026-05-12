import PlaceCard from "../common/PlaceCard";

function getExplanationText(explanation) {
  if (!explanation) {
    return "";
  }

  if (typeof explanation === "string") {
    return explanation;
  }

  return explanation.summary || "";
}

/**
 * Input props:
 * - places: recommendation result array
 *
 * Output:
 * - list/grid of place cards
 */
export default function RecommendationList({ places = [] }) {
  return (
    <div className="grid grid-3">
      {places.map((place) => {
        const explanationText = getExplanationText(place.explanation);

        return (
          <div key={place.id} style={{ display: "grid", gap: "8px" }}>
            {explanationText ? (
              <div
                style={{
                  padding: "8px 12px",
                  borderRadius: "8px",
                  background: "var(--color-primary-soft)",
                  color: "var(--color-primary)",
                  fontSize: "0.85rem",
                  fontWeight: 600,
                }}
              >
                {explanationText}
              </div>
            ) : null}
            <PlaceCard place={place} />
          </div>
        );
      })}
    </div>
  );
}
