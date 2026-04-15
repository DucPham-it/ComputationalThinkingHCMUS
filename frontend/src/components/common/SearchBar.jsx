import { useState, useRef } from "react";
import { Search, X, Sparkles } from "lucide-react";

/**
 * SearchBar Component - Thanh tìm kiếm thông minh (Advanced)
 * Nâng cấp trải nghiệm người dùng:
 * - Tự động focus/blur thông minh để tối ưu cho Mobile.
 * - Hiệu ứng chuyển màu icon khi tương tác (Micro-interactions).
 * - Nút xóa nhanh (Clear button) giúp thao tác liền mạch.
 */
export default function SearchBar({ 
    value = "", 
    onChange, 
    onSubmit,
    placeholder = "Where do you want to go? (food, cafe, mall...)"
}) {
    const [isFocused, setIsFocused] = useState(false);
    const inputRef = useRef(null);

    // Xử lý khi nhấn phím trên bàn phím
    function handleKeyDown(event) {
        if (event.key === "Enter") {
            onSubmit?.();
            // Tự động bỏ focus để đóng bàn phím ảo trên thiết bị di động
            inputRef.current?.blur(); 
        }
    }

    // Xóa nhanh nội dung và giữ focus để người dùng gõ từ khóa mới
    function handleClear() {
        onChange?.("");
        inputRef.current?.focus(); 
    }

    return (
        <div 
            // Class "search-bar" đã được cấu hình focus-within trong components.css
            className="search-bar"
            style={{ 
                alignItems: "center",
                position: "relative" 
            }}
        >
            {/* Search Icon: Đổi màu mượt mà khi người dùng đang nhập liệu */}
            <div style={{ 
                paddingLeft: "8px", 
                display: "flex", 
                alignItems: "center",
                color: isFocused ? "var(--color-primary)" : "var(--color-muted)",
                transition: "color 0.3s ease"
            }}>
                <Search size={20} strokeWidth={2.5} />
            </div>

            {/* Input chính */}
            <input
                ref={inputRef}
                type="text"
                placeholder={placeholder}
                value={value}
                onChange={(event) => onChange?.(event.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                style={{
                    flex: 1,
                    border: "none",
                    outline: "none",
                    background: "transparent",
                    fontSize: "1.05rem",
                    padding: "12px 8px",
                    color: "var(--color-text)",
                    fontWeight: 500
                }}
            />

            {/* Nút Xóa (Clear Button): Chỉ hiển thị khi có dữ liệu */}
            {value.length > 0 && (
                <button
                    className="press"
                    onClick={handleClear}
                    style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        background: "var(--color-bg-soft)",
                        border: "none",
                        borderRadius: "50%",
                        width: "26px",
                        height: "26px",
                        padding: 0,
                        color: "var(--color-text-soft)",
                        cursor: "pointer",
                        marginRight: "4px",
                        transition: "background 0.2s"
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = "#e2e8f0"}
                    onMouseLeave={(e) => e.currentTarget.style.background = "var(--color-bg-soft)"}
                    aria-label="Clear search"
                    title="Clear"
                >
                    <X size={14} strokeWidth={2.5} />
                </button>
            )}

            {/* Nút Thực thi tìm kiếm */}
            <button
                className="btn-primary press"
                onClick={onSubmit}
                style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "12px 24px",
                    borderRadius: "12px",
                    fontSize: "0.95rem",
                    fontWeight: 700,
                    letterSpacing: "0.02em"
                }}
            >
                <Sparkles size={18} />
                <span>Explore</span>
            </button>
        </div>
    );
}