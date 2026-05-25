import { Link } from "react-router-dom";

/**
 * Footer Component - Chân trang của ứng dụng (Advanced UI)
 * - Đã loại bỏ lucide-react để tránh lỗi không tìm thấy icon trên localhost.
 * - Sử dụng Text-links thay cho icon mạng xã hội.
 * - Duy trì các hiệu ứng animation (float, hover-lift, pulse-soft) từ CSS.
 */
export default function Footer() {
    const currentYear = new Date().getFullYear();

    return (
        <footer 
            className="footer fade-in"
            style={{
                marginTop: "auto", // Luôn nằm dưới cùng của trang
                background: "rgba(255, 255, 255, 0.58)",
                backdropFilter: "blur(18px)",
                borderTop: "1px solid var(--color-border)",
                padding: "48px 0 24px 0" // Không gian đệm (whitespace) cao cấp
            }}
        >
            <div className="container" style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
                
                {/* DÒNG TRÊN: Logo & Liên kết mạng xã hội */}
                <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "24px"
                }}>
                    {/* Khu vực Thương hiệu (Brand) */}
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        <div style={{
                            background: "var(--color-primary-soft)",
                            color: "var(--color-primary)",
                            padding: "6px 10px",
                            borderRadius: "10px",
                            fontWeight: 800,
                            fontSize: "1.2rem"
                        }}>
                            S
                        </div>
                        
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                            <span style={{ fontSize: "1.15rem", fontWeight: 800, color: "var(--color-text)", letterSpacing: 0 }}>
                                D<span style={{ color: "var(--color-primary)" }}>Map</span>
                            </span>
                            
                            {/* Badge hiệu ứng lơ lửng (float) */}
                            <span 
                                className="float"
                                style={{
                                    fontSize: "0.7rem",
                                    fontWeight: 700,
                                    background: "linear-gradient(135deg, #10b981, #059669)",
                                    color: "white",
                                    padding: "2px 8px",
                                    borderRadius: "20px"
                                }}
                            >
                                GoToEveryWhere
                            </span>
                        </div>
                    </div>

                    {/* Danh sách liên kết xã hội (Dạng chữ để tránh lỗi icon) */}
                    <div style={{ display: "flex", gap: "24px" }}>
                        <a 
                            href="https://github.com/DucPham-it/ComputationalThinkingHCMUS" 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="hover-lift" 
                            style={{ 
                                color: "var(--color-text-soft)", 
                                fontSize: "0.85rem", 
                                fontWeight: 600,
                                textDecoration: "none"
                            }}
                        >
                            Github
                        </a>

                        <a 
                            href="mailto:phamvoduc.it1905@gmail.com" 
                            className="hover-lift" 
                            style={{ 
                                color: "var(--color-text-soft)", 
                                fontSize: "0.85rem", 
                                fontWeight: 600,
                                textDecoration: "none"
                            }}
                        >
                            Contact
                        </a>
                    </div>
                </div>

                {/* Đường kẻ phân cách (Divider) */}
                <div style={{ width: "100%", height: "1px", background: "var(--color-border)" }} />

                {/* DÒNG DƯỚI: Bản quyền & Tech Stack */}
                <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "16px"
                }}>
                    <p style={{ margin: 0, fontSize: "0.9rem", color: "var(--color-text-soft)", fontWeight: 500 }}>
                        © {currentYear} Make By Group 3 - Computational Thinking - 24CTT3
                    </p>

                    {/* Credits ghi chú công nghệ */}
                    <div style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        fontSize: "0.9rem",
                        color: "var(--color-muted)",
                        fontWeight: 500
                    }}>
                        <span>Build by Duc and </span>
                        {/* Trái tim dùng ký tự Unicode để thay cho icon Heart */}
                        <span style={{ color: "#ef4444" }} className="pulse-soft">Power Of GPT</span>
                    </div>
                </div>
            </div>
        </footer>
    );
}
