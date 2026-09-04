"""
Canonical P1.2 Architecture Protection Classifier.

This is the SINGLE SOURCE OF TRUTH for mapping Mneme's governability assessment
to the P1.2 protection classification. It must not be duplicated elsewhere.

P1.2 Frozen Contract Mapping:
- Protected = deterministic intent WITH VERIFIED existing enforcement (FORBID_LITERAL rules)
- Mneme-ready = deterministic intent WITH concrete safe Mneme guardrail identified
  - Single-term anti-patterns: always enforced as FORBID_LITERAL (concrete guardrail)
  - Multi-term anti-patterns: ONLY when explicit guardrail can be derived safely
- Requires modelling = deterministic intent EXISTS but no safe concrete Mneme guardrail ("no X" constraints, multi-term anti-patterns requiring interpretation)
- Guidance = intent not appropriate for deterministic enforcement

Decision flow:
1. No deterministic intent? → Guidance
2. Verified enforcement exists (FORBID_LITERAL)? → Protected
3. Concrete safe Mneme guardrail exists? → Mneme-ready
4. Deterministic intent but no safe concrete guardrail? → Requires modelling
"""
from __future__ import annotations

from mneme.enforcer import GovernabilityAssessment

from app.models.protection_audit import MnemeRule, ProtectionClassification


def classify_protection(
    assessment: GovernabilityAssessment,
    guardrail: MnemeRule | None = None,
) -> ProtectionClassification:
    """
    Canonical P1.2 protection classification from Mneme governability assessment.

    This is the authoritative mapping. Do not reimplement elsewhere.

    Priority order (highest to lowest):
    1. Protected: FORBID_LITERAL rules (verified enforcement evidence)
    2. Mneme-ready: concrete safe Mneme guardrail identified
       - Single-term anti-patterns: always enforced as FORBID_LITERAL
       - Multi-term anti-patterns: ONLY when explicit safe guardrail exists
    3. Requires modelling: "no X" constraints, or multi-term anti-patterns requiring interpretation
    4. Guidance: no deterministic intent for enforcement
    """
    # Check for deterministic intent first
    has_deterministic_intent = (
        assessment.has_literal_rules
        or assessment.has_single_term_anti_patterns
        or assessment.has_multi_term_anti_patterns
        or assessment.has_no_constraints
    )

    if not has_deterministic_intent:
        return ProtectionClassification.GUIDANCE

    # 1. Protected: VERIFIED existing enforcement (FORBID_LITERAL rules only)
    if assessment.has_literal_rules:
        return ProtectionClassification.PROTECTED

    # 2. Evidence, not a source-type/boolean assertion, makes a decision ready.
    # The adapter extracts this from supported core rules before classification.
    if guardrail is not None:
        MnemeRule.model_validate(guardrail)
        return ProtectionClassification.MNEME_READY

    # 3. Deterministic intent without a serializable safe strategy needs modelling.
    return ProtectionClassification.REQUIRES_MODELLING


def extract_proposed_rule(decision) -> "MnemeRule | None":
    """Extract proposed Mneme rule from decision's typed rules."""
    from app.models.protection_audit import MnemeRule
    from mneme.enforcer import _is_literal_rule, _rule_terms

    # Priority: FORBID_LITERAL rules first (Protected evidence)
    for rule in decision.rules:
        if rule.type == "FORBID_LITERAL":
            return MnemeRule(
                type=rule.type,
                pattern=rule.value,
                description=f"{rule.type}: {rule.value}",
                include_paths=list(rule.include_paths) if rule.include_paths else None,
                exclude_paths=list(rule.exclude_paths) if rule.exclude_paths else [],
            )

    # Single-term anti-patterns (Mneme-ready evidence - concrete guardrail)
    for ap in decision.anti_patterns:
        if _is_literal_rule(ap):
            # Use the core's sole significant literal, not surrounding prose
            # such as "no postgres". Do not guess a token from multi-term intent.
            literal = _rule_terms(ap)[0]
            return MnemeRule(
                type="FORBID_LITERAL",
                pattern=literal,
                description=f"FORBID_LITERAL: {literal}",
            )

    # Multi-term anti-patterns: NO proposed rule returned
    # Caller must explicitly derive guardrail if safe to do so

    return None
