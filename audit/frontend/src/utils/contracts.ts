import type { AuditComparison, ProtectionAuditResponse, ProtectionSummary } from '../types/audit';

const classifications = ['Protected', 'Mneme-ready', 'Requires modelling', 'Guidance'];
const states = ['improved', 'regressed', 'added', 'removed', 'unchanged', 'uncomparable'];
const object = (value: unknown): value is Record<string, any> => !!value && typeof value === 'object';
const text = (value: unknown): value is string => typeof value === 'string' && value.length > 0;
const finite = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value);

// Validate only: no frontend scoring, classification or count reconstruction.
export function validSummary(value: unknown): value is ProtectionSummary {
  return object(value) && ['decisions_discovered', 'protection_relevant', 'protected_count',
    'mneme_ready_count', 'requires_modelling_count', 'guidance_count', 'current_protection',
    'identified_mneme_potential'].every(key => finite(value[key])) && Array.isArray(value.sources);
}

export function parseAudit(value: unknown): ProtectionAuditResponse {
  if (!object(value) || value.schema !== 'mneme.audit/v1' || !text(value.audit_id) ||
    !text(value.repository) || !text(value.commit_sha) || !text(value.mneme_version) ||
    !text(value.timestamp) || !Number.isFinite(Date.parse(value.timestamp)) ||
    !validSummary(value.summary) || !Array.isArray(value.decisions) ||
    !value.decisions.every((d: any) => object(d) && text(d.id) && text(d.title) &&
      text(d.requirement) && typeof d.summary === 'string' && object(d.source) &&
      text(d.source.file) && classifications.includes(d.protection_classification) && Array.isArray(d.applies_to))) {
    throw new Error('The backend returned an incompatible audit. Expected mneme.audit/v1 with complete scores and decisions.');
  }
  return value as ProtectionAuditResponse;
}

export function parseComparison(value: unknown): AuditComparison {
  if (!object(value) || !text(value.baseline_audit_id) || !text(value.current_audit_id) ||
    !text(value.baseline_commit_sha) || !text(value.current_commit_sha) ||
    !object(value.summary) || !states.every(state => finite(value.summary[state])) ||
    !validSummary(value.baseline_summary) || !validSummary(value.current_summary) ||
    !finite(value.current_protection_delta) || !finite(value.identified_mneme_potential_delta) ||
    !Array.isArray(value.decisions) || !value.decisions.every((d: any) =>
      object(d) && text(d.decision_key) && states.includes(d.state) && object(d.details))) {
    throw new Error('The backend returned an incompatible comparison. Its summary or authoritative scores are unavailable.');
  }
  return value as AuditComparison;
}
