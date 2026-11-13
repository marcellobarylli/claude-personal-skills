// Only http(s) URLs can be checked; anchors, mailto: and relative paths are skipped.
export function isCheckable(link) {
  let url;
  try {
    url = new URL(link);
  } catch {
    return false;
  }
  return url.protocol === 'http:' || url.protocol === 'https:';
}
