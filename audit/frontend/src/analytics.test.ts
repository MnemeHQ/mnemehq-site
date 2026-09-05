import { afterEach, describe, expect, it } from 'vitest';
import {
  analyticsEnvironmentAllowed,
  declaredContentSegment,
  initializeAnalytics,
  reportScreen,
  resetAnalyticsStateForTests,
  routeContext,
  sanitizeDestination,
  sanitizeEventParams,
  summaryParams,
} from './analytics';
import { auditFixture } from './test/protectionFixture';

afterEach(() => {
  resetAnalyticsStateForTests();
  document.querySelector('meta[name="mneme:content-segment"]')?.remove();
  document.getElementById('audit-gtm')?.remove();
  delete window.dataLayer;
});

describe('Audit analytics safety contract', () => {
  it('templates every current route without exposing identifiers', () => {
    const contexts = [
      routeContext('/audit/audit-secret'),
      routeContext('/audit/audit-secret/decisions/decision-secret'),
      routeContext('/audit/audit-secret/gaps'),
      routeContext('/project/project-secret'),
      routeContext('/project/project-secret/compare'),
    ];
    const serialized = JSON.stringify(contexts);

    expect(serialized).not.toContain('audit-secret');
    expect(serialized).not.toContain('decision-secret');
    expect(serialized).not.toContain('project-secret');
    expect(contexts.map(value => value?.page_path)).toEqual([
      '/audit/workspace/audit/:auditId',
      '/audit/workspace/audit/:auditId/decisions/:decisionId',
      '/audit/workspace/audit/:auditId/gaps',
      '/audit/workspace/project/:projectId',
      '/audit/workspace/project/:projectId/compare',
    ]);
  });

  it('ignores the legacy redirect route and de-duplicates the canonical screen', () => {
    expect(reportScreen('/audit')).toBe(false);
    expect(reportScreen('/')).toBe(true);
    expect(reportScreen('/')).toBe(false);
    expect(window.dataLayer).toBeUndefined();
  });

  it('fails closed for local, preview, test, and non-production environments', () => {
    const production = { productionBuild: true, enabled: true, hostname: 'mnemehq.com', protocol: 'https:' };
    expect(analyticsEnvironmentAllowed(production)).toBe(true);
    expect(analyticsEnvironmentAllowed({ ...production, productionBuild: false })).toBe(false);
    expect(analyticsEnvironmentAllowed({ ...production, enabled: false })).toBe(false);
    expect(analyticsEnvironmentAllowed({ ...production, hostname: 'localhost' })).toBe(false);
    expect(analyticsEnvironmentAllowed({ ...production, hostname: '127.0.0.1' })).toBe(false);
    expect(analyticsEnvironmentAllowed({ ...production, hostname: 'preview.mnemehq.com' })).toBe(false);
    expect(analyticsEnvironmentAllowed({ ...production, hostname: 'mnemehq.test' })).toBe(false);
    expect(analyticsEnvironmentAllowed({ ...production, protocol: 'http:' })).toBe(false);

    initializeAnalytics();
    expect(document.getElementById('audit-gtm')).toBeNull();
    expect(window.dataLayer).toBeUndefined();
  });

  it('emits only the current backend summary fields without rebuilding scores', () => {
    const summary = auditFixture().summary;
    expect(summaryParams(summary)).toEqual({
      decisions_discovered: 1,
      protection_relevant: 0,
      protected_count: 0,
      mneme_ready_count: 0,
      requires_modelling_count: 0,
      guidance_count: 1,
      current_protection: 0,
      identified_mneme_potential: 0,
    });
    expect(summaryParams(summary)).not.toHaveProperty('enforceable');
    expect(summaryParams(summary)).not.toHaveProperty('partial');
    expect(summaryParams(summary)).not.toHaveProperty('coverage');
    expect(summaryParams(summary)).not.toHaveProperty('gap_count');
  });

  it('keeps canonical CTA attribution while stripping identifiers and pilot query data', () => {
    const route = routeContext('/audit/raw-id')!;
    const params = sanitizeEventParams('cta_click', {
      cta_intent: 'request_pilot',
      cta_position: 'audit_result',
      cta_destination: 'https://mnemehq.com/pilot/?source=architecture-audit&audit=raw-id&repository=private',
      link_text: '  Request   a pilot  ',
    });
    const meta = document.createElement('meta');
    meta.name = 'mneme:content-segment';
    meta.content = 'problem_awareness';
    document.head.appendChild(meta);

    expect(route.source_page).toBe('/audit/workspace/audit/:auditId');
    expect(params).toMatchObject({
      cta_intent: 'request_pilot',
      cta_position: 'audit_result',
      cta_component: 'audit_app',
      cta_destination: 'https://mnemehq.com/pilot/',
      link_text: 'Request a pilot',
    });
    expect(JSON.stringify(params)).not.toContain('raw-id');
    expect(JSON.stringify(params)).not.toContain('private');
    expect(declaredContentSegment()).toBe('problem_awareness');
    expect(sanitizeDestination('/audit/workspace/audit/raw-id')).toBe('https://mnemehq.com/audit/workspace/audit/:auditId');

    expect(sanitizeEventParams('cta_click', {
      cta_intent: 'install_mneme',
      cta_position: 'audit_overview',
      cta_destination: 'https://github.com/MnemeHQ/mneme',
      link_text: 'Install Mneme',
    })).toMatchObject({
      cta_intent: 'install_mneme',
      cta_destination: 'https://github.com/MnemeHQ/mneme',
    });
    expect(sanitizeEventParams('cta_click', {
      cta_intent: 'discuss_pilot',
      cta_position: 'audit_overview',
      cta_destination: 'https://github.com/MnemeHQ/mneme/discussions/categories/pilots?audit=raw-id',
      link_text: 'Discuss a pilot',
    })).toMatchObject({
      cta_intent: 'discuss_pilot',
      cta_destination: 'https://github.com/MnemeHQ/mneme/discussions/categories/pilots',
    });
  });
});
