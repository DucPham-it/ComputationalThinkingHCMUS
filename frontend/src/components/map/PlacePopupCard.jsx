import { Heart, MapPin, Route, Star, ExternalLink } from "lucide-react";

import { formatRating } from "../../utils/formatter";

export default function PlacePopupCard({
  place,
  onViewPlace,
  onSavePlace,
  onPrimaryAction,
  onCancelSelection,
  primaryActionLabel = "Pick",
  selectionModeLabel,
  cancelActionLabel = "Cancel pin",
}) {
  const canViewPlace = place?._canView !== false;
  const canSavePlace = place?._canSave !== false;

  return (
    <div
      style={{
        width: "250px",
        overflow: "hidden",
        borderRadius: "16px",
        background: "#ffffff",
      }}
    >
      <div
        style={{
          height: "110px",
          background: place.photo_url
            ? `linear-gradient(rgba(15, 23, 42, 0.24), rgba(15, 23, 42, 0.24)), url(${place.photo_url}) center/cover`
            : "linear-gradient(135deg, #dbeafe 0%, #fef3c7 100%)",
          borderRadius: "12px",
        }}
      />

      <div style={{ display: "grid", gap: "10px", padding: "12px" }}>
        <div>
          <h3
            style={{
              margin: "0 0 6px 0",
              fontSize: "15px",
              lineHeight: 1.3,
              color: "#0f172a",
            }}
          >
            {place.name}
          </h3>
          <p style={{ margin: 0, fontSize: "12px", color: "#64748b" }}>{place.address}</p>
        </div>

        {selectionModeLabel ? (
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              width: "fit-content",
              padding: "6px 10px",
              borderRadius: "999px",
              background: "#fff7ed",
              color: "#c2410c",
              fontSize: "11px",
              fontWeight: 700,
            }}
          >
            {selectionModeLabel}
          </div>
        ) : null}

        <div style={{ display: "grid", gap: "6px", fontSize: "12px", color: "#334155" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", fontWeight: 700 }}>
              <Star size={14} color="#f59e0b" fill="#f59e0b" />
              Web {formatRating(place.web_rating)}
            </span>
            <span style={{ color: "#64748b" }}>
              {place.web_review_count ?? place.review_count ?? 0} reviews
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", fontWeight: 600 }}>
              <Star size={13} color="#94a3b8" />
              Google {formatRating(place.google_rating)}
            </span>
            {place.google_review_count ? (
              <span style={{ color: "#64748b" }}>{place.google_review_count} ratings</span>
            ) : null}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#64748b" }}>
            <MapPin size={13} />
            <span>{place.distance_km ?? "N/A"} km by route</span>
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: "8px",
            marginTop: "2px",
          }}
        >
          <button
            className="btn-outline"
            style={{ padding: "8px 10px", borderRadius: "10px", fontWeight: 700 }}
            disabled={!canViewPlace}
            onClick={() => onViewPlace?.(place)}
          >
            <ExternalLink size={14} style={{ marginRight: "4px" }} />
            View
          </button>
          <button
            className="btn-outline"
            style={{ padding: "8px 10px", borderRadius: "10px", fontWeight: 700 }}
            disabled={!canSavePlace}
            onClick={() => onSavePlace?.(place)}
          >
            <Heart size={14} style={{ marginRight: "4px" }} />
            Save
          </button>
          <button
            className="btn-primary"
            style={{ padding: "8px 10px", borderRadius: "10px", fontWeight: 700 }}
            onClick={() => onPrimaryAction?.(place)}
          >
            <Route size={14} style={{ marginRight: "4px" }} />
            {primaryActionLabel}
          </button>
        </div>

        {onCancelSelection ? (
          <button
            className="btn-outline"
            style={{
              padding: "8px 10px",
              borderRadius: "10px",
              fontWeight: 700,
              color: "#b91c1c",
              borderColor: "#fecaca",
            }}
            onClick={() => onCancelSelection(place)}
          >
            {cancelActionLabel}
          </button>
        ) : null}
      </div>
    </div>
  );
}
