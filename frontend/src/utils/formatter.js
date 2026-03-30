/**
 * Format numeric rating for display.
 *
 * Input:
 * - number, null, or undefined
 *
 * Output:
 * - one-decimal string or N/A
 */
export function formatRating(value) {
  if (value === null || value === undefined) {
    return "N/A";
  }
  return Number(value).toFixed(1);
}
