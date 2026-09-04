import type { ProtectionAuditResponse } from '../types/audit';

export const PILOT_CONTEXT_KEY = 'mneme_pilot_context';

export interface PilotAuditContext {
  auditId: string;
  repository: string;
  totalItems: number;
  protected: number;
  mnemeReady: number;
  requiresModelling: number;
  guidance: number;
  currentProtection: number;
  topGaps: string[];
  selectedDecisionId?: string;
  createdAt: string;
}

export function buildPilotContext(audit: ProtectionAuditResponse, selectedDecisionId?: string): PilotAuditContext {
  return {
    auditId: audit.audit_id,
    repository: audit.repository,
    totalItems: audit.summary.decisions_discovered,
    protected: audit.summary.protected_count,
    mnemeReady: audit.summary.mneme_ready_count,
    requiresModelling: audit.summary.requires_modelling_count,
    guidance: audit.summary.guidance_count,
    currentProtection: audit.summary.current_protection,
    topGaps: audit.decisions.filter(d => d.protection_classification === 'Requires modelling' || d.protection_classification === 'Mneme-ready')
      .slice(0, 3).map(d => `${d.title}: ${d.protection_classification}`),
    selectedDecisionId,
    createdAt: audit.timestamp,
  };
}

export function storePilotContext(audit: ProtectionAuditResponse, selectedDecisionId?: string): void {
  try {
    sessionStorage.setItem(PILOT_CONTEXT_KEY, JSON.stringify(buildPilotContext(audit, selectedDecisionId)));
  } catch {
    // The pilot remains usable if storage is unavailable.
  }
}

export function buildPilotHref(audit: ProtectionAuditResponse): string {
  const params = new URLSearchParams({ source: 'architecture-audit', audit: audit.audit_id });
  if (audit.repository.startsWith('https://github.com/')) params.set('repository', audit.repository);
  return `https://mnemehq.com/pilot/?${params.toString()}`;
}
