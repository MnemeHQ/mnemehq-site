import type { ProtectionDecision } from '../types/audit';

export const FIELD_HELP = {
  requirement: 'The architectural intent or repository evidence Mneme extracted. Review it to confirm the finding reflects what your team intended.',
  appliesTo: 'The repository paths, services, or change types where this decision should apply. Explicit scope is required for safe enforcement.',
  proposedRule: 'The supported deterministic check identified by the backend. Guidance does not require such a check; Requires modelling needs a safe strategy before enforcement can be proposed.',
  confidence: 'Mneme’s confidence that the extracted text represents the stated decision. It is not a measure of whether the decision is good.',
  source: 'The file and line range used as evidence. Use this to validate the finding with the decision owner.',
  protection: 'The backend classifies each decision as Protected, Mneme-ready, Requires modelling, or Guidance based on deterministic enforcement evidence.',
} as const;

export interface DecisionRecommendation {
  title: string;
  description: string;
}

export function getDecisionRecommendations(decision: ProtectionDecision): DecisionRecommendation[] {
  if (decision.protection_classification === 'Guidance') return [{
    title: 'Review this guidance with the decision owner',
    description: 'Keep the intent clear and current. This classification does not call for deterministic enforcement.',
  }];
  const recommendations: DecisionRecommendation[] = [];

  if (decision.applies_to.length === 0) {
    recommendations.push({
      title: 'Define where this applies',
      description: 'Add repository paths, file globs, services, or change types so the control has an explicit and safe scope.',
    });
  }

  if (!decision.proposed_rule) {
    recommendations.push({
      title: 'State a machine-testable constraint',
      description: 'Describe the required or forbidden pattern and the condition that should pass or fail. Mneme can then propose a deterministic rule.',
    });
  }

  if (decision.evidence_confidence === 'low') {
    recommendations.push({
      title: 'Validate the interpretation',
      description: 'Ask the decision owner to confirm the extracted intent or rewrite the source in clearer normative language.',
    });
  }

  if (recommendations.length === 0) {
    recommendations.push({
      title: 'Pilot this control in observe mode',
      description: 'Run the rule without blocking changes first, review false positives with the owning team, then promote it to enforcement.',
    });
  }

  return recommendations;
}

export function getEvidenceLabel(decision: ProtectionDecision): string {
  return decision.category === 'config_evidence' ? 'Detected evidence' : 'Decision requirement';
}

export function getPlainLanguageSummary(decision: ProtectionDecision): string {
  if (decision.category === 'config_evidence') {
    return `Mneme found project configuration in ${decision.source.file}. It is useful evidence of how the repository is built or operated, but the file alone does not state a scoped, machine-testable governance rule.`;
  }

  return decision.summary || decision.requirement;
}
