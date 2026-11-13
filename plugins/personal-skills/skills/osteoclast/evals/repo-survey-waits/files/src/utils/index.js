export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function chunk(items, size) {
  const out = [];
  for (let i = 0; i < items.length; i += size) {
    out.push(items.slice(i, i + size));
  }
  return out;
}

export function isNil(value) {
  return value === null || value === undefined;
}

export function deepClone(value) {
  if (Array.isArray(value)) {
    return value.map(deepClone);
  }
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, inner]) => [key, deepClone(inner)]));
  }
  return value;
}

export function debounce(fn, wait) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
}

export function unique(items) {
  return [...new Set(items)];
}
