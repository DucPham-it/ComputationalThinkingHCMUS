import { useEffect, useState } from "react";
import SearchBar from "../components/common/SearchBar";
import FilterPanel from "../components/recommendation/FilterPanel";
import RankingPanel from "../components/recommendation/RankingPanel";
import RecommendationList from "../components/recommendation/RecommendationList";
import { fetchRecommendations } from "../services/placeService";

/**
 * Home page.
 *
 * Input sources:
 * - search text entered by user
 * - later: browser GPS, filters, time, budget, category
 *
 * Output:
 * - recommendation list UI
 */
export default function Home() {
  const [query, setQuery] = useState("");
  const [places, setPlaces] = useState([]);

  useEffect(() => {
    loadRecommendations();
  }, []);

  async function loadRecommendations() {
    try {
      const data = await fetchRecommendations({ query: "" });
      setPlaces(data.items ?? []);
    } catch (error) {
      console.error(error);
    }
  }

  async function handleSearch() {
    try {
      const data = await fetchRecommendations({ query });
      setPlaces(data.items ?? []);
    } catch (error) {
      console.error(error);
    }
  }

  return (
    <div className="grid">
      <h1>Discover travel destinations</h1>
      <SearchBar value={query} onChange={setQuery} onSubmit={handleSearch} />
      <FilterPanel />
      <RankingPanel />
      <RecommendationList places={places} />
    </div>
  );
}
