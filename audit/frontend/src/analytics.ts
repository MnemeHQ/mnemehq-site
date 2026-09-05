import type { AuditComparison, ProtectionDecision, ProtectionSummary } from './types/audit';

type Value = string | number | boolean | null;
type Params = Record<string, Value>;
export type InputType = 'repository_url' | 'zip' | 'demo';
export type Stage = 'create' | 'load_audit' | 'load_project' | 'save_baseline' | 're_audit' | 'compare' | 'export' | 'copy_rule' | 'validation';
export type Event = 'audit_screen_view' | 'cta_click' | 'audit_input_selected' | 'audit_start' |
  'audit_complete' | 'audit_error' | 'audit_baseline_saved' | 'audit_reaudit_start' |
  'audit_reaudit_complete' | 'audit_comparison_view' | 'audit_decision_toggle' |
  'audit_decision_view' | 'audit_rule_copy' | 'audit_export';

declare global { interface Window { dataLayer?: unknown[] } }

const ORIGIN = 'https://mnemehq.com';
const BASE = '/audit/workspace';
const TITLE = 'Architecture Audit | Mneme HQ';
const routes = [
  [/^\/$/, '/', 'new_audit'],
  [/^\/audit\/[^/]+$/, '/audit/:auditId', 'audit_overview'],
  [/^\/audit\/[^/]+\/decisions\/[^/]+$/, '/audit/:auditId/decisions/:decisionId', 'decision_detail'],
  [/^\/audit\/[^/]+\/gaps$/, '/audit/:auditId/gaps', 'governance_gaps'],
  [/^\/project\/[^/]+$/, '/project/:projectId', 'project'],
  [/^\/project\/[^/]+\/compare$/, '/project/:projectId/compare', 'comparison'],
] as const;

