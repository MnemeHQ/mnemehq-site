import type { AuditComparison, ProtectionAuditResponse, ProtectionDecision, ProtectionSummary, ProjectWithHistory } from '../types/audit';

const classifications = ['Protected', 'Mneme-ready', 'Requires modelling', 'Guidance'];
const states = ['improved', 'regressed', 'added', 'removed', 'unchanged', 'uncomparable'];
const object = (value: unknown): value is Record<string, any> => !!value && typeof value === 'object';
const text = (value: unknown): value is string => typeof value === 'string' && value.trim().length > 0;
const identity = (value: unknown): value is string => text(value) && !['undefined', 'null'].includes(value);
const finite = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value);
const strings = (value: unknown): value is string[] => Array.isArray(value) && value.every(text);
const date = (value: unknown) => text(value) && Number.isFinite(Date.parse(value));

// Validate only: no frontend scoring, classification or count reconstruction.
export function validSummary(value: unknown): value is ProtectionSummary {
  return object(value) && ['decisions_discovered', 'protection_relevant', 'protected_count',
    'mneme_ready_count', 'requires_modelling_count', 'guidance_count']
    .every(key => Number.isInteger(value[key]) && value[key] >= 0) &&
    ['current_protection', 'identified_mneme_potential'].every(key => finite(value[key]) && value[key] >= 0 && value[key] <= 1) &&
    strings(value.sources);
}

function validDecision(d: unknown): d is ProtectionDecision {
  if (!object(d) || !identity(d.id) || !text(d.title) || !text(d.requirement) ||
    typeof d.summary !== 'string' || !text(d.category) || !object(d.source) ||
    !text(d.source.file) || typeof d.source.lines !== 'string' ||
    !classifications.includes(d.protection_classification) ||
    !['high', 'medium', 'low'].includes(d.evidence_confidence) || !strings(d.applies_to)) return false;
  const rule = d.proposed_rule;
  if (rule === null) return d.protection_classification !== 'Mneme-ready';
  return object(rule) && rule.type === 'FORBID_LITERAL' && text(rule.pattern) && text(rule.description) &&
    (rule.include_paths == null || strings(rule.include_paths)) &&
    (rule.exclude_paths === undefined || strings(rule.exclude_paths));
}

export function parseAudit(value: unknown): ProtectionAuditResponse {
  if (!object(value) || value.schema !== 'mneme.audit/v1' || !identity(value.audit_id) ||
    !text(value.repository) || !text(value.commit_sha) || !text(value.mneme_version) ||
    !text(value.timestamp) || !Number.isFinite(Date.parse(value.timestamp)) ||
    !validSummary(value.summary) || !Array.isArray(value.decisions) ||
    !value.decisions.every(validDecision)) {
    throw new Error('The backend returned an incompatible audit. Expected mneme.audit/v1 with complete scores and decisions.');
  }
  return value as ProtectionAuditResponse;
}

export function parseComparison(value: unknown): AuditComparison {
  if (!object(value) || !identity(value.baseline_audit_id) || !identity(value.current_audit_id) ||
    !text(value.baseline_commit_sha) || !text(value.current_commit_sha) ||
    !text(value.baseline_mneme_version) || !text(value.current_mneme_version) ||
    !text(value.baseline_schema) || !text(value.current_schema) ||
    !object(value.summary) || !states.every(state => finite(value.summary[state])) ||
    !validSummary(value.baseline_summary) || !validSummary(value.current_summary) ||
    !finite(value.current_protection_delta) || !finite(value.identified_mneme_potential_delta) ||
    !Array.isArray(value.decisions) || !value.decisions.every((d: any) =>
      object(d) && identity(d.decision_key) && states.includes(d.state) && object(d.details) &&
      (d.baseline_decision === null || validDecision(d.baseline_decision)) &&
      (d.current_decision === null || validDecision(d.current_decision)))) {
    throw new Error('The backend returned an incompatible comparison. Its summary or authoritative scores are unavailable.');
  }
  return value as AuditComparison;
}

export function parseProject(value: unknown): ProjectWithHistory {
  if (!object(value) || !identity(value.id) || !text(value.name) || !text(value.source_locator) ||
    !text(value.source_type) || !['ephemeral', 'saved', 'pilot'].includes(value.lifecycle) ||
    !(value.baseline_audit_id === null || identity(value.baseline_audit_id)) ||
    !date(value.created_at) || !date(value.updated_at) || !Array.isArray(value.audits) ||
    !value.audits.every((a: any) => object(a) && identity(a.id) &&
      ['running', 'completed', 'failed'].includes(a.status) && text(a.trigger_type) && date(a.created_at))) {
    throw new Error('The backend returned an incompatible project. Its identity or audit history is unavailable.');
  }
  return value as ProjectWithHistory;
}
