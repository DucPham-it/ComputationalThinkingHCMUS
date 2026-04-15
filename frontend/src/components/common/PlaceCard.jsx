import { useNavigate } from "react-router-dom";
import { 
    Star, 
    MapPin, 
    DollarSign, 
    Clock, 
    ChevronRight, 
    Sparkles 
} from "lucide-react";
import { formatRating } from "../../utils/formatter";

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

    function handleClick() {
        navigate(`/places/${place.id}`);
    }

    // Xử lý logic hiển thị màu sắc cho trạng thái Đóng/Mở cửa
    const isOpen = place.open_now;
    const hasStatus = isOpen !== null && isOpen !== undefined;
    const statusColor = !hasStatus ? "var(--color-muted)" : isOpen ? "#10b981" : "#ef4444"; // Xanh lục (Mở) / Đỏ (Đóng)
    const statusBg = !hasStatus ? "var(--color-bg-soft)" : isOpen ? "#d1fae5" : "#fee2e2";

    return (
        <div
            className="card fade-in hover-lift"
            style={{ 
                cursor: "pointer",
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
                // Nếu backend có trả về image_url, bạn có thể thay thế bằng: `url(${place.image_url})`
                background: "linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%)", 
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
                <button
                    className="btn-outline press"
                    style={{
                        width: "100%",
                        marginTop: "4px",
                        display: "flex",
                        justifyContent: "center",
                        alignItems: "center",
                        gap: "6px",
                        padding: "10px",
                        borderRadius: "10px",
                        fontWeight: 600
                    }}
                    onClick={(e) => {
                        e.stopPropagation(); // Ngăn sự kiện click của button kích hoạt sự kiện của card
                        handleClick();
                    }}
                >
                    <span>View Details</span>
                    <ChevronRight size={18} />
                </button>
            </div>
        </div>
    );
}
