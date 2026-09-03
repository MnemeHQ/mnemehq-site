import { useState, useCallback } from 'react';
import type {
  ProtectionAuditResponse,
  ProtectionSummary,
  NewAuditRequest,
  ApiResponse,
  Project,
  ProjectWithHistory,
  ProjectAudit,
  AuditComparison,
  CreateProjectRequest,
  RunAuditRequest,
  UpdateProjectRequest,
  ProjectLifecycle,
} from '../types/audit';

const API_BASE = (import.meta.env.VITE_API_BASE ?? '').replace(/\/$/, '');

const STORAGE_PREFIX = 'mneme_audit_';

function getStoredAudit(id: string): ProtectionAuditResponse | null {
  try {
    const raw = sessionStorage.getItem(`${STORAGE_PREFIX}${id}`);
    if (raw) return JSON.parse(raw);
  } catch {
    // ignore storage error
  }
  return null;
}

function storeAudit(audit: ProtectionAuditResponse): void {
  try {
    sessionStorage.setItem(`${STORAGE_PREFIX}${audit.audit_id}`, JSON.stringify(audit));
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
      return { success: false, error: data.error || data.detail || `HTTP ${response.status}` };
    }
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : 'Network error' };
  }
}

function toLegacyAudit(p12: ProtectionAuditResponse) {
  const decisions = p12.decisions.map((d) => {
    let governability: 'enforceable' | 'partial' | 'guidance';
    switch (d.protection_classification) {
      case 'Protected':
        governability = 'enforceable';
        break;
      case 'Mneme-ready':
      case 'Requires modelling':
        governability = 'partial';
        break;
      default:
        governability = 'guidance';
    }

    let confidence = 0.9;
    if (d.evidence_confidence === 'medium') confidence = 0.6;
    else if (d.evidence_confidence === 'low') confidence = 0.3;

    return {
      id: d.id,
      title: d.title,
      summary: d.summary,
      requirement: d.requirement,
      source: d.source,
      governability,
      appliesTo: d.applies_to,
      proposedRule: d.proposed_rule ? {
        type: d.proposed_rule.type,
        pattern: d.proposed_rule.pattern,
        description: d.proposed_rule.description,
      } : null,
      confidence,
    };
  });

  const summary = p12.summary;
  const enforceable = decisions.filter(d => d.governability === 'enforceable').length;
  const partial = decisions.filter(d => d.governability === 'partial').length;
  const guidance = decisions.filter(d => d.governability === 'guidance').length;
  const total = decisions.length;
  const coverage = total > 0 ? Math.round(((enforceable + partial * 0.5) / total) * 100) : 0;

  return {
    id: p12.audit_id,
    repository: p12.repository,
    repositoryUrl: p12.repository_url,
    createdAt: p12.timestamp,
    summary: {
      totalDecisions: total,
      enforceable,
      partial,
      guidance,
      coverage,
      sources: summary.sources,
    },
    decisions,
    gaps: [],
  };
}

