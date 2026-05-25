import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
    Star, 
    MapPin, 
    DollarSign, 
    Clock, 
    ChevronRight, 
    Sparkles,
    Route,
    Heart
} from "lucide-react";
import { formatRating } from "../../utils/formatter";
import { useApp } from "../../hooks/useApp";
import { addFavorite } from "../../services/favoriteService";
import { recordPlacePick } from "../../services/mapPickService";
import { buildRouteDestinationFromMapPick } from "../../pages/MapView";

function getNumericPlaceId(place) {
    const numericId = Number(place?.id);
    return Number.isInteger(numericId) && numericId > 0 ? numericId : null;
}

/**
 * PlaceCard Component - Thẻ hiển thị thông tin địa điểm (Advanced UI)
 * * Các tính năng nâng cấp:
 * - Layout linh hoạt: Giữ nút và thông tin phụ luôn nằm ở đáy thẻ dù tiêu đề dài/ngắn.
 * - Color-coded status: Trạng thái mở/đóng cửa có màu sắc trực quan.
 * - Text Truncation: Tự động thêm "..." cho tiêu đề hoặc địa chỉ quá dài.
 * - Animation: Tích hợp hiệu ứng hover-lift và press từ animations.css.
 */
export default function PlaceCard({ place }) {
    const navigate = useNavigate();
    const { setSelectedPlace } = useApp();
    const [isSaved, setIsSaved] = useState(false);
    const [saving, setSaving] = useState(false);
    const [interactionError, setInteractionError] = useState("");

    useEffect(() => {
        setIsSaved(false);
        setSaving(false);
        setInteractionError("");
    }, [place.id]);

    const numericPlaceId = getNumericPlaceId(place);
    const canViewPlace = place?._canView !== false && place?.can_view !== false && numericPlaceId !== null;
    const canSavePlace = place?._canSave !== false && place?.can_save !== false && numericPlaceId !== null;

    function handleClick() {
        if (!canViewPlace) {
            setInteractionError("This OSM point is not in the local database yet, so it has no detail page.");
            return;
        }

        navigate(`/places/${numericPlaceId}`);
    }

    async function handlePick(event) {
        event.stopPropagation();
        setInteractionError("");

        let destination;
        try {
            destination = buildRouteDestinationFromMapPick(place);
        } catch (error) {
            setInteractionError("This place is missing coordinates. Cannot navigate to route.");
            return;
        }

        if (numericPlaceId !== null) {
            try {
                await recordPlacePick(numericPlaceId);
            } catch (error) {
                console.error("Failed to record place pick, proceeding to route anyway", error);
            }
        }

        setSelectedPlace(destination);
        navigate("/route");
    }

    async function handleSave(event) {
        event.stopPropagation();
        if (saving || isSaved) {
            return;
        }

        if (!canSavePlace) {
            setInteractionError("Only database places can be saved. OSM-only points can still be used for routing.");
            return;
        }

        try {
            setSaving(true);
            setInteractionError("");
            await addFavorite(numericPlaceId);
            setIsSaved(true);
        } catch (error) {
            console.error("Failed to save place", error);
            const detail = error?.response?.data?.detail;
            setInteractionError(detail || "We could not save this place. Please log in and try again.");
        } finally {
            setSaving(false);
        }
    }

    // Xử lý logic hiển thị màu sắc cho trạng thái Đóng/Mở cửa
    const isOpen = place.open_now;
    const hasStatus = isOpen !== null && isOpen !== undefined;
    const statusColor = !hasStatus ? "var(--color-muted)" : isOpen ? "#10b981" : "#ef4444"; // Xanh lục (Mở) / Đỏ (Đóng)
    const statusBg = !hasStatus ? "var(--color-bg-soft)" : isOpen ? "#d1fae5" : "#fee2e2";

    return (
        <div
            className="card dynamic-card place-card fade-in hover-lift"
            style={{ 
                cursor: canViewPlace ? "pointer" : "default",
                padding: 0, // Xóa padding mặc định của thẻ card để banner chạm viền
                display: "flex",
                flexDirection: "column",
                overflow: "hidden", // Bo góc đều cho cả banner và nội dung
                height: "100%" // Giúp các thẻ trong cùng một grid row có chiều cao bằng nhau
            }}
            onClick={handleClick}
        >
            {/* 1. HERO BANNER AREA: Điểm nhấn thị giác */}
            <div style={{
                height: "130px",
                background: place.photo_url
                    ? `linear-gradient(rgba(15, 23, 42, 0.18), rgba(15, 23, 42, 0.18)), url(${place.photo_url}) center/cover`
                    : "linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%)",
                position: "relative",
                borderBottom: "1px solid var(--color-border)"
            }}>
                {/* AI Score Badge: Góc trên cùng bên phải */}
                <div style={{
                    position: "absolute",
                    top: "12px",
                    right: "12px",
                    background: "var(--color-primary)",
                    color: "white",
                    padding: "4px 10px",
                    borderRadius: "12px",
                    fontSize: "0.85rem",
                    fontWeight: 700,
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    boxShadow: "0 4px 12px rgba(37,99,235,0.3)"
                }}>
                    <Sparkles size={14} /> 
                    {place.score ?? "N/A"}
                </div>

                {/* Category Badge: Góc dưới cùng bên trái */}
                <div style={{
                    position: "absolute",
                    bottom: "12px",
                    left: "16px",
                    background: "rgba(255, 255, 255, 0.85)",
                    backdropFilter: "blur(8px)",
                    padding: "4px 12px",
                    borderRadius: "20px",
                    fontSize: "0.75rem",
                    fontWeight: 600,
                    color: "var(--color-text)",
                    border: "1px solid rgba(255, 255, 255, 0.4)"
                }}>
                    {place.primary_type ?? "Unknown"}
                </div>
            </div>

            {/* 2. CONTENT AREA: Vùng chứa dữ liệu chính */}
            <div style={{ 
                padding: "20px 16px", 
                display: "flex", 
                flexDirection: "column", 
                flex: 1, 
                gap: "14px" 
            }}>
                
                {/* Tiêu đề & Địa chỉ */}
                <div>
                    <h3 className="card-title" style={{ 
                        fontSize: "1.15rem", 
                        lineHeight: 1.3,
                        // Giới hạn hiển thị tối đa 2 dòng, quá sẽ hiện "..."
                        display: "-webkit-box", 
                        WebkitLineClamp: 2, 
                        WebkitBoxOrient: "vertical", 
                        overflow: "hidden" 
                    }}>
                        {place.name}
                    </h3>
                    <p className="card-text" style={{ 
                        fontSize: "0.85rem", 
                        whiteSpace: "nowrap", 
                        overflow: "hidden", 
                        textOverflow: "ellipsis" 
                    }}>
                        {place.address}
                    </p>
                </div>

                {/* Đánh giá & Khoảng cách */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.9rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", fontWeight: 700, color: "var(--color-text)" }}>
                        <Star size={16} fill="var(--color-accent)" color="var(--color-accent)" />
                        <span>{formatRating(place.rating)}</span>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "4px", color: "var(--color-text-soft)", fontWeight: 500 }}>
                        <MapPin size={15} />
                        <span>{place.distance_km ?? "N/A"} km</span>
                    </div>
                </div>

                <div style={{ fontSize: "0.85rem", color: "var(--color-text-soft)", fontWeight: 600 }}>
                    Reviews: {place.review_count ?? 0}
                </div>

                {/* Phân cách */}
                <div style={{ marginTop: "auto" }}>
                    <div style={{ width: "100%", height: "1px", background: "var(--color-border)", margin: "12px 0", borderStyle: "dashed", borderWidth: "1px 0 0 0" }} />
                    
                    {/* Chi phí & Trạng thái mở cửa */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.85rem" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "4px", color: "var(--color-text-soft)", fontWeight: 600 }}>
                            {/* Đổi màu icon Dollar thành xanh lá để liên tưởng tới tiền */}
                            <DollarSign size={16} color="#10b981" />
                            <span>{place.price_level ?? "N/A"}</span>
                        </div>

                        {/* Nhãn dán hiển thị trạng thái động */}
                        <div style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "6px",
                            padding: "4px 10px",
                            borderRadius: "8px",
                            background: statusBg,
                            color: statusColor,
                            fontWeight: 700,
                            fontSize: "0.8rem"
                        }}>
                            <Clock size={14} />
                            <span>{hasStatus ? (isOpen ? "Open" : "Closed") : "N/A"}</span>
                        </div>
                    </div>
                </div>

                {/* 3. ACTION BUTTON */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px", marginTop: "4px" }}>
                    <button
                        className="btn-outline press"
                        style={{
                            width: "100%",
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                            gap: "6px",
                            padding: "10px",
                            borderRadius: "10px",
                            fontWeight: 600
                        }}
                        onClick={(e) => {
                            e.stopPropagation();
                            handleClick();
                        }}
                        disabled={!canViewPlace}
                    >
                        <span>View</span>
                        <ChevronRight size={18} />
                    </button>
                    <button
                        className={isSaved ? "btn-primary press" : "btn-outline press"}
                        style={{
                            width: "100%",
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                            gap: "6px",
                            padding: "10px",
                            borderRadius: "10px",
                            fontWeight: 700
                        }}
                        onClick={handleSave}
                        disabled={saving || isSaved || !canSavePlace}
                    >
                        <Heart size={18} fill={isSaved ? "currentColor" : "none"} />
                        <span>{isSaved ? "Saved" : saving ? "Saving" : "Save"}</span>
                    </button>
                    <button
                        className="btn-primary press"
                        style={{
                            width: "100%",
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                            gap: "6px",
                            padding: "10px",
                            borderRadius: "10px",
                            fontWeight: 700
                        }}
                        onClick={handlePick}
                    >
                        <span>Pick</span>
                        <Route size={18} />
                    </button>
                </div>

                {interactionError ? (
                    <p
                        style={{
                            margin: 0,
                            padding: "10px 12px",
                            borderRadius: "12px",
                            background: "#fef2f2",
                            color: "#b91c1c",
                            fontSize: "0.85rem",
                            fontWeight: 600,
                        }}
                    >
                        {interactionError}
                    </p>
                ) : null}
            </div>
        </div>
    );
}
