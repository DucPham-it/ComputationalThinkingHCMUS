import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import AppLogo from "../../assets/pictures/logo.png";
import { useAuth } from "../../hooks/useAuth";
import { 
    MapPin, 
    Navigation, 
    Heart, 
    User, 
    Menu, 
    X, 
    Compass,
    ShieldCheck
} from "lucide-react";

/**
 * Navbar Component - Thanh điều hướng chính của ứng dụng
 * Tính năng nâng cao:
 * - Dynamic Glassmorphism: Thay đổi độ trong suốt và hiệu ứng blur khi cuộn trang.
 * - Active State Tracking: Tự động highlight mục menu tương ứng với URL hiện tại.
 * - Mobile Optimized: Hỗ trợ menu trượt cho thiết bị di động.
 * - Micro-interactions: Hiệu ứng hover và click mượt mà (smooth transitions).
 */
export default function Navbar() {
    const { user, isAuthenticated, hasCompletedProfile } = useAuth();
    const location = useLocation();
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    // Lắng nghe sự kiện cuộn trang để cập nhật trạng thái UI
    useEffect(() => {
        const handleScroll = () => {
            // Ngưỡng 20px để kích hoạt hiệu ứng thu nhỏ header
            setIsScrolled(window.scrollY > 20);
        };

        // Sử dụng { passive: true } để tối ưu hiệu suất cuộn của trình duyệt
        window.addEventListener("scroll", handleScroll, { passive: true });
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    // Tự động đóng Mobile Menu khi người dùng chuyển hướng trang
    useEffect(() => {
        setIsMobileMenuOpen(false);
    }, [location.pathname]);

    /**
     * Kiểm tra trạng thái hoạt động của đường dẫn
     * @param {string} path - URL cần kiểm tra
     * @returns {boolean} - Trả về true nếu trùng khớp với location hiện tại
     */
    const isActive = (path) => location.pathname === path;

    // Cấu hình danh sách điều hướng (Navigation Config)
    const navLinks = [
        { path: "/", label: "Suggestion", icon: Compass },
        { path: "/map", label: "Map", icon: MapPin },
        { path: "/route", label: "Route", icon: Navigation },
        { path: "/favorites", label: "Saved", icon: Heart },
    ];
    if (isAuthenticated && user?.is_admin) {
        navLinks.push({ path: "/admin", label: "Admin", icon: ShieldCheck });
    }
    const profileLabel = hasCompletedProfile ? "Profile" : "Complete Profile";

    return (
        <header 
            className={`navbar ${isScrolled ? "glass" : ""}`}
            style={{
                position: "sticky",
                top: 0,
                zIndex: 1000,
                transition: "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                padding: isScrolled ? "10px 0" : "18px 0",
                backgroundColor: isScrolled ? "rgba(255, 255, 255, 0.8)" : "transparent",
                boxShadow: isScrolled ? "0 10px 30px -10px rgba(0, 0, 0, 0.08)" : "none",
                borderBottom: isScrolled ? "1px solid var(--color-border)" : "1px solid transparent"
            }}
        >
            <div className="container navbar-inner" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                
               
                <Link to="/" className="logo press" style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <div style={{
                        background: "rgba(255, 255, 255, 0.88)",
                        padding: "6px",
                        borderRadius: "16px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        boxShadow: "0 10px 24px rgba(15, 23, 42, 0.12)",
                        transform: isScrolled ? "scale(0.9)" : "scale(1)",
                        transition: "transform 0.3s ease"
                    }}>
                        <img
                            src={AppLogo}
                            alt="SmartTravel logo"
                            style={{
                                width: "42px",
                                height: "42px",
                                objectFit: "contain",
                                display: "block"
                            }}
                        />
                    </div>
                    <span style={{ 
                        fontSize: "1.25rem", 
                        fontWeight: 800, 
                        letterSpacing: "-0.04em",
                        color: "var(--color-text)" 
                    }}>
                        GoTo<span style={{ color: "var(--color-primary)" }}>Everywhere</span>
                    </span>
                </Link>

                {/* DESKTOP MENU: Ẩn trên mobile thông qua CSS */}
                <nav className="nav-links" style={{ display: "flex", alignItems: "center", gap: "28px" }}>
                    {navLinks.map((link) => {
                        const active = isActive(link.path);
                        return (
                            <Link
                                key={link.path}
                                to={link.path}
                                className={`nav-link press ${active ? "active-link" : ""}`}
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "8px",
                                    fontSize: "0.95rem",
                                    fontWeight: active ? 700 : 500,
                                    color: active ? "var(--color-primary)" : "var(--color-text-soft)",
                                    transition: "color 0.3s ease"
                                }}
                            >
                                <link.icon size={17} strokeWidth={active ? 2.5 : 2} />
                                {link.label}
                            </Link>
                        );
                    })}

                    {/* Dải phân cách dọc (Visual Divider) */}
                    <div style={{ width: "1px", height: "24px", background: "var(--color-border)", margin: "0 4px" }} />

                    <Link 
                        to={isAuthenticated ? "/profile" : "/login"} 
                        className="btn-primary press"
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "8px",
                            padding: "10px 20px",
                            borderRadius: "14px",
                            fontSize: "0.9rem",
                            textDecoration: "none",
                            fontWeight: 600
                        }}
                    >
                        <User size={16} strokeWidth={2.5} />
                        {isAuthenticated ? profileLabel : "Sign In"}
                    </Link>
                </nav>

                {/* MOBILE TOGGLE: Chỉ hiển thị trên màn hình nhỏ */}
                <button 
                    className="mobile-toggle press"
                    onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    style={{
                        background: "var(--color-bg-soft)",
                        border: "none",
                        padding: "8px",
                        borderRadius: "10px",
                        cursor: "pointer",
                        color: "var(--color-text)"
                    }}
                >
                    {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* MOBILE DROPDOWN MENU: Hiệu ứng trượt xuống mượt mà */}
            {isMobileMenuOpen && (
                <div className="mobile-menu fade-in glass" style={{
                    position: "absolute",
                    top: "100%",
                    left: 0,
                    width: "100%",
                    padding: "24px",
                    borderBottom: "1px solid var(--color-border)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "16px",
                    boxShadow: "0 20px 40px rgba(0,0,0,0.1)"
                }}>
                    {navLinks.map((link) => (
                        <Link 
                            key={link.path} 
                            to={link.path} 
                            style={{ 
                                display: "flex", 
                                alignItems: "center", 
                                gap: "12px", 
                                fontWeight: 600,
                                fontSize: "1.05rem",
                                color: isActive(link.path) ? "var(--color-primary)" : "var(--color-text)"
                            }}
                        >
                            <link.icon size={20} />
                            {link.label}
                        </Link>
                    ))}
                    <Link to={isAuthenticated ? "/profile" : "/login"} className="btn-primary" style={{ textAlign: "center", padding: "14px", marginTop: "8px" }}>
                        {isAuthenticated ? profileLabel : "Sign In"}
                    </Link>
                </div>
            )}
        </header>
    );
}