export function useAuditApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // --- Legacy ephemeral audit API ---
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

      const data = await response.json();
      setLoading(false);

      if (!response.ok) {
        setError(data.error || 'Failed to create audit');
        return { success: false as const, error: data.error };
      }

      const p12Result = data as ProtectionAuditResponse;
      storeAudit(p12Result);
      return { success: true as const, data: p12Result };
    } catch (err) {
      setLoading(false);
      const msg = err instanceof Error ? err.message : 'Network error';
      setError(msg);
      return { success: false as const, error: msg };
    }
  }, []);

  const getAudit = useCallback(async (id: string) => {
    const cached = getStoredAudit(id);
    if (cached) {
      return { success: true as const, data: cached };
    }

    setLoading(true);
    setError(null);
    const result = await fetchApi<ProtectionAuditResponse>(`/api/audit/${id}`);
    setLoading(false);
    if (!result.success) {
      setError(result.error ?? 'Unknown error');
    } else if (result.data) {
      storeAudit(result.data);
    }
    return result;
  }, []);

  const getAuditLegacy = useCallback(async (id: string) => {
    const result = await getAudit(id);
    if (result.success && result.data) {
      return { success: true as const, data: toLegacyAudit(result.data) };
    }
    return { success: false as const, error: result.error };
  }, [getAudit]);

  const exportAudit = useCallback(async (id: string, format: 'markdown' | 'json' = 'markdown') => {
    const response = await fetch(`${API_BASE}/api/audit/${id}/export?format=${format}`);
    if (!response.ok) throw new Error('Export failed');
    return response.blob();
  }, []);

  // --- M1 Persistence API ---
  const createProject = useCallback(async (request: CreateProjectRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchApi<{ id: string; slug: string; lifecycle: ProjectLifecycle }>(
        '/api/v1/projects',
        {
          method: 'POST',
          body: JSON.stringify(request),
        }
      );
      setLoading(false);
      if (!result.success) setError(result.error ?? 'Failed to create project');
      return result;
    } catch (err) {
      setLoading(false);
      const msg = err instanceof Error ? err.message : 'Network error';
      setError(msg);
      return { success: false as const, error: msg };
    }
  }, []);

  const getProject = useCallback(async (projectId: string) => {
    setLoading(true);
    setError(null);
    const result = await fetchApi<ProjectWithHistory>(`/api/v1/projects/${projectId}`);
    setLoading(false);
    if (!result.success) setError(result.error ?? 'Unknown error');
    return result;
  }, []);

  const listProjects = useCallback(async (lifecycle?: ProjectLifecycle, limit = 50, offset = 0) => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    if (lifecycle) params.set('lifecycle', lifecycle);
    params.set('limit', String(limit));
    params.set('offset', String(offset));
    const result = await fetchApi<Project[]>(`/api/v1/projects?${params.toString()}`);
    setLoading(false);
    if (!result.success) setError(result.error ?? 'Unknown error');
    return result;
  }, []);

  const updateProject = useCallback(async (projectId: string, request: UpdateProjectRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchApi<ProjectWithHistory>(
        `/api/v1/projects/${projectId}`,
        {
          method: 'PATCH',
          body: JSON.stringify(request),
        }
      );
      setLoading(false);
      if (!result.success) setError(result.error ?? 'Failed to update project');
      return result;
    } catch (err) {
      setLoading(false);
      const msg = err instanceof Error ? err.message : 'Network error';
      setError(msg);
      return { success: false as const, error: msg };
    }
  }, []);

  const runProjectAudit = useCallback(async (projectId: string, request: RunAuditRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchApi<{ id: string; status: string; commit_sha: string; mneme_version: string; schema_version: number }>(
        `/api/v1/projects/${projectId}/audits`,
        {
          method: 'POST',
          body: JSON.stringify(request),
        }
      );
      setLoading(false);
      if (!result.success) setError(result.error ?? 'Failed to run audit');
      return result;
    } catch (err) {
      setLoading(false);
      const msg = err instanceof Error ? err.message : 'Network error';
      setError(msg);
      return { success: false as const, error: msg };
    }
  }, []);

  const getProjectAudit = useCallback(async (auditId: string) => {
    setLoading(true);
    setError(null);
    const result = await fetchApi<{
      id: string;
      project_id: string;
      status: string;
      trigger_type: string;
      source_ref: string | null;
      commit_sha: string;
      mneme_version: string;
      schema_version: number;
      result: ProtectionAuditResponse;
      summary: ProtectionSummary;
      started_at: string;
      completed_at: string | null;
      created_at: string;
    }>(`/api/v1/audits/${auditId}`);
    setLoading(false);
    if (!result.success) setError(result.error ?? 'Unknown error');
    return result;
  }, []);

  const listProjectAudits = useCallback(async (projectId: string, limit = 50, offset = 0) => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    params.set('limit', String(limit));
    params.set('offset', String(offset));
    const result = await fetchApi<ProjectAudit[]>(`/api/v1/projects/${projectId}/audits?${params.toString()}`);
    setLoading(false);
    if (!result.success) setError(result.error ?? 'Unknown error');
    return result;
  }, []);

  const compareAudits = useCallback(async (projectId: string, currentAuditId?: string) => {
    setLoading(true);
    setError(null);
    const params = currentAuditId ? `?current_audit_id=${currentAuditId}` : '';
    const result = await fetchApi<AuditComparison>(`/api/v1/projects/${projectId}/compare${params}`);
    setLoading(false);
    if (!result.success) setError(result.error ?? 'Unknown error');
    return result;
  }, []);

  return {
    // Legacy
    createAudit,
    getAudit,
    getAuditLegacy,
    exportAudit,
    // M1 Persistence
    createProject,
    getProject,
    listProjects,
    updateProject,
    runProjectAudit,
    getProjectAudit,
    listProjectAudits,
    compareAudits,
    loading,
    error,
  };
}