import { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
import { ChevronDown, Coffee, Compass, LoaderCircle, MapPin, Navigation, Sparkles, Utensils, Users } from "lucide-react";

import Section from "../components/common/Section";
import SearchBar from "../components/common/SearchBar";
import LoadingSpinner from "../components/common/LoadingSpinner";
import Empty from "../components/common/Empty";
import Error from "../components/common/Error";

import FilterPanel, {
    EMPTY_RECOMMENDATION_FILTERS,
    buildRecommendationFilterPayload,
} from "../components/recommendation/FilterPanel";
import RecommendationList from "../components/recommendation/RecommendationList";

import { fetchRecommendations, RECOMMENDATION_PAGE_SIZE } from "../services/recommendationService";
import { useAuth } from "../hooks/useAuth";
import { useApp } from "../hooks/useApp";
import { getCurrentBrowserLocation } from "../utils/geolocation";
import { mergePlacesByKey } from "../utils/placeCollection";

const QUICK_PROMPTS = [
    { label: "Cafe chill", query: "cafe chill gần đây", icon: Coffee },
    { label: "Ăn tối ngon", query: "nhà hàng ngon cho buổi tối", icon: Utensils },
    { label: "Đi chơi nhóm", query: "địa điểm đi chơi với bạn bè", icon: Users },
    { label: "Gần tôi", query: "địa điểm thú vị gần tôi", icon: MapPin },
];

/**
 * Màn hình Home (Trang chủ)
 *
 * Owner:
 * - TV2: Recommendation search/filter UI.
 *
 * File input:
 * - User natural-language query from SearchBar.
 * - Controlled FilterPanel state.
 * - Browser GPS/currentLocation from AppContext.
 * - Authentication/profile state from useAuth.
 *
 * File output:
 * - Calls fetchRecommendations with query, filters, latitude, longitude.
 * - Stores returned places and loaded-more pages in local state and AppContext.
 * - Renders loading, empty, error, and RecommendationList states.
 *
 * Implementation:
 * - Query-only, filter-only, and query+filter searches all call the same API.
 * - FilterPanel emits backend-ready payload through buildRecommendationFilterPayload.
 */
export default function Home() {
    const { isAuthenticated, hasCompletedProfile } = useAuth();
    const {
        currentLocation,
        setCurrentLocation,
        setRecommendationPlaces
    } = useApp();
    const [query, setQuery] = useState("");
    const [places, setPlaces] = useState([]);
    const [loading, setLoading] = useState(false);
    const [loadingMore, setLoadingMore] = useState(false);
    const [error, setError] = useState(null);
    const [loadMoreError, setLoadMoreError] = useState(null);
    const [locationStatus, setLocationStatus] = useState("");
    const [filters, setFilters] = useState(EMPTY_RECOMMENDATION_FILTERS);
    const [hasMore, setHasMore] = useState(false);
    const [nextOffset, setNextOffset] = useState(null);
    const [lastSearchParams, setLastSearchParams] = useState(null);
    
    // State UX để đổi tiêu đề khi đã thực hiện tìm kiếm
    const [hasSearched, setHasSearched] = useState(false);
    
    // Ref dùng để tự động cuộn màn hình xuống kết quả tìm kiếm
    const resultsRef = useRef(null);
    const canUseChat = isAuthenticated && hasCompletedProfile;

    function buildLocationParams() {
        const latitude = currentLocation?.latitude ?? currentLocation?.lat;
        const longitude = currentLocation?.longitude ?? currentLocation?.lng;

        return {
            latitude,
            longitude,
        };
    }

    function scrollToResults() {
        if (resultsRef.current) {
            resultsRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }

    async function runRecommendationSearch(nextQuery = query, filterPayload = buildRecommendationFilterPayload(filters)) {
        if (!canUseChat) {
            return;
        }

        const trimmedQuery = nextQuery.trim();
        const hasFilters = Object.keys(filterPayload).length > 0;
        const requestParams = {
            ...(trimmedQuery ? { query: trimmedQuery } : {}),
            ...filterPayload,
            ...buildLocationParams(),
        };

        try {
            setHasSearched(Boolean(trimmedQuery || hasFilters));
            setLoading(true);
            setError(null);
            setLoadMoreError(null);

            const data = await fetchRecommendations({
                ...requestParams,
                limit: RECOMMENDATION_PAGE_SIZE,
                offset: 0,
            });
            const items = data.items ?? [];
            setPlaces(items);
            setRecommendationPlaces(items);
            setHasMore(Boolean(data.has_more));
            setNextOffset(data.next_offset ?? null);
            setLastSearchParams(requestParams);

            if (trimmedQuery || hasFilters) {
                scrollToResults();
            }
        } catch (err) {
            console.error(err);
            setError("Search failed. Please try again.");
            setLoadMoreError(null);
            setPlaces([]);
            setRecommendationPlaces([]);
            setHasMore(false);
            setNextOffset(null);
            setLastSearchParams(null);
        } finally {
            setLoading(false);
        }
    }

    async function loadSuggestions() {
        if (!canUseChat) {
            return;
        }

        await runRecommendationSearch("", {});
        setHasSearched(false);
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
            setLoadingMore(false);
            setError(null);
            setLoadMoreError(null);
            setHasMore(false);
            setNextOffset(null);
            setLastSearchParams(null);
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
                setLoadMoreError(null);

                const requestParams = buildLocationParams();
                const data = await fetchRecommendations({
                    ...requestParams,
                    limit: RECOMMENDATION_PAGE_SIZE,
                    offset: 0,
                });
                if (!active) return;
                const items = data.items ?? [];
                setPlaces(items);
                setRecommendationPlaces(items);
                setHasSearched(false);
                setHasMore(Boolean(data.has_more));
                setNextOffset(data.next_offset ?? null);
                setLastSearchParams(requestParams);
            } catch (err) {
                if (!active) return;
                console.error(err);
                setError("Suggestions are unavailable right now. Please try again.");
                setLoadMoreError(null);
                setPlaces([]);
                setRecommendationPlaces([]);
                setHasMore(false);
                setNextOffset(null);
                setLastSearchParams(null);
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

    async function handleSearch() {
        if (!canUseChat) return;

        const filterPayload = buildRecommendationFilterPayload(filters);
        if (!query.trim() && Object.keys(filterPayload).length === 0) {
            await loadSuggestions();
            return;
        }

        await runRecommendationSearch(query, filterPayload);
    }

    async function handleQuickPrompt(prompt) {
        setQuery(prompt.query);
        await runRecommendationSearch(prompt.query, buildRecommendationFilterPayload(filters));
    }

    async function handleFilterApply(filterPayload) {
        await runRecommendationSearch(query, filterPayload);
    }

    async function handleLoadMore() {
        if (!canUseChat || loadingMore || loading || !hasMore || nextOffset == null) {
            return;
        }

        const requestParams = lastSearchParams ?? {
            ...(query.trim() ? { query: query.trim() } : {}),
            ...buildRecommendationFilterPayload(filters),
            ...buildLocationParams(),
        };

        try {
            setLoadingMore(true);
            setLoadMoreError(null);

            const data = await fetchRecommendations({
                ...requestParams,
                limit: RECOMMENDATION_PAGE_SIZE,
                offset: nextOffset,
            });
            const incomingItems = data.items ?? [];

            setPlaces((currentPlaces) => {
                const mergedPlaces = mergePlacesByKey(currentPlaces, incomingItems);
                setRecommendationPlaces(mergedPlaces);
                return mergedPlaces;
            });
            setHasMore(Boolean(data.has_more));
            setNextOffset(data.next_offset ?? null);
        } catch (err) {
            console.error(err);
            setLoadMoreError("Could not load more places. Please try again.");
        } finally {
            setLoadingMore(false);
        }
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
            
            {/* HERO BANNER: Giao diện tìm kiếm nổi bật */}
            <section className="hero-panel travel-hero">
                <div className="hero-copy fade-in">
                    <div className="hero-eyebrow">
                        <Sparkles size={16} />
                        <span>Smart Travel Engine</span>
                    </div>
                    
                    <h1 className="hero-title">
                        Find what ever you want to see
                    </h1>
                    
                    {locationStatus ? (
                        <p className="hero-status">
                            {locationStatus}
                        </p>
                    ) : null}

                    <div className="hero-search-card">
                        <SearchBar
                            value={query}
                            onChange={setQuery}
                            onSubmit={handleSearch}
                            disabled={!canUseChat}
                        />
                    </div>
                    <div className="quick-prompt-row" aria-label="Quick searches">
                        {QUICK_PROMPTS.map((prompt) => (
                            <button
                                key={prompt.label}
                                type="button"
                                className="quick-prompt press"
                                onClick={() => handleQuickPrompt(prompt)}
                                disabled={!canUseChat || loading}
                            >
                                <prompt.icon size={16} />
                                <span>{prompt.label}</span>
                            </button>
                        ))}
                    </div>

                    <div className="travel-cockpit" aria-label="Travel cockpit">
                        <div className="cockpit-card">
                            <MapPin size={18} />
                            <span>{currentLocation ? "GPS Ready" : "GPS Pending"}</span>
                        </div>
                        <Link to="/map" className="cockpit-card">
                            <Compass size={18} />
                            <span>Map View</span>
                        </Link>
                        <Link to="/route" className="cockpit-card">
                            <Navigation size={18} />
                            <span>Route</span>
                        </Link>
                        <Link to="/social" className="cockpit-card">
                            <Users size={18} />
                            <span>Social</span>
                        </Link>
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
            >
                <div className="section-soft">
                    <FilterPanel
                        value={filters}
                        onChange={setFilters}
                        onApply={handleFilterApply}
                        disabled={!canUseChat}
                    />
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
                        : !hasSearched
                        ? ""
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
                    <div className="fade-in-delay-1" style={{ display: "grid", gap: "18px" }}>
                        <RecommendationList places={places} />
                        {hasMore ? (
                            <div className="load-more-panel">
                                <span className="load-more-count">
                                    Showing {places.length} places
                                </span>
                                <button
                                    type="button"
                                    className="load-more-button"
                                    onClick={handleLoadMore}
                                    disabled={loadingMore}
                                >
                                    {loadingMore ? (
                                        <LoaderCircle className="load-more-icon spin" size={18} />
                                    ) : (
                                        <ChevronDown className="load-more-icon" size={18} />
                                    )}
                                    <span>{loadingMore ? "Loading..." : "Load more places"}</span>
                                </button>
                                {loadMoreError ? (
                                    <p className="load-more-error">
                                        {loadMoreError}
                                    </p>
                                ) : null}
                            </div>
                        ) : null}
                    </div>
                )}
            </Section>
        </div>
    );
}
