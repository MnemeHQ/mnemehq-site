export const ROUTER_BASENAME = import.meta.env.BASE_URL.replace(/\/$/, '') || '/';

export function getLegacyHashRoute(
  hash: string,
  basename = ROUTER_BASENAME,
): string | null {
  if (!hash.startsWith('#/')) return null;

  const route = hash.slice(1);
  const normalizedBase = basename === '/' ? '' : basename.replace(/\/$/, '');
  return route === '/' ? `${normalizedBase}/` : `${normalizedBase}${route}`;
}

export function migrateLegacyHashRoute(): void {
  const cleanPath = getLegacyHashRoute(window.location.hash);
  if (!cleanPath) return;

  window.history.replaceState(
    window.history.state,
    '',
    `${cleanPath}${window.location.search}`,
  );
}
