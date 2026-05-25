import { Heart, MapPin, Route, Star, ExternalLink, MessageSquarePlus } from "lucide-react";

import { formatRating } from "../../utils/formatter";

function hasDatabasePlaceId(place) {
  const numericId = Number(place?.id);
  return Number.isInteger(numericId) && numericId > 0;
}

export default function PlacePopupCard({
  place,
  onViewPlace,
  onSavePlace,
  onSuggestChange,
  onPrimaryAction,
  onCancelSelection,
  primaryActionLabel = "Pick",
  selectionModeLabel,
  cancelActionLabel = "Cancel pin",
}) {
  const isDatabasePlace = hasDatabasePlaceId(place);
  const canViewPlace = place?._canView !== false && place?.can_view !== false && isDatabasePlace;
  const canSavePlace = place?._canSave !== false && place?.can_save !== false && isDatabasePlace;

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
              {formatRating(place.rating)}
            </span>
            <span style={{ color: "#64748b" }}>
              {place.review_count ?? 0} reviews
            </span>
          </div>
          {place.distance_km != null ? (
            <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#64748b" }}>
              <MapPin size={13} />
              <span>{place.distance_km} km away</span>
            </div>
          ) : null}
          <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#64748b" }}>
            <MapPin size={13} />
            <span style={{ fontFamily: "monospace" }}>
              {place.lat?.toFixed(5) ?? place.latitude?.toFixed(5) ?? "N/A"}, {place.lng?.toFixed(5) ?? place.longitude?.toFixed(5) ?? "N/A"}
            </span>
          </div>
        </div>

        {onPrimaryAction ? (
          <div style={{ fontSize: "12px", color: "#2563eb", fontWeight: 600, marginTop: "4px", textAlign: "center" }}>
            Do you want to use this location for your route?
          </div>
        ) : null}

        <div
          style={{
            display: "grid",
            gridTemplateColumns: onPrimaryAction ? "1fr 1fr 1fr" : "1fr 1fr",
            gap: "8px",
            marginTop: "2px",
          }}
        >
          <button
            className="btn-outline"
            style={{ padding: "8px 10px", borderRadius: "10px", fontWeight: 700 }}
            disabled={!canViewPlace}
            onClick={(e) => {
              e.stopPropagation();
              onViewPlace?.(place);
            }}
          >
            <ExternalLink size={14} style={{ marginRight: "4px" }} />
            View
          </button>
          <button
            className="btn-outline"
            style={{ padding: "8px 10px", borderRadius: "10px", fontWeight: 700 }}
            disabled={!canSavePlace}
            onClick={(e) => {
              e.stopPropagation();
              onSavePlace?.(place);
            }}
          >
            <Heart size={14} style={{ marginRight: "4px" }} />
            Save
          </button>
          <button
            className="btn-primary"
            style={{ padding: "8px 10px", borderRadius: "10px", fontWeight: 700 }}
            onClick={(e) => {
              e.stopPropagation();
              onPrimaryAction?.(place);
            }}
          >
            <Route size={14} style={{ marginRight: "4px" }} />
            {primaryActionLabel}
          </button>
        </div>

        {onSuggestChange ? (
          <button
            className="btn-outline"
            style={{ padding: "8px 10px", borderRadius: "10px", fontWeight: 700 }}
            onClick={(e) => {
              e.stopPropagation();
              onSuggestChange(place);
            }}
          >
            <MessageSquarePlus size={14} style={{ marginRight: "4px" }} />
            Suggest add/edit/delete
          </button>
        ) : null}

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
            onClick={(e) => {
              e.stopPropagation();
              onCancelSelection(place);
            }}
          >
            {cancelActionLabel}
          </button>
        ) : null}
      </div>
    </div>
  );
}
