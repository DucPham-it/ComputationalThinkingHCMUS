/**
 * Shared helpers for place arrays used by Home, Map, and Route pages.
 */

export function getPlaceKey(place) {
  /**
   * Input:
   * - place: place object from recommendation, search, load-more, or map-pick flow.
   *
   * Output:
   * - stable string key for deduplicating place arrays.
   * - null when the input is empty.
   */
  if (!place) {
    return null;
  }

  const key =
    place.external_place_id ||
    place.place_id ||
    place.id ||
    `${place.name || ""}-${place.address || ""}`;

  return key == null ? null : String(key);
}

export function mergePlacesByKey(...placeGroups) {
  /**
   * Input:
   * - placeGroups: one or more place arrays.
   *
   * Output:
   * - single deduplicated array.
   * - earlier arrays have priority, so a newly selected place can stay at the top.
   */
  const seen = new Set();
  const mergedPlaces = [];

  placeGroups.flatMap((group) => (Array.isArray(group) ? group : [])).forEach((place) => {
    const key = getPlaceKey(place);
    if (!key || seen.has(key)) {
      return;
    }

    seen.add(key);
    mergedPlaces.push(place);
  });

  return mergedPlaces;
}
