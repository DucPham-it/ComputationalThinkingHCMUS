import { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
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
import { useAuth } from "../hooks/useAuth";
import { useApp } from "../hooks/useApp";
import { getCurrentBrowserLocation } from "../utils/geolocation";

/**
 * Màn hình Home (Trang chủ)
 * Đã nâng cấp giao diện UI/UX nhưng vẫn giữ nguyên cấu trúc vận hành API gốc.
 */
export default function Home() {
    const { isAuthenticated, hasCompletedProfile } = useAuth();
    const {
        currentLocation,
        setCurrentLocation,
        recommendationPlaces,
        setRecommendationPlaces
    } = useApp();
    const [query, setQuery] = useState("");
    const [places, setPlaces] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [locationStatus, setLocationStatus] = useState("");
    
    // State UX để đổi tiêu đề khi đã thực hiện tìm kiếm
    const [hasSearched, setHasSearched] = useState(false);
    
    // Ref dùng để tự động cuộn màn hình xuống kết quả tìm kiếm
    const resultsRef = useRef(null);
    const canUseChat = isAuthenticated && hasCompletedProfile;

    async function loadSuggestions() {
        if (!canUseChat) {
            return;
        }

        try {
            setLoading(true);
            setError(null);

            const data = await fetchRecommendations({
                latitude: currentLocation?.lat,
                longitude: currentLocation?.lng,
            });
            const items = data.items ?? [];
            setPlaces(items);
            setRecommendationPlaces(items);
            setHasSearched(false);
        } catch (err) {
            console.error(err);
            setError("Suggestions are unavailable right now. Please try again.");
            setPlaces([]);
            setRecommendationPlaces([]);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        let active = true;

        async function hydrateLocation() {
            if (currentLocation) {
                return;
            }

            try {
                const location = await getCurrentBrowserLocation();
                if (!active) return;
                setCurrentLocation(location);
                setLocationStatus("Using your GPS as the default starting point.");
            } catch (locationError) {
                if (!active) return;
                setLocationStatus("GPS is unavailable. You can still search and enter a manual route start.");
            }
        }

        hydrateLocation();
        return () => {
            active = false;
        };
    }, [currentLocation, setCurrentLocation]);

    useEffect(() => {
        if (!canUseChat) {
            setPlaces([]);
            setRecommendationPlaces([]);
            setHasSearched(false);
            setLoading(false);
            setError(null);
        }
    }, [canUseChat, setRecommendationPlaces]);

    useEffect(() => {
        if (!canUseChat || query.trim()) {
            return;
        }

        let active = true;

        async function hydrateSuggestions() {
            try {
                setLoading(true);
                setError(null);

                const data = await fetchRecommendations({
                    latitude: currentLocation?.lat,
                    longitude: currentLocation?.lng,
                });
                if (!active) return;
                const items = data.items ?? [];
                setPlaces(items);
                setRecommendationPlaces(items);
                setHasSearched(false);
            } catch (err) {
                if (!active) return;
                console.error(err);
                setError("Suggestions are unavailable right now. Please try again.");
                setPlaces([]);
                setRecommendationPlaces([]);
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        }

        hydrateSuggestions();
        return () => {
            active = false;
        };
    }, [
        canUseChat,
        currentLocation,
        query,
        setRecommendationPlaces,
    ]);

    // Logic gốc: Tìm kiếm theo từ khóa
    async function handleSearch() {
        if (!canUseChat) return;
        if (!query.trim()) {
            await loadSuggestions();
            return;
        }

        try {
            setHasSearched(true);
            setLoading(true);
            setError(null);

            const data = await fetchRecommendations({
                query,
                latitude: currentLocation?.lat,
                longitude: currentLocation?.lng,
            });
            const items = data.items ?? [];
            setPlaces(items);
            setRecommendationPlaces(items);

            // UX: Cuộn mượt mà xuống phần kết quả sau khi gọi API
            if (resultsRef.current) {
                resultsRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        } catch (err) {
            console.error(err);
            setError("Search failed. Please try again.");
            setPlaces([]);
            setRecommendationPlaces([]);
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
                    {locationStatus ? (
                        <p
                            style={{
                                margin: "0 auto 20px auto",
                                maxWidth: "560px",
                                color: "var(--color-text)",
                                fontWeight: 600,
                            }}
                        >
                            {locationStatus}
                        </p>
                    ) : null}

                    <div style={{ 
                        boxShadow: "0 20px 40px -10px rgba(37, 99, 235, 0.15)", 
                        borderRadius: "16px" 
                    }}>
                        <SearchBar
                            value={query}
                            onChange={setQuery}
                            onSubmit={handleSearch}
                            disabled={!canUseChat}
                        />
                    </div>
                    {!canUseChat && (
                        <div
                            className="card"
                            style={{
                                marginTop: "16px",
                                textAlign: "left",
                                background: "rgba(255, 255, 255, 0.86)"
                            }}
                        >
                            <h3 style={{ marginBottom: "8px" }}>Profile required for AI chat</h3>
                            <p style={{ marginBottom: "12px" }}>
                                Complete your account profile before using the recommendation chat/search.
                            </p>
                            <p style={{ marginBottom: 0 }}>
                                {isAuthenticated ? (
                                    <Link to="/profile" style={{ color: "var(--color-primary)", fontWeight: 700 }}>
                                        Complete profile
                                    </Link>
                                ) : (
                                    <Link to="/login" style={{ color: "var(--color-primary)", fontWeight: 700 }}>
                                        Sign in to continue
                                    </Link>
                                )}
                            </p>
                        </div>
                    )}
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
                title={hasSearched ? "Search Results" : "Suggestion"}
                subtitle={
                    !canUseChat
                        ? "Complete your profile to unlock AI recommendations"
                        : !hasSearched && !loading && !error && places.length > 0
                        ? "Default suggestions are generated from your address, saved places, picks, and recent searches."
                        : !hasSearched
                        ? "Default suggestions are generated from your address and your recent activity."
                        : !loading && !error && places.length > 0 
                        ? `Found ${places.length} amazing places` 
                        : "No places matched your current query."
                }
            >
                {!canUseChat && (
                    <div className="card" style={{ display: "grid", gap: "12px" }}>
                        <h3 style={{ marginBottom: 0 }}>Recommendations are locked</h3>
                        <p style={{ marginBottom: 0 }}>
                            Finish your profile first, then the AI chat and recommendation results will be available here.
                        </p>
                    </div>
                )}

                {canUseChat && !hasSearched && !loading && !error ? (
                    <div className="card" style={{ display: "grid", gap: "12px" }}>
                        <h3 style={{ marginBottom: 0 }}>Suggestion</h3>
                        <p style={{ marginBottom: 0 }}>
                            We generate suggestions near your profile address first, then learn from the places you save, pick, and search. The live map stays on the <strong style={{ color: "var(--color-text)" }}>Map</strong> page.
                        </p>
                    </div>
                ) : null}

                {loading && (
                    <LoadingSpinner message="Finding best places for you..." />
                )}

                {!loading && error && (
                    <Error
                        message={error}
                        onAction={handleSearch}
                    />
                )}

                {canUseChat && !loading && !error && places.length === 0 && (
                    <Empty
                        icon={Compass}
                        title={hasSearched ? "No places found" : "No suggestions yet"}
                        message={
                            hasSearched
                                ? "Try searching for food, cafe, park, or shopping"
                                : "Try allowing GPS or search for a place type like food, park, or mall"
                        }
                    />
                )}

                {canUseChat && !loading && !error && places.length > 0 && (
                    <div className="fade-in-delay-1">
                        <RecommendationList places={places} />
                    </div>
                )}
            </Section>
        </div>
    );
}
