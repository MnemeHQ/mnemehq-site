export type ProtectionClassification = 'Protected' | 'Mneme-ready' | 'Requires modelling' | 'Guidance';

export type EvidenceConfidence = 'high' | 'medium' | 'low';

export interface DecisionSource {
  file: string;
  lines: string;
}

export interface MnemeRule {
  type: string;
  pattern: string;
  description: string;
  include_paths?: string[];
  exclude_paths?: string[];
}

export interface ProtectionDecision {
  id: string;
  title: string;
  summary: string;
  requirement: string;
  source: DecisionSource;
  protection_classification: ProtectionClassification;
  evidence_confidence: EvidenceConfidence;
  applies_to: string[];
  proposed_rule: MnemeRule | null;
  category: string;
}

export interface ProtectionSummary {
  decisions_discovered: number;
  protection_relevant: number;
  protected_count: number;
  mneme_ready_count: number;
  requires_modelling_count: number;
  guidance_count: number;
  current_protection: number;
  identified_mneme_potential: number;
  sources: string[];
  by_category: Record<string, number>;
}

export interface ProtectionAuditResponse {
  schema: string;
  audit_id: string;
  project_id?: string;
  repository: string;
  repository_url?: string | null;
  commit_sha: string;
  mneme_version: string;
  timestamp: string;
  summary: ProtectionSummary;
  decisions: ProtectionDecision[];
}

// M1 Persistence Types
export type ProjectLifecycle = 'ephemeral' | 'saved' | 'pilot';

export type AuditTriggerType = 'initial' | 're_audit' | 'manual';

export type AuditStatus = 'running' | 'completed' | 'failed';

export interface Project {
  id: string;
  name: string;
  slug: string;
  source_type: string;
  source_locator: string;
  default_ref: string | null;
  lifecycle: ProjectLifecycle;
  baseline_audit_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectAudit {
  id: string;
  status: AuditStatus;
  trigger_type: AuditTriggerType;
  commit_sha: string;
  mneme_version: string;
  schema_version: number;
  created_at: string;
  completed_at: string | null;
}

export interface ProjectWithHistory extends Project {
  audits: ProjectAudit[];
}

export type ComparisonState = 'improved' | 'regressed' | 'unchanged' | 'added' | 'removed' | 'uncomparable';

export type SchemaCompatibility = 'compatible' | 'incompatible' | 'unknown';

export interface DecisionComparison {
  decision_key: string;
  baseline_decision: ProtectionDecision | null;
  current_decision: ProtectionDecision | null;
  state: ComparisonState;
  details: Record<string, unknown>;
}

export interface AuditComparison {
  baseline_audit_id: string;
  current_audit_id: string;
  baseline_commit_sha: string;
  current_commit_sha: string;
  baseline_mneme_version: string;
  current_mneme_version: string;
  baseline_schema_version: number;
  current_schema_version: number;
  baseline_schema: string;
  current_schema: string;
  schema_compatibility: SchemaCompatibility;
  decisions: DecisionComparison[];
  summary: Record<string, number>;
  baseline_summary: ProtectionSummary;
  current_summary: ProtectionSummary;
  current_protection_delta: number;
  identified_mneme_potential_delta: number;
}

export interface CreateProjectRequest {
  name: string;
  slug: string;
  source_locator: string;
  source_type?: string;
  default_ref?: string;
}

export interface RunAuditRequest {
  repository_url?: string;
  source_ref?: string;
  trigger_type?: AuditTriggerType;
}

export interface UpdateProjectRequest {
  name?: string;
  lifecycle?: ProjectLifecycle;
  baseline_audit_id?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface NewAuditRequest {
  repositoryUrl?: string;
  zipFile?: File;
  localPath?: string;
}

export interface ExportResponse {
  blob: Blob;
}

// Legacy types (for backward compatibility)
export type Governability = 'enforceable' | 'partial' | 'guidance';

export interface ArchitecturalDecision {
  id: string;
  title: string;
  summary: string;
  requirement: string;
  source: {
    file: string;
    lines: string;
  };
  governability: Governability;
  appliesTo: string[];
  proposedRule: {
    type: string;
    pattern: string;
    description: string;
  } | null;
  confidence: number;
}

export interface AuditSummary {
  totalDecisions: number;
  enforceable: number;
  partial: number;
  guidance: number;
  coverage: number;
  sources: string[];
}

export interface GovernanceGap {
  decision: string;
  reason: string;
  suggestedNextStep: string;
}

export interface AuditResult {
  id: string;
  repository: string;
  repositoryUrl?: string;
  createdAt: string;
  summary: AuditSummary;
  decisions: ArchitecturalDecision[];
  gaps: GovernanceGap[];
}

export interface LegacyApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
