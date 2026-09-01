import { useState, useCallback } from 'react';
import type { AuditResult, NewAuditRequest, ApiResponse } from '../types/audit';
import { trackAuditEvent } from '../analytics';

// API base is configurable via VITE_API_BASE env var
// - unset → same-origin "/api/..." (production default)
// - dev/staging → configurable host (e.g., "http://localhost:8001")
// Convention: VITE_API_BASE should NOT include trailing slash
const API_BASE = (import.meta.env.VITE_API_BASE ?? '').replace(/\/$/, '');

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      ...options,
    });
    const data = await response.json();
    if (!response.ok) {
      return { success: false, error: data.error || `HTTP ${response.status}` };
    }
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : 'Network error' };
  }
}

export function useAuditApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createAudit = useCallback(async (request: NewAuditRequest) => {
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    if (request.repositoryUrl) formData.append('repository_url', request.repositoryUrl);
    if (request.zipFile) formData.append('zip_file', request.zipFile);
    if (request.localPath) formData.append('local_path', request.localPath);

    const inputType = request.source ?? (request.zipFile ? 'zip' : 'repository_url');
    const startedAt = performance.now();
    trackAuditEvent('audit_start', { input_type: inputType });

    try {
      const response = await fetch(`${API_BASE}/api/audit`, {
        method: 'POST',
        body: formData,
      });
      const contentType = response.headers.get('content-type') || '';
      const data = contentType.includes('application/json') ? await response.json() : {};

      if (!response.ok) {
        const message = data.error || `HTTP ${response.status}`;
        trackAuditEvent('audit_error', { stage: 'create', error_code: response.status });
        return { success: false as const, error: message };
      }

      const audit = data as AuditResult;
      trackAuditEvent('audit_complete', {
        input_type: inputType,
        duration_ms: Math.round(performance.now() - startedAt),
        decision_count: audit.summary.totalDecisions,
        enforceable_count: audit.summary.enforceable,
        partial_count: audit.summary.partial,
        guidance_count: audit.summary.guidance,
        gap_count: audit.gaps.length,
      });
      return { success: true as const, data: audit };
    } catch {
      const message = 'Unable to contact the audit service';
      trackAuditEvent('audit_error', { stage: 'create', error_code: 'network_or_invalid_response' });
      return { success: false as const, error: message };
    } finally {
      setLoading(false);
    }
  }, []);

  const getAudit = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    const result = await fetchApi<AuditResult>(`/api/audit/${id}`);
    setLoading(false);
    if (!result.success) {
      setError(result.error ?? 'Unknown error');
      trackAuditEvent('audit_error', { stage: 'load', error_code: 'request_failed' });
    }
    return result;
  }, []);

  const exportAudit = useCallback(async (id: string, format: 'markdown' | 'json' = 'markdown') => {
    try {
      const response = await fetch(`${API_BASE}/api/audit/${id}/export?format=${format}`);
      if (!response.ok) {
        trackAuditEvent('audit_error', { stage: 'export', error_code: response.status, format });
        throw new Error('Export failed');
      }
      trackAuditEvent('audit_export', { format });
      return response.blob();
    } catch (error) {
      if (!(error instanceof Error && error.message === 'Export failed')) {
        trackAuditEvent('audit_error', { stage: 'export', error_code: 'network_error', format });
      }
      throw error;
    }
  }, []);

  return { createAudit, getAudit, exportAudit, loading, error };
}
