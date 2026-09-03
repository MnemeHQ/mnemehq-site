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

from app.models.protection_audit import ProtectionClassification


def classify_protection(
    assessment: GovernabilityAssessment,
    has_explicit_guardrail: bool = False,
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

    # 2. Mneme-ready: CONCRETE safe Mneme guardrail identified
    # Single-term anti-patterns = always enforced as FORBID_LITERAL (concrete guardrail)
    if assessment.has_single_term_anti_patterns:
        return ProtectionClassification.MNEME_READY

    # Multi-term anti-patterns: ONLY Mneme-ready if explicit safe guardrail exists
    if assessment.has_multi_term_anti_patterns:
        if has_explicit_guardrail:
            return ProtectionClassification.MNEME_READY
        # No explicit guardrail signal -> Requires modelling
        return ProtectionClassification.REQUIRES_MODELLING

    # 3. Requires modelling: deterministic intent exists but NO safe concrete guardrail
    # "no X" constraints produce WARN only, need formal modelling
    if assessment.has_no_constraints:
        return ProtectionClassification.REQUIRES_MODELLING

    # 4. Guidance: no deterministic intent for enforcement
    return ProtectionClassification.GUIDANCE


def extract_proposed_rule(decision) -> "MnemeRule | None":
    """Extract proposed Mneme rule from decision's typed rules."""
    from app.models.protection_audit import MnemeRule
    from mneme.enforcer import _is_literal_rule

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
            return MnemeRule(
                type="FORBID_LITERAL",
                pattern=ap,
                description=f"FORBID_LITERAL: {ap}",
            )

    # Multi-term anti-patterns: NO proposed rule returned
    # Caller must explicitly derive guardrail if safe to do so

    return None