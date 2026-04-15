import { SearchX } from "lucide-react";

/**
 * Empty Component - Hiển thị trạng thái "Không có dữ liệu" (Advanced UI)
 * Tính năng nổi bật:
 * - Hiệu ứng lơ lửng (float) cho icon để giao diện sinh động hơn.
 * - Hỗ trợ truyền icon tùy chỉnh từ bên ngoài (mặc định là SearchX).
 * - Sử dụng viền đứt nét (dashed border) theo chuẩn thiết kế Empty State hiện đại.
 */
export default function Empty({
    title = "No results found",
    message = "Try adjusting your search keywords or explore different categories.",
    actionText,
    onAction,
    icon: Icon = SearchX // Cho phép override icon nếu muốn dùng cho màn hình Favorites trống
}) {
    return (
        <div
            className="card fade-in"
            style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
                padding: "48px 24px",
                minHeight: "300px",
                background: "var(--color-bg-soft)", // Nền xám nhạt dịu mắt
                border: "2px dashed var(--color-border)", // Viền đứt nét đặc trưng
                boxShadow: "none" // Bỏ bóng để nhấn mạnh trạng thái "trống"
            }}
        >
            {/* Vùng chứa Icon với hiệu ứng lơ lửng (float) */}
            <div 
                className="float"
                style={{
                    background: "var(--color-primary-soft)",
                    color: "var(--color-primary)",
                    width: "80px",
                    height: "80px",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: "24px",
                    boxShadow: "0 8px 24px -6px rgba(37, 99, 235, 0.2)"
                }}
            >
                <Icon size={36} strokeWidth={1.5} />
            </div>

            {/* Tiêu đề chính */}
            <h3 style={{ 
                fontSize: "1.25rem", 
                color: "var(--color-text)", 
                marginBottom: "8px",
                fontWeight: 700,
                letterSpacing: "-0.01em"
            }}>
                {title}
            </h3>

            {/* Nội dung thông báo phụ (được giới hạn độ dài để không dàn trải) */}
            <p style={{ 
                color: "var(--color-text-soft)", 
                maxWidth: "380px", 
                margin: "0 auto",
                marginBottom: actionText ? "24px" : "0",
                lineHeight: 1.6,
                fontSize: "0.95rem"
            }}>
                {message}
            </p>

            {/* Nút hành động (Ví dụ: Xóa bộ lọc, Về trang chủ) */}
            {actionText && onAction && (
                <button 
                    className="btn-primary press" 
                    onClick={onAction}
                    style={{
                        padding: "10px 24px",
                        borderRadius: "12px",
                        fontWeight: 600,
                        letterSpacing: "0.02em"
                    }}
                >
                    {actionText}
                </button>
            )}
        </div>
    );
}