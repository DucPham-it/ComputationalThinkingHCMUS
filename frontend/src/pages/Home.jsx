import { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
import { ChevronDown, Compass, LoaderCircle, Sparkles } from "lucide-react";

import Section from "../components/common/Section";
import SearchBar from "../components/common/SearchBar";

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
import LoadingSpinner from "../components/common/LoadingSpinner";
import Error from "../components/common/Error";
import Empty from "../components/common/Empty";

/**
 * Màn hình Home (Trang chủ).
 *
 * Owner:
 * - TV2: Recommendation search/filter UI.
 * *
 * State & Props:
 * - query: string — natural-language query from SearchBar.
 * - filters: object — controlled state from FilterPanel.
 * - places: array — current active recommendations.
 * - loading / error / hasSearched: UI state indicators.
 *
 * Submit Flows:
 * 1. Query only: user inputs text -> handleSearch() -> search with query and current filters.
 * 2. Filter only: user adjusts filters -> handleFilterApply() -> search with query and new filters.
 * 3. Query+Filter: search with both query and filters.
 *
 * Implementation:
 * - Calls fetchRecommendations with query, filters, latitude, and longitude.
 * - Supports pagination (limit, offset, load more) and updates recommendation places in local state and AppContext.
 * - Auto-scrolls to results area when search completes.
 */

const EMPTY_FILTERS = {
  entertainment_type: "",
  budget_level: "",
  companion_type: "",
  start_time: "",
  max_distance_km: "",
  require_open_now: false,
  min_rating: "",
};

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

    // --- Case 1: Query only (SearchBar submit) ---
    async function handleSearch() {
        if (!canUseChat) return;

        const filterPayload = buildRecommendationFilterPayload(filters);
        if (!query.trim() && Object.keys(filterPayload).length === 0) {
            await loadSuggestions();
            return;
        }

        await runRecommendationSearch(query, filterPayload);
    }

    // --- Case 2 & 3: FilterPanel apply (filter only hoặc query + filter) ---
    async function handleFilterApply(filterPayload) {
        await runRecommendationSearch(query, filterPayload);
    }

    // --- Load more suggestions ---
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

    // --- Effects ---
    // Lấy GPS lần đầu
    useEffect(() => {
        let active = true;
        async function hydrateLocation() {
            if (currentLocation) return;
            try {
                const location = await getCurrentBrowserLocation();
                if (!active) return;
                setCurrentLocation(location);
                setLocationStatus("Using your GPS as the default starting point.");
            } catch {
                if (!active) return;
                setLocationStatus("GPS is unavailable. You can still search and enter a manual route start.");
            }
        }
        hydrateLocation();
        return () => { active = false; };
    }, [currentLocation, setCurrentLocation]);

    // Reset khi logout
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

    // Load default suggestions khi vào trang (nếu chưa search)
    useEffect(() => {
        if (!canUseChat || query.trim()) return;

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

  // --- Render ---
  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      {/* HERO BANNER */}
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
        marginBottom: "40px",
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
            backdropFilter: "blur(4px)",
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
            letterSpacing: "-0.03em",
          }}>
            Discover your next <br />
            <span style={{ color: "var(--color-primary)" }}>perfect destination</span>
          </h1>

          <p style={{
            fontSize: "1.1rem",
            color: "var(--color-text-soft)",
            maxWidth: "500px",
            margin: "0 auto 32px auto",
          }}>
            Tell us what you're craving or where you want to explore. We'll curate the best spots just for you.
          </p>

          {locationStatus && (
            <p style={{ margin: "0 auto 20px auto", maxWidth: "560px", color: "var(--color-text)", fontWeight: 600 }}>
              {locationStatus}
            </p>
          )}

          <div style={{ boxShadow: "0 20px 40px -10px rgba(37, 99, 235, 0.15)", borderRadius: "16px" }}>
            <SearchBar
              value={query}
              onChange={setQuery}
              onSubmit={handleSearch}
              disabled={!canUseChat}
            />
          </div>

          {!canUseChat && (
            <div className="card" style={{ marginTop: "16px", textAlign: "left", background: "rgba(255,255,255,0.86)" }}>
              <h3 style={{ marginBottom: "8px" }}>Profile required for AI chat</h3>
              <p style={{ marginBottom: "12px" }}>
                Complete your account profile before using the recommendation chat/search.
              </p>
              <p style={{ marginBottom: 0 }}>
                {isAuthenticated ? (
                  <Link to="/profile" style={{ color: "var(--color-primary)", fontWeight: 700 }}>Complete profile</Link>
                ) : (
                  <Link to="/login" style={{ color: "var(--color-primary)", fontWeight: 700 }}>Sign in to continue</Link>
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
        <div className="section-soft">
          <FilterPanel
            value={filters}
            onChange={setFilters}
            onApply={handleFilterApply}
            disabled={!canUseChat}
          />
        </div>
      </Section>

      {/* Anchor để scroll */}
      <div ref={resultsRef} style={{ scrollMarginTop: "100px" }} />

      {/* DANH SÁCH KẾT QUẢ */}
      <Section 
          title={hasSearched ? "Search Results" : "Suggestions"}
          subtitle={
              !canUseChat
                  ? "Complete your profile to unlock AI recommendations"
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
