import { AlertOctagon, RefreshCcw } from "lucide-react";

/**
 * Error Component - Hiển thị trạng thái lỗi mượt mà và trực quan (Advanced UI)
 * Tính năng nổi bật:
 * - Sử dụng tông màu đỏ nhạt (soft red) để cảnh báo lỗi mà không làm người dùng khó chịu.
 * - Hỗ trợ nút thao tác nhanh (Action button) với icon Refresh đồng bộ.
 * - Hiệu ứng Scale-in giúp icon xuất hiện tự nhiên hơn, thu hút sự chú ý.
 */
export default function Error({
    title = "Something went wrong",
    message = "We couldn’t load the data. Please try again.",
    actionText = "Retry",
    onAction
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
                background: "var(--color-bg-soft)",
                border: "1px solid rgba(239, 68, 68, 0.2)", // Viền đỏ nhạt để báo hiệu lỗi
                boxShadow: "0 8px 24px -6px rgba(239, 68, 68, 0.1)" // Đổ bóng mờ tông đỏ
            }}
        >
            {/* VÙNG CHỨA ICON VỚI HIỆU ỨNG XUẤT HIỆN */}
            <div
                className="scale-in"
                style={{
                    background: "rgba(239, 68, 68, 0.1)",
                    color: "#ef4444", // Màu đỏ Tailwind (red-500)
                    width: "80px",
                    height: "80px",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: "24px"
                }}
            >
                <AlertOctagon size={36} strokeWidth={1.5} />
            </div>

            {/* TIÊU ĐỀ CHÍNH */}
            <h3 style={{
                fontSize: "1.25rem",
                color: "var(--color-text)",
                marginBottom: "8px",
                fontWeight: 700,
                letterSpacing: "-0.01em"
            }}>
                {title}
            </h3>

            {/* MÔ TẢ CHI TIẾT (Giới hạn chiều rộng để không bị dàn trải quá dài) */}
            <p style={{
                color: "var(--color-text-soft)",
                maxWidth: "400px",
                margin: "0 auto",
                marginBottom: onAction ? "24px" : "0",
                lineHeight: 1.6,
                fontSize: "0.95rem"
            }}>
                {message}
            </p>

            {/* NÚT XỬ LÝ SỰ CỐ (Ví dụ: Thử lại) */}
            {onAction && (
                <button
                    className="btn-outline press"
                    onClick={onAction}
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        padding: "10px 24px",
                        borderRadius: "12px",
                        fontWeight: 600,
                        color: "#ef4444", // Đồng bộ màu chữ với icon cảnh báo
                        borderColor: "rgba(239, 68, 68, 0.3)",
                        backgroundColor: "white",
                        transition: "all 0.2s ease"
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = "#fef2f2"; // Đỏ cực nhạt (red-50) khi hover
                        e.currentTarget.style.borderColor = "#ef4444";
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = "white";
                        e.currentTarget.style.borderColor = "rgba(239, 68, 68, 0.3)";
                    }}
                >
                    <RefreshCcw size={16} strokeWidth={2.5} />
                    <span>{actionText}</span>
                </button>
            )}
        </div>
    );
}