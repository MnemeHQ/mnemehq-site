import { useState, useCallback } from 'react';
import type { AuditResult, NewAuditRequest, ApiResponse } from '../types/audit';

const API_BASE = '/api';

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

    const response = await fetch(`${API_BASE}/audit`, {
      method: 'POST',
      body: formData,
    });
    
    const data = await response.json();
    setLoading(false);
    
    if (!response.ok) {
      setError(data.error || 'Failed to create audit');
      return { success: false as const, error: data.error };
    }
    
    return { success: true as const, data: data as AuditResult };
  }, []);

  const getAudit = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    const result = await fetchApi<AuditResult>(`/audit/${id}`);
    setLoading(false);
    if (!result.success) setError(result.error ?? 'Unknown error');
    return result;
  }, []);

  const exportAudit = useCallback(async (id: string, format: 'markdown' | 'json' = 'markdown') => {
    const response = await fetch(`${API_BASE}/audit/${id}/export?format=${format}`);
    if (!response.ok) throw new Error('Export failed');
    return response.blob();
  }, []);

  return { createAudit, getAudit, exportAudit, loading, error };
}