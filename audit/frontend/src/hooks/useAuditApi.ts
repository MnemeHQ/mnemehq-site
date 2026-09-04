import { useState, useCallback } from 'react';
import type { ApiResponse, AuditComparison, NewAuditRequest, ProtectionAuditResponse, RunAuditRequest } from '../types/audit';
import { parseAudit, parseComparison, parseProject } from '../utils/contracts';
import { comparisonParams, summaryParams, track, type InputType, type Stage } from '../analytics';

class RequestFailure extends Error {
  constructor(message: string, readonly analyticsCode: string) { super(message); }
}

// Preserve main's production endpoint fallback. Explicit preview base overrides it.
const configured = import.meta.env.VITE_API_BASE?.trim();
const API_BASE = (configured || (import.meta.env.PROD
  ? 'https://mneme-audit-api-842519822929.us-central1.run.app' : '')).replace(/\/$/, '');

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options).catch(() => {
    throw new RequestFailure('Unable to contact the audit service. Please retry.', 'network_error');
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = data?.error || data?.detail;
    throw new RequestFailure(typeof message === 'string' ? message : `Request failed (HTTP ${response.status}). Please retry.`, `http_${response.status}`);
  }
  if (data === null) throw new Error('The server returned an invalid response. Please retry.');
  return data as T;
}

const json = (body: unknown): RequestInit => ({
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
});

export function useAuditApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const run = useCallback(async <T,>(action: () => Promise<T>, stage: Stage): Promise<ApiResponse<T>> => {
    setLoading(true);
    setError(null);
    try { return { success: true, data: await action() }; }
    catch (cause) {
      const message = cause instanceof Error ? cause.message : 'Request failed';
      setError(message);
      track('audit_error', { stage, error_code: cause instanceof RequestFailure ? cause.analyticsCode : 'invalid_response' });
      return { success: false, error: message };
    } finally { setLoading(false); }
  }, []);

  const createAudit = useCallback((input: NewAuditRequest, inputType: InputType = input.zipFile ? 'zip' : 'repository_url') => run(async () => {
    const form = new FormData();
    if (input.repositoryUrl) form.append('repository_url', input.repositoryUrl);
    if (input.zipFile) form.append('zip_file', input.zipFile);
    const startedAt = performance.now();
    track('audit_start', { input_type: inputType });
    const result = parseAudit(await request('/api/v1/audit', { method: 'POST', body: form }));
    track('audit_complete', { input_type: inputType, duration_ms: Math.round(performance.now() - startedAt), ...summaryParams(result.summary) });
    return result;
  }, 'create'), [run]);

  const getProjectAudit = useCallback((id: string) => run(async () => {
    const record = await request<{ id: string; project_id: string; result: ProtectionAuditResponse; summary_payload: ProtectionAuditResponse['summary'] }>(`/api/v1/audits/${encodeURIComponent(id)}`);
    const result = parseAudit({ ...record.result, summary: record.summary_payload });
    if (result.audit_id !== record.id || record.id !== id) throw new Error('Audit identity does not match the requested persisted record.');
    return { ...record, result };
  }, 'load_audit'), [run]);

  const getAudit = useCallback(async (id: string): Promise<ApiResponse<ProtectionAuditResponse>> => {
    const record = await getProjectAudit(id);
    return record.success ? { success: true, data: record.data!.result } : { success: false, error: record.error };
  }, [getProjectAudit]);

  const getProject = useCallback((id: string) => run(async () => {
    const project = parseProject(await request(`/api/v1/projects/${encodeURIComponent(id)}`));
    if (project.id !== id) throw new Error('Project identity does not match the requested record.');
    return project;
  }, 'load_project'), [run]);
  const saveBaseline = useCallback((auditId: string) => run(async () => {
    const project = parseProject(await request('/api/v1/baselines', json({ audit_id: auditId })));
    if (project.baseline_audit_id !== auditId) throw new Error('Saved baseline does not match the requested audit.');
    if (project.lifecycle === 'saved' || project.lifecycle === 'pilot') track('audit_baseline_saved');
    return project;
  }, 'save_baseline'), [run]);
  const runProjectAudit = useCallback((id: string, input: RunAuditRequest) => run(async () => {
    const startedAt = performance.now();
    track('audit_reaudit_start');
    const record = await request<{id: string; status: string}>(`/api/v1/projects/${encodeURIComponent(id)}/audits`, json(input));
    if (record && typeof record.id === 'string' && record.id.trim() && record.status === 'completed') {
      track('audit_reaudit_complete', { duration_ms: Math.round(performance.now() - startedAt) });
    } else {
      throw new RequestFailure('The re-audit did not complete successfully. Your baseline is unchanged.', 'unexpected_status');
    }
    return record;
  }, 're_audit'), [run]);
  const compareAudits = useCallback((id: string) => run(async (): Promise<AuditComparison> => {
    const comparison = parseComparison(await request(`/api/v1/projects/${encodeURIComponent(id)}/compare`));
    track('audit_comparison_view', comparisonParams(comparison));
    return comparison;
  }, 'compare'), [run]);
  const exportAudit = useCallback(async (id: string, format: 'markdown' | 'json' = 'markdown') => {
    let code = 'network_error';
    try {
      const response = await fetch(`${API_BASE}/api/v1/audits/${encodeURIComponent(id)}/export?format=${format}`);
      code = `http_${response.status}`;
      if (!response.ok) throw new Error('Export failed. Please retry.');
      code = 'body_read_failed';
      const blob = await response.blob();
      track('audit_export', { format });
      return blob;
    } catch (cause) {
      track('audit_error', { stage: 'export', error_code: code, format });
      throw cause;
    }
  }, []);
  return { createAudit, getAudit, getProject, getProjectAudit, saveBaseline, runProjectAudit, compareAudits, exportAudit, loading, error };
}
