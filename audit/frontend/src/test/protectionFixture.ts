import type { ProtectionAuditResponse, ProtectionDecision } from '../types/audit';

export function decisionFixture(overrides: Partial<ProtectionDecision> = {}): ProtectionDecision {
  return {
    id: 'decision-1', title: 'Project Config: pyproject.toml',
    summary: 'Python project configuration.', requirement: '[project]',
    source: { file: 'pyproject.toml', lines: '1-20' },
    protection_classification: 'Guidance', evidence_confidence: 'low',
    applies_to: [], proposed_rule: null, category: 'config_evidence', ...overrides,
  };
}

export function auditFixture(overrides: Partial<ProtectionAuditResponse> = {}): ProtectionAuditResponse {
  return {
    schema: 'mneme.audit/v1', audit_id: 'audit-1',
    repository: 'https://github.com/example/repo',
    commit_sha: '0123456789abcdef0123456789abcdef01234567',
    mneme_version: '0.6.0', timestamp: '2026-09-01T00:00:00Z',
    summary: {
      decisions_discovered: 1, protection_relevant: 0, protected_count: 0,
      mneme_ready_count: 0, requires_modelling_count: 0, guidance_count: 1,
      current_protection: 0, identified_mneme_potential: 0,
      sources: ['pyproject.toml'], by_category: { config_evidence: 1 },
    },
    decisions: [decisionFixture()], ...overrides,
  };
}
