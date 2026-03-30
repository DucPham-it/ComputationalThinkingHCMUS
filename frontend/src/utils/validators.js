/**
 * Return true when value is empty after trimming.
 */
export function isEmpty(value) {
  return !String(value ?? "").trim();
}
