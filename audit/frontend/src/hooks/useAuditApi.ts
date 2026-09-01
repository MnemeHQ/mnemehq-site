import { useState, useCallback } from 'react';
import type { AuditResult, NewAuditRequest, ApiResponse } from '../types/audit';

// API base is configurable via VITE_API_BASE env var
// - unset → same-origin "/api/..." (production default)
// - dev/staging → configurable host (e.g., "http://localhost:8001")
// Convention: VITE_API_BASE should NOT include trailing slash
const API_BASE = (import.meta.env.VITE_API_BASE ?? '').replace(/\/$/, '');

const STORAGE_PREFIX = 'mneme_audit_';

function getStoredAudit(id: string): AuditResult | null {
  try {
    const raw = sessionStorage.getItem(`${STORAGE_PREFIX}${id}`);
    if (raw) return JSON.parse(raw);
  } catch {
    // ignore storage error
  }
  return null;
}

function storeAudit(audit: AuditResult): void {
  try {
    sessionStorage.setItem(`${STORAGE_PREFIX}${audit.id}`, JSON.stringify(audit));
  } catch {
    // ignore storage error
  }
}

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

    try {
      const response = await fetch(`${API_BASE}/api/audit`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json().catch(() => ({}));
      setLoading(false);
      
      if (!response.ok) {
        const message = data.error || data.detail || `Failed to create audit (HTTP ${response.status})`;
        setError(message);
        return { success: false as const, error: message };
      }
      
      const auditResult = data as AuditResult;
      storeAudit(auditResult);
      return { success: true as const, data: auditResult };
    } catch (err) {
      setLoading(false);
      const msg = err instanceof Error ? err.message : 'Network error';
      setError(msg);
      return { success: false as const, error: msg };
    }
  }, []);

  const getAudit = useCallback(async (id: string) => {
    // 1. Check local session cache first
    const cached = getStoredAudit(id);
    if (cached) {
      return { success: true as const, data: cached };
    }

    setLoading(true);
    setError(null);
    const result = await fetchApi<AuditResult>(`/api/audit/${id}`);
    setLoading(false);
    if (!result.success) {
      setError(result.error ?? 'Unknown error');
    } else if (result.data) {
      storeAudit(result.data);
    }
    return result;
  }, []);

  const exportAudit = useCallback(async (id: string, format: 'markdown' | 'json' = 'markdown') => {
    const response = await fetch(`${API_BASE}/api/audit/${id}/export?format=${format}`);
    if (!response.ok) throw new Error('Export failed');
    return response.blob();
  }, []);

  return { createAudit, getAudit, exportAudit, loading, error };
}
