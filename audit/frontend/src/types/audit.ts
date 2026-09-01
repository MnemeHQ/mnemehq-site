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
  category?: 'architecture_decision' | 'agent_instruction' | 'config_evidence';
}

export interface AuditSummary {
  totalDecisions: number;
  enforceable: number;
  partial: number;
  guidance: number;
  coverage: number;
  sources: string[];
  byCategory?: {
    architecture_decision?: number;
    agent_instruction?: number;
    config_evidence?: number;
  };
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

export interface GovernanceGap {
  decision: string;
  reason: string;
  suggestedNextStep: string;
}

export interface NewAuditRequest {
  repositoryUrl?: string;
  zipFile?: File;
  localPath?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
