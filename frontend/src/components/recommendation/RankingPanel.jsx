/**
 * Displays ranking explanation.
 *
 * Intended output:
 * - short explanation of why a place was recommended
 * - score factors such as rating, distance, weather, user habits, favorites similarity
 */
export default function RankingPanel() {
  return (
    <div className="card">
      <h3>Ranking Logic</h3>
      <p>This section can explain score, distance, weather, and user preference.</p>
    </div>
  );
}
