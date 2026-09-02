import type { AuditResult } from '../types/audit';

export const PILOT_CONTEXT_KEY = 'mneme_pilot_context';

export interface PilotAuditContext {
  auditId: string;
  repository: string;
  totalItems: number;
  enforceable: number;
  partial: number;
  guidance: number;
  coverage: number;
  topGaps: string[];
  selectedDecisionId?: string;
  createdAt: string;
}

export function buildPilotContext(audit: AuditResult, selectedDecisionId?: string): PilotAuditContext {
  return {
    auditId: audit.id,
    repository: audit.repository,
    totalItems: audit.summary.totalDecisions,
    enforceable: audit.summary.enforceable,
    partial: audit.summary.partial,
    guidance: audit.summary.guidance,
    coverage: audit.summary.coverage,
    topGaps: audit.gaps.slice(0, 3).map((gap) => `${gap.decision}: ${gap.suggestedNextStep}`),
    selectedDecisionId,
    createdAt: audit.createdAt,
  };
}

export function storePilotContext(audit: AuditResult, selectedDecisionId?: string): void {
  try {
    sessionStorage.setItem(PILOT_CONTEXT_KEY, JSON.stringify(buildPilotContext(audit, selectedDecisionId)));
  } catch {
    // The pilot remains usable if storage is unavailable.
  }
}

export function buildPilotHref(audit: AuditResult): string {
  const params = new URLSearchParams({ source: 'architecture-audit', audit: audit.id });
  if (audit.repository.startsWith('https://github.com/')) params.set('repository', audit.repository);
  return `https://mnemehq.com/pilot/?${params.toString()}`;
}
