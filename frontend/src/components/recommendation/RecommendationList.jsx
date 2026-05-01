import PlaceCard from "../common/PlaceCard";

/**
 * RecommendationList — Danh sách top 10 địa điểm gợi ý.
 *
 * Owner:
 * - TV2: Frontend search/filter/result wiring.
 *
 * Props:
 * - places: array PlaceSummary từ GET /recommendations (tối đa 10 items).
 *   Mỗi item tối thiểu: { id, name, address, latitude, longitude,
 *     primary_type, category, rating, review_count, photo_url,
 *     score, explanation }
 * - loading: boolean — hiện skeleton/spinner khi đang fetch.
 * - error: string | null — hiện error message nếu có.
 * - hasSearched: boolean — phân biệt "chưa search" và "search không có kết quả".
 *
 * Output:
 * - Grid 3 cột của PlaceCard khi có kết quả.
 * - Skeleton loading khi loading=true.
 * - Error state khi error != null.
 * - Empty state tùy theo hasSearched.
 *
 * Note:
 * - score và explanation là optional (TODO TV5/F4). Khi có thì hiện badge,
 *   khi chưa có thì PlaceCard vẫn render bình thường.
 */
export default function RecommendationList({
  places = [],
  loading = false,
  error = null,
  hasSearched = false,
}) {
  // --- Loading state ---
  if (loading) {
    return (
      <div className="grid grid-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  // --- Error state ---
  if (error) {
    return (
      <div
        className="card"
        style={{
          textAlign: "center",
          padding: "40px 24px",
          background: "#fef2f2",
          border: "1px solid #fecaca",
        }}
      >
        <p style={{ fontSize: "2rem", marginBottom: "12px" }}>😕</p>
        <p style={{ fontWeight: 700, color: "#b91c1c", marginBottom: "8px" }}>
          Something went wrong
        </p>
        <p style={{ color: "#991b1b", fontSize: "0.9rem" }}>{error}</p>
      </div>
    );
  }

  // --- Empty state ---
  if (places.length === 0) {
    return (
      <div className="card" style={{ textAlign: "center", padding: "40px 24px" }}>
        <p style={{ fontSize: "2.5rem", marginBottom: "12px" }}>🔍</p>
        <p style={{ fontWeight: 700, color: "var(--color-text)", marginBottom: "8px" }}>
          {hasSearched ? "No places found" : "No suggestions yet"}
        </p>
        <p style={{ color: "var(--color-text-soft)", fontSize: "0.9rem" }}>
          {hasSearched
            ? "Try a different query or adjust your filters."
            : "Search for something or allow GPS to get started."}
        </p>
      </div>
    );
  }

  // --- Results ---
  return (
    <div style={{ display: "grid", gap: "12px" }}>
      {/* Số kết quả */}
      <p style={{ color: "var(--color-text-soft)", fontSize: "0.9rem", fontWeight: 600 }}>
        {places.length} place{places.length > 1 ? "s" : ""} found
      </p>

      <div className="grid grid-3">
        {places.map((place, index) => (
          <div key={place.id} style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {/* Explanation badge từ F4 (TV5) — chỉ hiện khi có */}
            {place.explanation && (
              <div
                style={{
                  padding: "8px 12px",
                  borderRadius: "10px",
                  background: "linear-gradient(135deg, #eff6ff, #f3e8ff)",
                  border: "1px solid #ddd6fe",
                  fontSize: "0.82rem",
                  color: "var(--color-primary)",
                  fontWeight: 600,
                  display: "flex",
                  gap: "6px",
                  alignItems: "flex-start",
                }}
              >
                <span>✨</span>
                <span>{place.explanation}</span>
              </div>
            )}
            <PlaceCard place={place} />
          </div>
        ))}
      </div>
    </div>
  );
}

/** Skeleton card khi đang loading */
function SkeletonCard() {
  return (
    <div
      className="card"
      style={{ padding: 0, overflow: "hidden", height: "320px", display: "flex", flexDirection: "column" }}
    >
      <div
        style={{
          height: "130px",
          background: "linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%)",
          backgroundSize: "200% 100%",
          animation: "shimmer 1.5s infinite",
        }}
      />
      <div style={{ padding: "16px", display: "grid", gap: "12px" }}>
        <div style={{ height: "20px", borderRadius: "6px", background: "#e2e8f0", width: "70%" }} />
        <div style={{ height: "14px", borderRadius: "6px", background: "#e2e8f0", width: "90%" }} />
        <div style={{ height: "14px", borderRadius: "6px", background: "#e2e8f0", width: "50%" }} />
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px", marginTop: "auto" }}>
          {[1, 2, 3].map((i) => (
            <div key={i} style={{ height: "36px", borderRadius: "8px", background: "#e2e8f0" }} />
          ))}
        </div>
      </div>
      <style>{`
        @keyframes shimmer {
          0%   { background-position: -200% 0; }
          100% { background-position:  200% 0; }
        }
      `}</style>
    </div>
  );
}