export function routeContext(path: string) {
  const normalized = (path.split(/[?#]/)[0].replace(/\/+$/, '') || '/');
  const route = routes.find(([pattern]) => pattern.test(normalized));
  if (!route) return null; // Redirect aliases/unknown URLs emit no intermediate view.
  const pagePath = BASE + route[1];
  return { audit_screen: route[2], page_path: pagePath, page_location: ORIGIN + pagePath,
    page_title: TITLE, source_page: pagePath.replace(/\/+$/, '') };
}

// Gate the GTM bootstrap itself, not only selected events after it has loaded.
// The optional environment flag is an emergency production kill switch.
export function analyticsAllowed(): boolean {
  return analyticsEnvironmentAllowed({
    productionBuild: import.meta.env.PROD,
    enabled: import.meta.env.VITE_AUDIT_GTM_ENABLED !== 'false',
    hostname: window.location.hostname,
    protocol: window.location.protocol,
  });
}

export function analyticsEnvironmentAllowed(environment: {
  productionBuild: boolean;
  enabled: boolean;
  hostname: string;
  protocol: string;
}): boolean {
  return environment.productionBuild && environment.enabled &&
    environment.hostname === 'mnemehq.com' && environment.protocol === 'https:';
}

export function sanitizeDestination(raw: string): string {
  if (!raw) return '';
  try {
    const url = new URL(raw, ORIGIN + BASE + '/');
    if (url.origin === ORIGIN) {
      if (url.pathname === BASE || url.pathname.startsWith(BASE + '/')) {
        const path = url.hash.startsWith('#/') ? url.hash.slice(1) : url.pathname.slice(BASE.length) || '/';
        return routeContext(path)?.page_location || ORIGIN + BASE + '/';
      }
      // Only static CTA destinations; never arbitrary paths, query strings or fragments.
      if (/^\/(docs|pilot|demo|audit)\/?$/.test(url.pathname) || url.pathname === '/docs/quickstart') {
        return ORIGIN + url.pathname;
      }
      return ORIGIN + '/';
    }
    if (url.origin === 'https://github.com') {
      const path = url.pathname.replace(/\/$/, '');
      if (path === '/MnemeHQ/mneme' || path === '/MnemeHQ/mneme/discussions/categories/pilots') {
        return 'https://github.com' + path;
      }
    }
  } catch { /* Unrecognized destinations are omitted. */ }
  return '';
}

const metricKeys = ['decisions_discovered', 'protection_relevant', 'protected_count', 'mneme_ready_count',
  'requires_modelling_count', 'guidance_count', 'current_protection', 'identified_mneme_potential'] as const;
const numericKeys = [...metricKeys, 'duration_ms', 'improved_count', 'regressed_count', 'unchanged_count',
  'added_count', 'removed_count', 'uncomparable_count', 'current_protection_delta', 'identified_mneme_potential_delta'];
const enums: Record<string, readonly string[]> = {
  input_type: ['repository_url', 'zip', 'demo'], selection_method: ['drop', 'file_picker', 'url'],
  stage: ['create', 'load_audit', 'load_project', 'save_baseline', 're_audit', 'compare', 'export', 'copy_rule', 'validation'],
  format: ['markdown', 'json'], protection_classification: ['Protected', 'Mneme-ready', 'Requires modelling', 'Guidance'],
  evidence_confidence: ['high', 'medium', 'low'], rule_type: ['FORBID_LITERAL', 'none'],
  action: ['expand', 'collapse'], schema_compatibility: ['compatible', 'incompatible', 'unknown'],
};
const ctaIntents = ['run_audit', 'try_demo', 'nav_home', 'nav_new_audit', 'nav_github', 'nav_demo', 'back',
  'new_audit', 'retry_audit', 'back_to_audit', 'back_to_overview', 'view_gaps', 'export_markdown', 'export_json',
  'save_baseline', 'install', 'request_pilot', 'pilot', 'view_guardrail', 'review_gap', 'view_all_decisions',
  'view_details', 'show_all', 'review_gap_item', 'private_repo_docs', 'install_mneme', 'discuss_pilot'];
const ctaPositions = ['new_audit', 'audit_nav', 'audit_detail', 'audit_overview', 'audit_summary',
  'decision_detail', 'decision_list', 'decision_group', 'governance_gaps', 'gaps', 'error', 'audit_result'];
const contextKeys = ['audit_screen', 'page_path', 'page_location', 'page_title', 'page_referrer', 'source_page', 'content_segment'];
const parameterKeys = [...numericKeys, ...Object.keys(enums), 'error_code', 'has_proposed_rule',
  'cta_intent', 'cta_position', 'cta_component', 'cta_destination', 'link_text'];
let currentPath: string | undefined;
let previousLocation = '';

function context() {
  const path = currentPath ?? window.location.pathname.slice(BASE.length);
  const view = routeContext(path) || routeContext('/')!;
  return { ...view, page_referrer: previousLocation || sanitizeDestination(document.referrer),
    content_segment: declaredContentSegment() };
}

export function declaredContentSegment(): string | null {
  const segment = document.querySelector('meta[name="mneme:content-segment"]')?.getAttribute('content');
  return segment === 'developer_evaluation' || segment === 'problem_awareness' ? segment : null;
}

function layer() { return window.dataLayer = window.dataLayer || []; }

export function sanitizeEventParams(event: Event, params: Params = {}): Params {
  const safe: Params = {};
  for (const [key, value] of Object.entries(params)) {
    if (numericKeys.includes(key) && typeof value === 'number' && Number.isFinite(value)) safe[key] = value;
    else if (enums[key]?.includes(String(value))) safe[key] = value;
    else if (key === 'has_proposed_rule' && typeof value === 'boolean') safe[key] = value;
    else if (key === 'error_code' && typeof value === 'string' &&
      /^(http_[1-5]\d\d|network_error|invalid_response|body_read_failed|clipboard_unavailable|missing_input|invalid_zip|invalid_repository_url|unexpected_status)$/.test(value)) safe[key] = value;
  }
  // CTA values are collected only from opted-in controls with static labels.
  if (event === 'cta_click' && ctaIntents.includes(String(params.cta_intent))) {
    safe.cta_intent = params.cta_intent;
    safe.cta_position = ctaPositions.includes(String(params.cta_position)) ? params.cta_position : 'audit_result';
    safe.cta_component = 'audit_app';
    safe.cta_destination = sanitizeDestination(String(params.cta_destination || ''));
    safe.link_text = String(params.link_text || '').replace(/\s+/g, ' ').trim().slice(0, 100);
  }
  return safe;
}

export function track(event: Event, params: Params = {}) {
  if (!analyticsAllowed()) return;
  const safe = sanitizeEventParams(event, params);
  // Null clears the v2 data-layer model so an earlier event cannot donate fields.
  const cleared = Object.fromEntries([...parameterKeys, ...contextKeys].map(key => [key, null]));
  layer().push({ ...cleared, event, page_type: 'audit', ...context(), ...safe });
}

export function reportScreen(pathname: string): boolean {
  const view = routeContext(pathname);
  const normalized = pathname.split(/[?#]/)[0].replace(/\/+$/, '') || '/';
  if (!view || currentPath === normalized) return false;
  const prior = currentPath;
  previousLocation = prior ? routeContext(prior)?.page_location || '' : '';
  currentPath = normalized; // Raw router identity stays in memory only, never in the data layer.
  if (!analyticsAllowed()) return true;
  layer().push(['set', context()]);
  track('audit_screen_view');
  return true;
}

export function summaryParams(summary: ProtectionSummary): Params {
  // Project values verbatim. No sums, percentages, ratios or score reconstruction.
  return Object.fromEntries(metricKeys.map(key => [key, summary[key]]));
}

export function decisionParams(decision: ProtectionDecision): Params {
  const validRule = decision.proposed_rule?.type === 'FORBID_LITERAL' && !!decision.proposed_rule.pattern.trim();
  return { protection_classification: decision.protection_classification, evidence_confidence: decision.evidence_confidence,
    has_proposed_rule: !!validRule, rule_type: validRule ? 'FORBID_LITERAL' : 'none' };
}

export function comparisonParams(comparison: AuditComparison): Params {
  return { schema_compatibility: comparison.schema_compatibility || 'unknown',
    ...Object.fromEntries(['improved', 'regressed', 'unchanged', 'added', 'removed', 'uncomparable']
      .map(state => [`${state}_count`, comparison.summary[state]])),
    current_protection_delta: comparison.current_protection_delta,
    identified_mneme_potential_delta: comparison.identified_mneme_potential_delta };
}

export function initializeAnalytics() {
  if (!analyticsAllowed() || document.getElementById('audit-gtm')) return;
  // Sanitize defaults BEFORE any third-party script can initialize a Google tag.
  layer().push(['consent', 'default', { analytics_storage: 'granted', ad_storage: 'denied',
    ad_user_data: 'denied', ad_personalization: 'denied' }]);
  layer().push(['set', { ...context(), send_page_view: false }]);
  layer().push({ 'gtm.start': Date.now(), event: 'gtm.js' });
  const script = document.createElement('script');
  script.id = 'audit-gtm';
  script.async = true;
  script.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-KL7FB67N';
  document.head.appendChild(script);
  document.addEventListener('click', event => {
    const control = event.target instanceof Element ? event.target.closest<HTMLElement>('[data-cta-intent]') : null;
    if (!control || control.matches(':disabled') || control.dataset.ctaIntent === 'copy_rule') return;
    const intent = control.dataset.ctaIntent || '';
    if (!ctaIntents.includes(intent)) return;
    track('cta_click', { cta_intent: intent, cta_position: control.dataset.ctaPosition || 'audit_result',
      cta_destination: control.getAttribute('href') || '', link_text: control.textContent || '' });
  }, true);
}

export function resetAnalyticsStateForTests() {
  currentPath = undefined;
  previousLocation = '';
}
