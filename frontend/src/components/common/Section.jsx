/**
 * Section Component - Vùng bọc nội dung chuẩn (Advanced Layout)
 * Tính năng nổi bật:
 * - Hỗ trợ Subtitle (Tiêu đề phụ) để tăng ngữ cảnh cho người dùng.
 * - Fluid padding/margin tự động tương thích với kích thước màn hình.
 * - Tối ưu SEO và Accessibility với thẻ aria-labelledby.
 * - Hiệu ứng xuất hiện mượt mà (fade-in).
 */
export default function Section({
    title,
    subtitle, // Mới: Hỗ trợ đoạn text mô tả nhỏ dưới tiêu đề
    children,
    action,   // Nút hành động (Ví dụ: "See all", "Filters")
    style = {},
    className = "" // Cho phép truyền thêm class từ bên ngoài nếu cần
}) {
    // Tạo ID an toàn cho Accessibility (A11y)
    const sectionId = title ? `section-${title.replace(/\s+/g, '-').toLowerCase()}` : undefined;

    return (
        <section
            className={`container fade-in ${className}`}
            style={{
                // Sử dụng biến không gian linh hoạt thay vì fix cứng 24px
                marginBottom: "clamp(32px, 5vw, 64px)", 
                ...style
            }}
            aria-labelledby={sectionId}
        >
            {/* HEADER AREA */}
            {(title || subtitle || action) && (
                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-end", // Căn đáy để nút action ngang hàng với baseline của title
                        marginBottom: "24px",
                        paddingBottom: "16px",
                        borderBottom: "1px solid rgba(0, 0, 0, 0.04)", // Đường viền mờ phân cách tinh tế
                        flexWrap: "wrap",
                        gap: "16px"
                    }}
                >
                    {/* Nhóm Tiêu đề & Phụ đề */}
                    <div style={{ display: "flex", flexDirection: "column", gap: "6px", flex: 1 }}>
                        {title && (
                            <h2 
                                id={sectionId}
                                style={{ 
                                    margin: 0,
                                    fontSize: "clamp(1.5rem, 3vw, 1.8rem)", // Font chữ tự động thu nhỏ trên Mobile
                                    fontWeight: 800,
                                    letterSpacing: "-0.02em",
                                    color: "var(--color-text)"
                                }}
                            >
                                {title}
                            </h2>
                        )}
                        
                        {subtitle && (
                            <p style={{ 
                                margin: 0, 
                                color: "var(--color-text-soft)", 
                                fontSize: "0.95rem",
                                lineHeight: 1.5 
                            }}>
                                {subtitle}
                            </p>
                        )}
                    </div>

                    {/* Vùng hành động (Action / Nút bấm) */}
                    {action && (
                        <div style={{ display: "flex", alignItems: "center" }}>
                            {action}
                        </div>
                    )}
                </div>
            )}

            {/* CONTENT AREA */}
            <div style={{ width: "100%", position: "relative" }}>
                {children}
            </div>
        </section>
    );
}