import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { auditFixture } from '../test/protectionFixture';
import type { AuditComparison } from '../types/audit';
import { useAuditApi } from './useAuditApi';

const { track } = vi.hoisted(() => ({ track: vi.fn() }));
vi.mock('../analytics', async importActual => ({
  ...(await importActual<typeof import('../analytics')>()),
  track,
}));

const audit = auditFixture({
  audit_id: 'audit-private-id',
  project_id: 'project-private-id',
  summary: {
    decisions_discovered: 8,
    protection_relevant: 6,
    protected_count: 2,
    mneme_ready_count: 1,
    requires_modelling_count: 3,
    guidance_count: 2,
    current_protection: 0.25,
    identified_mneme_potential: 0.375,
    sources: ['ADR.md'],
    by_category: { architecture_decision: 8 },
  },
});

const jsonResponse = (value: unknown, status = 200) => new Response(JSON.stringify(value), {
  status,
  headers: { 'Content-Type': 'application/json' },
});

const project = {
  id: 'project-private-id',
  name: 'Private project',
  slug: 'private-project',
  source_type: 'github',
  source_locator: 'https://github.com/example/private',
  default_ref: null,
  lifecycle: 'saved',
  baseline_audit_id: 'audit-private-id',
  created_at: '2026-09-01T00:00:00Z',
  updated_at: '2026-09-01T00:00:00Z',
  audits: [],
};

const comparison: AuditComparison = {
  baseline_audit_id: 'baseline-private-id',
  current_audit_id: 'current-private-id',
  baseline_commit_sha: '1111111111111111111111111111111111111111',
  current_commit_sha: '2222222222222222222222222222222222222222',
  baseline_mneme_version: '0.6.0',
  current_mneme_version: '0.6.1',
  baseline_schema_version: 1,
  current_schema_version: 1,
  baseline_schema: 'mneme.audit/v1',
  current_schema: 'mneme.audit/v1',
  schema_compatibility: 'compatible',
  decisions: [],
  summary: { improved: 2, regressed: 1, unchanged: 3, added: 1, removed: 0, uncomparable: 0 },
  baseline_summary: audit.summary,
  current_summary: audit.summary,
  current_protection_delta: 0.125,
  identified_mneme_potential_delta: -0.25,
};

