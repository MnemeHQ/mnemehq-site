import { useState, useCallback } from 'react';
import type { ApiResponse, AuditComparison, NewAuditRequest, ProjectWithHistory, ProtectionAuditResponse, RunAuditRequest } from '../types/audit';
import { parseAudit, parseComparison } from '../utils/contracts';

// Preserve main's production endpoint fallback. Explicit preview base overrides it.
const configured = import.meta.env.VITE_API_BASE?.trim();
const API_BASE = (configured || (import.meta.env.PROD
  ? 'https://mneme-audit-api-842519822929.us-central1.run.app' : '')).replace(/\/$/, '');

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = data?.error || data?.detail;
    throw new Error(typeof message === 'string' ? message : `Request failed (HTTP ${response.status}). Please retry.`);
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
  const run = useCallback(async <T,>(action: () => Promise<T>): Promise<ApiResponse<T>> => {
    setLoading(true);
    setError(null);
    try { return { success: true, data: await action() }; }
    catch (cause) {
      const message = cause instanceof Error ? cause.message : 'Request failed';
      setError(message);
      return { success: false, error: message };
    } finally { setLoading(false); }
  }, []);

  const createAudit = useCallback((input: NewAuditRequest) => run(async () => {
    const form = new FormData();
    if (input.repositoryUrl) form.append('repository_url', input.repositoryUrl);
    if (input.zipFile) form.append('zip_file', input.zipFile);
    return parseAudit(await request('/api/v1/audit', { method: 'POST', body: form }));
  }), [run]);

  const getProjectAudit = useCallback((id: string) => run(async () => {
    const record = await request<{ id: string; project_id: string; result: ProtectionAuditResponse; summary_payload: ProtectionAuditResponse['summary'] }>(`/api/v1/audits/${encodeURIComponent(id)}`);
    const result = parseAudit({ ...record.result, summary: record.summary_payload });
    if (result.audit_id !== record.id) throw new Error('Audit identity does not match the persisted record.');
    return { ...record, result };
  }), [run]);

  const getAudit = useCallback(async (id: string): Promise<ApiResponse<ProtectionAuditResponse>> => {
    const record = await getProjectAudit(id);
    return record.success ? { success: true, data: record.data!.result } : { success: false, error: record.error };
  }, [getProjectAudit]);

  const getProject = useCallback((id: string) => run(() => request<ProjectWithHistory>(`/api/v1/projects/${encodeURIComponent(id)}`)), [run]);
  const saveBaseline = useCallback((auditId: string) => run(() => request<ProjectWithHistory>('/api/v1/baselines', json({ audit_id: auditId }))), [run]);
  const runProjectAudit = useCallback((id: string, input: RunAuditRequest) => run(() => request<{id: string}>(`/api/v1/projects/${encodeURIComponent(id)}/audits`, json(input))), [run]);
  const compareAudits = useCallback((id: string) => run(async (): Promise<AuditComparison> =>
    parseComparison(await request(`/api/v1/projects/${encodeURIComponent(id)}/compare`))), [run]);
  const exportAudit = useCallback(async (id: string, format: 'markdown' | 'json' = 'markdown') => {
    const response = await fetch(`${API_BASE}/api/v1/audits/${encodeURIComponent(id)}/export?format=${format}`);
    if (!response.ok) throw new Error('Export failed. Please retry.');
    return response.blob();
  }, []);
  return { createAudit, getAudit, getProject, getProjectAudit, saveBaseline, runProjectAudit, compareAudits, exportAudit, loading, error };
}
