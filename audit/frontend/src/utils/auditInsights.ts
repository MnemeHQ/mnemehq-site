import type { ArchitecturalDecision } from '../types/audit';

export const FIELD_HELP = {
  requirement: 'The architectural intent or repository evidence Mneme extracted. Review it to confirm the finding reflects what your team intended.',
  appliesTo: 'The repository paths, services, or change types where this decision should apply. Explicit scope is required for safe enforcement.',
  proposedRule: 'A deterministic check Mneme could evaluate before a change is accepted. No proposed rule means more specificity is needed.',
  confidence: 'Mneme’s confidence that the extracted text represents the stated decision. It is not a measure of whether the decision is good.',
  source: 'The file and line range used as evidence. Use this to validate the finding with the decision owner.',
  governability: 'How completely this item can be translated into a deterministic control: enforceable, partial, or guidance only.',
  coverage: 'The percentage of governance items that are at least partially machine-testable. It measures specification readiness, not repository quality.',
} as const;

export interface DecisionRecommendation {
  title: string;
  description: string;
}

export function getDecisionRecommendations(decision: ArchitecturalDecision): DecisionRecommendation[] {
  const recommendations: DecisionRecommendation[] = [];

  if (decision.appliesTo.length === 0) {
    recommendations.push({
      title: 'Define where this applies',
      description: 'Add repository paths, file globs, services, or change types so the control has an explicit and safe scope.',
    });
  }

  if (!decision.proposedRule) {
    recommendations.push({
      title: 'State a machine-testable constraint',
      description: 'Describe the required or forbidden pattern and the condition that should pass or fail. Mneme can then propose a deterministic rule.',
    });
  }

  if (decision.confidence < 0.7) {
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

export function getEvidenceLabel(decision: ArchitecturalDecision): string {
  return decision.category === 'config_evidence' ? 'Detected evidence' : 'Decision requirement';
}

export function getPlainLanguageSummary(decision: ArchitecturalDecision): string {
  if (decision.category === 'config_evidence') {
    return `Mneme found project configuration in ${decision.source.file}. It is useful evidence of how the repository is built or operated, but the file alone does not state a scoped, machine-testable governance rule.`;
  }

  return decision.summary || decision.requirement;
}
