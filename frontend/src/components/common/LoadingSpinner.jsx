import { useState, useEffect } from "react";
import { Compass, Sparkles } from "lucide-react";

/**
 * LoadingSpinner Component - Trạng thái chờ tải dữ liệu (Advanced UI)
 * Tính năng nổi bật:
 * - Thay đổi câu thông báo xoay vòng (Smart Messaging) giúp giảm cảm giác chờ đợi.
 * - Icon tùy chỉnh kết hợp hiệu ứng xoay (spin-slow) và tỏa sáng (pulse-soft).
 * - Hỗ trợ hiển thị linh hoạt (trong nội dung hoặc toàn màn hình).
 */
export default function LoadingSpinner({ 
    message, // Cho phép ghi đè thông báo mặc định nếu muốn
    fullHeight = false // Bật true nếu muốn spinner chiếm trọn chiều cao (ví dụ: đang load page)
}) {
    // Tập hợp các câu thông báo thú vị (tiếng Anh cho UI)
    const defaultMessages = [
        "Scouting the best spots...",
        "Analyzing AI recommendations...",
        "Curating your experience...",
        "Almost there..."
    ];

    const [textIndex, setTextIndex] = useState(0);

    // Logic đảo thông báo mỗi 2.5 giây để UX trở nên sinh động hơn (engaging)
    useEffect(() => {
        if (message) return; // Nếu dev truyền message cứng vào thì bỏ qua hiệu ứng xoay vòng

        const interval = setInterval(() => {
            setTextIndex((prev) => (prev + 1) % defaultMessages.length);
        }, 2500);

        return () => clearInterval(interval);
    }, [message, defaultMessages.length]);

    const displayText = message || defaultMessages[textIndex];

    return (
        <div 
            className="fade-in"
            style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                minHeight: fullHeight ? "60vh" : "240px", // Đảm bảo luôn có khoảng trống an toàn
                width: "100%",
                gap: "24px"
            }}
        >
            {/* Vùng chứa Spinner tùy chỉnh */}
            <div 
                style={{ 
                    position: "relative", 
                    width: "72px", 
                    height: "72px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center"
                }}
            >
                {/* Vòng hào quang tỏa sáng phía sau (dùng class từ animations.css) */}
                <div 
                    className="pulse-soft" 
                    style={{
                        position: "absolute",
                        inset: "4px", // Thu nhỏ lại một chút so với khung 72px
                        background: "var(--color-primary-soft)",
                        borderRadius: "50%",
                        zIndex: 0
                    }} 
                />

                {/* La bàn xoay chậm - Đại diện cho du lịch & Khám phá */}
                <Compass 
                    size={44} 
                    color="var(--color-primary)" 
                    className="spin-slow" 
                    style={{ position: "relative", zIndex: 1 }}
                    strokeWidth={1.5}
                />

                {/* Tia lửa AI lơ lửng - Đại diện cho hệ thống đề xuất thông minh */}
                <div style={{
                    position: "absolute",
                    top: "-2px",
                    right: "-2px",
                    background: "white",
                    borderRadius: "50%",
                    padding: "2px",
                    zIndex: 2,
                    boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
                }}>
                    <Sparkles size={16} color="var(--color-accent)" />
                </div>
            </div>

            {/* Vùng chứa Text với hiệu ứng xuất hiện lại mỗi khi đổi câu chữ */}
            <div style={{ height: "24px", overflow: "hidden", textAlign: "center" }}>
                <p 
                    key={displayText} // Đổi key ép React re-render phần tử để kích hoạt lại CSS animation
                    className="appear" 
                    style={{ 
                        margin: 0,
                        fontWeight: 600, 
                        color: "var(--color-text-soft)", 
                        fontSize: "1.05rem",
                        letterSpacing: "0.01em"
                    }}
                >
                    {displayText}
                </p>
            </div>
        </div>
    );
}