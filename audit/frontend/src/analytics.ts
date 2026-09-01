type AnalyticsValue = string | number | boolean | undefined;

type AnalyticsParams = Record<string, AnalyticsValue>;

declare global {
  interface Window {
    dataLayer?: Array<Record<string, AnalyticsValue>>;
  }
}

const PAGE_TYPE = 'audit';

function auditScreen(pathname: string): string {
  if (pathname === '/') return 'new_audit';
  if (/^\/audit\/[^/]+\/decisions\/[^/]+$/.test(pathname)) return 'decision_detail';
  if (/^\/audit\/[^/]+\/gaps$/.test(pathname)) return 'governance_gaps';
  if (/^\/audit\/[^/]+$/.test(pathname)) return 'audit_overview';
  return 'unknown';
}

function push(event: string, params: AnalyticsParams = {}): void {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event, page_type: PAGE_TYPE, ...params });
}

export function trackAuditScreen(pathname: string): void {
  const screen = auditScreen(pathname);
  push('audit_screen_view', { audit_screen: screen, page_path: `/audit/workspace/#${pathname}` });
}

export function trackAuditEvent(event: string, params: AnalyticsParams = {}): void {
  push(event, params);
}

function ctaDestination(element: HTMLElement): string | undefined {
  const href = element.getAttribute('href');
  if (!href) return undefined;

  try {
    const destination = new URL(href, window.location.href);
    if (destination.origin !== window.location.origin) return destination.origin + destination.pathname;
    return auditScreen(destination.hash.replace(/^#/, '') || '/');
  } catch {
    return undefined;
  }
}

export function installCtaTracking(): () => void {
  const onClick = (event: MouseEvent) => {
    const target = event.target;
    if (!(target instanceof Element)) return;
    const control = target.closest<HTMLElement>('[data-cta-intent]');
    if (!control) return;

    push('cta_click', {
      cta_intent: control.dataset.ctaIntent,
      cta_position: control.dataset.ctaPosition,
      cta_component: control.dataset.ctaComponent || 'audit_app',
      cta_destination: ctaDestination(control),
    });
  };

  document.addEventListener('click', onClick, true);
  return () => document.removeEventListener('click', onClick, true);
}