describe('useAuditApi analytics lifecycle', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    track.mockReset();
  });

  it('completes only a freshly created, canonically validated audit with backend metrics', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(audit)));
    const { result } = renderHook(() => useAuditApi());

    await act(async () => { await result.current.createAudit({ repositoryUrl: audit.repository }, 'repository_url'); });

    expect(track).toHaveBeenCalledWith('audit_start', { input_type: 'repository_url' });
    const complete = track.mock.calls.find(call => call[0] === 'audit_complete');
    expect(complete?.[1]).toMatchObject({
      input_type: 'repository_url',
      decisions_discovered: 8,
      protection_relevant: 6,
      protected_count: 2,
      mneme_ready_count: 1,
      requires_modelling_count: 3,
      guidance_count: 2,
      current_protection: 0.25,
      identified_mneme_potential: 0.375,
    });
    expect(complete?.[1]).not.toHaveProperty('enforceable');
    expect(complete?.[1]).not.toHaveProperty('coverage');
  });

  it('does not complete again when an existing report is loaded or refreshed', async () => {
    const record = { id: audit.audit_id, project_id: audit.project_id, result: audit, summary_payload: audit.summary };
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(record)));
    const { result } = renderHook(() => useAuditApi());

    await act(async () => { await result.current.getAudit(audit.audit_id); });
    await act(async () => { await result.current.getAudit(audit.audit_id); });

    expect(track).not.toHaveBeenCalledWith('audit_complete', expect.anything());
    expect(track).not.toHaveBeenCalledWith('audit_start', expect.anything());
  });

  it('does not complete when a create response fails the canonical contract', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ ...audit, schema: 'legacy.audit/v0' })));
    const { result } = renderHook(() => useAuditApi());

    let response;
    await act(async () => { response = await result.current.createAudit({ repositoryUrl: audit.repository }); });

    expect(response).toMatchObject({ success: false });
    expect(track).toHaveBeenCalledWith('audit_start', { input_type: 'repository_url' });
    expect(track).toHaveBeenCalledWith('audit_error', { stage: 'create', error_code: 'invalid_response' });
    expect(track).not.toHaveBeenCalledWith('audit_complete', expect.anything());
  });

  it('counts a baseline only after confirmed persistence', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(jsonResponse({ error: 'storage unavailable' }, 503))
      .mockResolvedValueOnce(jsonResponse(project));
    vi.stubGlobal('fetch', fetchMock);
    const { result } = renderHook(() => useAuditApi());

    await act(async () => { await result.current.saveBaseline(audit.audit_id); });
    expect(track).not.toHaveBeenCalledWith('audit_baseline_saved', expect.anything());
    expect(track).toHaveBeenCalledWith('audit_error', { stage: 'save_baseline', error_code: 'http_503' });

    track.mockClear();
    await act(async () => { await result.current.saveBaseline(audit.audit_id); });
    expect(track).toHaveBeenCalledWith('audit_baseline_saved');
    expect(track).not.toHaveBeenCalledWith('audit_error', expect.anything());
  });

  it('keeps re-audit success and failure mutually exclusive', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(jsonResponse({ id: 'new-audit-private-id', status: 'completed' }))
      .mockResolvedValueOnce(jsonResponse({ id: 'failed-audit-private-id', status: 'failed' }));
    vi.stubGlobal('fetch', fetchMock);
    const { result } = renderHook(() => useAuditApi());

    await act(async () => { await result.current.runProjectAudit(project.id, { trigger_type: 're_audit' }); });
    expect(track).toHaveBeenCalledWith('audit_reaudit_start');
    expect(track).toHaveBeenCalledWith('audit_reaudit_complete', expect.objectContaining({ duration_ms: expect.any(Number) }));
    expect(track).not.toHaveBeenCalledWith('audit_error', expect.objectContaining({ stage: 're_audit' }));

    track.mockClear();
    await act(async () => { await result.current.runProjectAudit(project.id, { trigger_type: 're_audit' }); });
    expect(track).toHaveBeenCalledWith('audit_reaudit_start');
    expect(track).not.toHaveBeenCalledWith('audit_reaudit_complete', expect.anything());
    expect(track).toHaveBeenCalledWith('audit_error', { stage: 're_audit', error_code: 'unexpected_status' });
  });

  it('reports comparison aggregates exactly as supplied by the backend', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(comparison)));
    const { result } = renderHook(() => useAuditApi());

    await act(async () => { await result.current.compareAudits(project.id); });

    expect(track).toHaveBeenCalledWith('audit_comparison_view', {
      schema_compatibility: 'compatible',
      improved_count: 2,
      regressed_count: 1,
      unchanged_count: 3,
      added_count: 1,
      removed_count: 0,
      uncomparable_count: 0,
      current_protection_delta: 0.125,
      identified_mneme_potential_delta: -0.25,
    });
  });

  it('emits export success only after the response body is read', async () => {
    const blob = new Blob(['audit']);
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, blob: vi.fn().mockRejectedValue(new Error('stream failed')) })
      .mockResolvedValueOnce({ ok: true, status: 200, blob: vi.fn().mockResolvedValue(blob) });
    vi.stubGlobal('fetch', fetchMock);
    const { result } = renderHook(() => useAuditApi());

    await expect(result.current.exportAudit(audit.audit_id, 'json')).rejects.toThrow('stream failed');
    expect(track).not.toHaveBeenCalledWith('audit_export', expect.anything());
    expect(track).toHaveBeenCalledWith('audit_error', { stage: 'export', error_code: 'body_read_failed', format: 'json' });

    track.mockClear();
    await expect(result.current.exportAudit(audit.audit_id, 'markdown')).resolves.toBe(blob);
    expect(track).toHaveBeenCalledWith('audit_export', { format: 'markdown' });
    expect(track).not.toHaveBeenCalledWith('audit_error', expect.anything());
  });
});
