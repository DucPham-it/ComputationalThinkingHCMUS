import { useEffect, useState, useRef } from "react";
import { Sparkles, Compass } from "lucide-react";

import Section from "../components/common/Section";
import SearchBar from "../components/common/SearchBar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import Empty from "../components/common/Empty";
import Error from "../components/common/Error";

import FilterPanel from "../components/recommendation/FilterPanel";
import RankingPanel from "../components/recommendation/RankingPanel";
import RecommendationList from "../components/recommendation/RecommendationList";

import { fetchRecommendations } from "../services/placeService";

/**
 * Màn hình Home (Trang chủ)
 * Đã nâng cấp giao diện UI/UX nhưng vẫn giữ nguyên cấu trúc vận hành API gốc.
 */
export default function Home() {
    const [query, setQuery] = useState("");
    const [places, setPlaces] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    // State UX để đổi tiêu đề khi đã thực hiện tìm kiếm
    const [hasSearched, setHasSearched] = useState(false);
    
    // Ref dùng để tự động cuộn màn hình xuống kết quả tìm kiếm
    const resultsRef = useRef(null);

    useEffect(() => {
        loadRecommendations();
    }, []);

    // Logic gốc: Tải danh sách mặc định khi vào trang
    async function loadRecommendations() {
        try {
            setLoading(true);
            setError(null);

            const data = await fetchRecommendations({ query: "" });
            setPlaces(data.items ?? []);
        } catch (err) {
            console.error(err);
            setError("Failed to load recommendations");
            setPlaces([]);
        } finally {
            setLoading(false);
        }
    }

    // Logic gốc: Tìm kiếm theo từ khóa
    async function handleSearch() {
        if (!query.trim()) return;

        try {
            setLoading(true);
            setError(null);
            setHasSearched(true);

            const data = await fetchRecommendations({ query });
            setPlaces(data.items ?? []);

            // UX: Cuộn mượt mà xuống phần kết quả sau khi gọi API
            if (resultsRef.current) {
                resultsRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        } catch (err) {
            console.error(err);
            setError("Search failed. Please try again.");
            setPlaces([]);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
            
            {/* HERO BANNER: Giao diện tìm kiếm nổi bật */}
            <section style={{
                position: "relative",
                padding: "80px 24px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
                background: "linear-gradient(135deg, var(--color-primary-soft) 0%, #f3e8ff 100%)",
                borderBottom: "1px solid var(--color-border)",
                marginBottom: "40px"
            }}>
                <div className="fade-in" style={{ maxWidth: "700px", width: "100%", zIndex: 1 }}>
                    <div style={{ 
                        display: "inline-flex", 
                        alignItems: "center", 
                        gap: "8px", 
                        background: "rgba(255,255,255,0.6)", 
                        padding: "6px 16px", 
                        borderRadius: "20px",
                        marginBottom: "20px",
                        fontWeight: 600,
                        color: "var(--color-primary)",
                        backdropFilter: "blur(4px)"
                    }}>
                        <Sparkles size={16} />
                        <span>Smart Travel Engine</span>
                    </div>
                    
                    <h1 style={{ 
                        fontSize: "clamp(2rem, 5vw, 3.5rem)", 
                        fontWeight: 800, 
                        color: "var(--color-text)",
                        lineHeight: 1.1,
                        marginBottom: "16px",
                        letterSpacing: "-0.03em"
                    }}>
                        Discover your next <br />
                        <span style={{ color: "var(--color-primary)" }}>perfect destination</span>
                    </h1>
                    
                    <p style={{ 
                        fontSize: "1.1rem", 
                        color: "var(--color-text-soft)", 
                        marginBottom: "32px",
                        maxWidth: "500px",
                        margin: "0 auto 32px auto"
                    }}>
                        Tell us what you're craving or where you want to explore. We'll curate the best spots just for you.
                    </p>

                    <div style={{ 
                        boxShadow: "0 20px 40px -10px rgba(37, 99, 235, 0.15)", 
                        borderRadius: "16px" 
                    }}>
                        <SearchBar
                            value={query}
                            onChange={setQuery}
                            onSubmit={handleSearch}
                        />
                    </div>
                </div>
            </section>

            {/* BỘ LỌC TÌM KIẾM */}
            <Section 
                title="Customize your results"
                subtitle="Adjust filters to match your preferences"
            >
                <div className="section-soft row" style={{ gap: "16px", alignItems: "flex-start" }}>
                    <div style={{ flex: "1 1 300px" }}>
                        <FilterPanel />
                    </div>
                    <div style={{ flex: "1 1 300px" }}>
                        <RankingPanel />
                    </div>
                </div>
            </Section>

            {/* Anchor point để cuộn trang tới */}
            <div ref={resultsRef} style={{ scrollMarginTop: "100px" }} />

            {/* DANH SÁCH KẾT QUẢ */}
            <Section 
                title={hasSearched ? "Search Results" : "Recommended places"}
                subtitle={
                    !loading && !error && places.length > 0 
                        ? `Found ${places.length} amazing places` 
                        : "Handpicked spots based on your preferences"
                }
            >
                {loading && (
                    <LoadingSpinner message="Finding best places for you..." />
                )}

                {!loading && error && (
                    <Error
                        message={error}
                        onAction={handleSearch}
                    />
                )}

                {!loading && !error && places.length === 0 && (
                    <Empty
                        icon={Compass}
                        title="No places found"
                        message="Try searching for food, cafe, or shopping"
                    />
                )}

                {!loading && !error && places.length > 0 && (
                    <div className="fade-in-delay-1">
                        <RecommendationList places={places} />
                    </div>
                )}
            </Section>
        </div>
    );
}