"""
P1.2 Adapter — Serializes Mneme core output to mneme.audit/v1 format.

This adapter handles SERIALIZATION ONLY. All P1.2 classification logic
delegates to the canonical classifier in app.services.p12_classifier.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from uuid import uuid4
from hashlib import sha256
import re

from mneme.enforcer import (
    assess_governability,
    GovernabilityAssessment,
)
from mneme.schemas import Decision
from mneme.pipeline import PipelineResult, ScoredDecision

from app.models.protection_audit import (
    EvidenceConfidence,
    DecisionSource,
    MnemeRule,
    ProtectionDecision,
    ProtectionSummary,
    ProtectionAuditResponse,
    ProtectionClassification,
)
from app.services.p12_classifier import classify_protection, extract_proposed_rule


@dataclass
class P12DecisionInput:
    """Input for creating a P1.2 decision from Mneme data."""
    decision: Decision
    assessment: GovernabilityAssessment
    source_path: str
    source_lines: str


def map_confidence_to_evidence(confidence: float) -> EvidenceConfidence:
    """Map Mneme confidence to evidence confidence."""
    if confidence >= 0.9:
        return EvidenceConfidence.HIGH
    elif confidence >= 0.5:
        return EvidenceConfidence.MEDIUM
    else:
        return EvidenceConfidence.LOW


def build_protection_decision(
    input_data: P12DecisionInput,
) -> ProtectionDecision:
    """Build a P1.2 ProtectionDecision from Mneme decision and assessment."""
    assessment = input_data.assessment
    decision = input_data.decision
    
    # DELEGATE to canonical classifier - single source of truth
    proposed_rule = extract_proposed_rule(decision)
    protection_class = classify_protection(assessment, guardrail=proposed_rule)
    evidence_confidence = map_confidence_to_evidence(assessment.confidence)
    
    return ProtectionDecision(
        id=decision.id,
        title=decision.decision[:100] if len(decision.decision) > 100 else decision.decision,
        summary=decision.rationale[:300] if decision.rationale else decision.decision[:300],
        requirement=decision.decision + ("\n\nRationale: " + decision.rationale if decision.rationale else ""),
        source=DecisionSource(
            file=input_data.source_path or f"docs/adr/{decision.id}.md",
            lines=input_data.source_lines,
        ),
        protection_classification=protection_class,
        evidence_confidence=evidence_confidence,
        applies_to=list(assessment.applicable_paths),
        proposed_rule=proposed_rule,
        category="architecture_decision",
    )


def build_protection_audit_response(
    project_name: str,
    repository_url: Optional[str],
    commit_sha: str,
    mneme_version: str,
    decisions_inputs: List[P12DecisionInput],
    source_files: List[str],
) -> ProtectionAuditResponse:
    """
    Build complete mneme.audit/v1 response from Mneme decisions.
    
    This is the canonical immutable payload for M1.0 persistence.
    """
    # Build protection decisions
    protection_decisions = [
        build_protection_decision(d) for d in decisions_inputs
    ]
    
    # Calculate P1.2 summary counts
    decisions_discovered = len(protection_decisions)
    
    # Protection-relevant = Protected + Mneme-ready + Requires modelling
    # Guidance is EXCLUDED from denominator
    protected_count = sum(
        1 for d in protection_decisions 
        if d.protection_classification == ProtectionClassification.PROTECTED
    )
    mneme_ready_count = sum(
        1 for d in protection_decisions 
        if d.protection_classification == ProtectionClassification.MNEME_READY
    )
    requires_modelling_count = sum(
        1 for d in protection_decisions 
        if d.protection_classification == ProtectionClassification.REQUIRES_MODELLING
    )
    guidance_count = sum(
        1 for d in protection_decisions 
        if d.protection_classification == ProtectionClassification.GUIDANCE
    )
    
    protection_relevant = protected_count + mneme_ready_count + requires_modelling_count
    
    # Derived percentages (reconstructable from counts above)
    current_protection = 0.0
    identified_mneme_potential = 0.0
    if protection_relevant > 0:
        current_protection = protected_count / protection_relevant
        identified_mneme_potential = (protected_count + mneme_ready_count) / protection_relevant
    
    # Category breakdown
    by_category = {}
    for d in protection_decisions:
        cat = d.category
        by_category[cat] = by_category.get(cat, 0) + 1
    
    summary = ProtectionSummary(
        decisions_discovered=decisions_discovered,
        protection_relevant=protection_relevant,
        protected_count=protected_count,
        mneme_ready_count=mneme_ready_count,
        requires_modelling_count=requires_modelling_count,
        guidance_count=guidance_count,
        current_protection=current_protection,
        identified_mneme_potential=identified_mneme_potential,
        sources=sorted(set(source_files)),
        by_category=by_category,
    )
    
    return ProtectionAuditResponse(
        audit_id=str(uuid4()),
        repository=project_name,
        repository_url=repository_url,
        commit_sha=commit_sha,
        mneme_version=mneme_version,
        timestamp=datetime.now(timezone.utc),
        summary=summary,
        decisions=protection_decisions,
    )


def collect_p12_inputs(
    mneme_report,
    loose_adrs: List,
    agent_instructions: List,
    config_files: List,
    repo_path: Path,
) -> List[P12DecisionInput]:
    """
    Collect all decisions and assessments for P1.2 audit.
    
    Mirrors the audit_service sources but produces P1.2 format.
    """
    inputs = []

    def source_id(prefix: str, path: str) -> str:
        source = Path(path)
        if source.is_absolute():
            source = source.relative_to(repo_path)
        normalized = source.as_posix().replace("\\", "/")
        return f"{prefix}_{sha256(normalized.encode()).hexdigest()[:16]}"
    
    # Source 1: Mneme's authoritative ADR import
    for mneme_decision in mneme_report.decisions:
        assessment = assess_governability(mneme_decision)
        source_file = mneme_decision.source_path if mneme_decision.source_path else f"docs/adr/{mneme_decision.id}.md"
        inputs.append(P12DecisionInput(
            decision=mneme_decision,
            assessment=assessment,
            source_path=source_file,
            source_lines="ADR import",
        ))
    
    # Source 2: Loose ADRs
    for loose_adr in loose_adrs:
        from app.services.loose_adr_parser import LooseADRDecision
        if not isinstance(loose_adr, LooseADRDecision):
            continue
            
        constraints = _extract_constraints_for_p12(loose_adr.decision_text)
        anti_pattern_keywords = ["no ", "avoid ", "never ", "prohibit", "forbid", "forbidden",
            "do not ", "don't ", "must not ", "shall not ", "should not ",
            "cannot ", "can't ", "disallow", "prohibited", "disallowed",
            "prevent", "preclude", "block", "ban ", "restrict",]
        anti_patterns = [c for c in constraints if any(p in c.lower() for p in anti_pattern_keywords)]
        other_constraints = [c for c in constraints if c not in anti_patterns]
        
        from app.services.mneme_adapter import mneme_adapter
        assessment = mneme_adapter.assess_governability_from_text(
            decision_text=loose_adr.decision_text,
            rationale=loose_adr.rationale,
            constraints=other_constraints,
            anti_patterns=anti_patterns,
            scope=[],
            decision_id=source_id("loose", loose_adr.source_path),
        )
        
        # Create a Mneme Decision from the loose ADR
        from mneme.schemas import Decision as MnemeDecision
        mneme_decision = MnemeDecision(
            id=assessment.decision_id,
            decision=loose_adr.decision_text,
            rationale=loose_adr.rationale or "",
            scope=[],
            constraints=other_constraints,
            anti_patterns=anti_patterns,
            rules=[],
            source_path=loose_adr.source_path,
        )
        
        inputs.append(P12DecisionInput(
            decision=mneme_decision,
            assessment=assessment,
            source_path=loose_adr.source_path,
            source_lines=loose_adr.source_lines,
        ))
    
    # Source 3: Agent instructions (CLAUDE.md, AGENTS.md)
    for instr in agent_instructions:
        # Supported targets are already discovered independently and deduplicated
        # by the source finder. Do not follow arbitrary includes or invent intent
        # from a wrapper, including when its target is missing or outside the repo.
        if _is_reference_only_instruction(instr['content']):
            continue
        constraints = _extract_constraints_for_p12(instr['content'])
        if not constraints:
            continue
        anti_pattern_keywords = ["no ", "avoid ", "never ", "prohibit", "forbid", "forbidden",
            "do not ", "don't ", "must not ", "shall not ", "should not ",
            "cannot ", "can't ", "disallow", "prohibited", "disallowed",
            "prevent", "preclude", "block", "ban ", "restrict",]
        anti_patterns = [c for c in constraints if any(p in c.lower() for p in anti_pattern_keywords)]
        other_constraints = [c for c in constraints if c not in anti_patterns]
        
        from app.services.mneme_adapter import mneme_adapter
        assessment = mneme_adapter.assess_governability_from_text(
            decision_text="\n".join(constraints[:5]),
            rationale=f"Agent instructions from {instr['name']}",
            constraints=other_constraints,
            anti_patterns=anti_patterns,
            scope=[],
            decision_id=source_id("agent", instr['path']),
        )
        
        from mneme.schemas import Decision as MnemeDecision
        mneme_decision = MnemeDecision(
            id=assessment.decision_id,
            decision="\n".join(constraints[:5]),
            rationale=f"Agent instructions from {instr['name']}",
            scope=[],
            constraints=other_constraints,
            anti_patterns=anti_patterns,
            rules=[],
            source_path=instr['path'],
        )
        
        inputs.append(P12DecisionInput(
            decision=mneme_decision,
            assessment=assessment,
            source_path=instr['path'],
            source_lines=instr['lines'],
        ))
    
    # Source 4: Config files
    for cfg in config_files:
        # Config files are typically guidance in P1.2
        from app.services.mneme_adapter import mneme_adapter
        assessment = mneme_adapter.assess_governability_from_text(
            decision_text=cfg['content'][:500],
            rationale=f"Project config: {cfg['name']}",
            constraints=[],
            anti_patterns=[],
            scope=[],
            decision_id=source_id("config", cfg['path']),
        )
        
        from mneme.schemas import Decision as MnemeDecision
        mneme_decision = MnemeDecision(
            id=assessment.decision_id,
            decision=f"Project Config: {cfg['name']}",
            rationale=f"Project config: {cfg['name']}",
            scope=[],
            constraints=[],
            anti_patterns=[],
            rules=[],
            source_path=cfg['path'],
        )
        
        inputs.append(P12DecisionInput(
            decision=mneme_decision,
            assessment=assessment,
            source_path=cfg['path'],
            source_lines=cfg['lines'],
        ))
    
    return inputs


def _is_reference_only_instruction(text: str) -> bool:
    """Recognize instruction pointers without opening or interpreting their targets."""
    target = r"(?:`?@?[^\s`]+\.md`?|\[[^\]]+\]\([^\s)]+\.md\))"
    pointer = re.compile(
        rf"(?:@[^\s]+|{target}|"
        rf"(?:see|read|follow|use|include|import|refer to|defer to)\s+"
        rf"(?:the\s+)?(?:(?:instructions|guidelines)\s+(?:in|from)\s+)?{target}"
        rf"(?:\s+for\s+(?:all\s+)?(?:instructions|guidelines))?)[.!]?",
        re.IGNORECASE,
    )
    lines = [line.strip() for line in text.splitlines()
             if line.strip() and not line.lstrip().startswith('#')]
    return bool(lines) and all(pointer.fullmatch(line) for line in lines)


def _extract_constraints_for_p12(text: str) -> List[str]:
    """Extract constraint lines from text (same logic as audit_service)."""
    constraints = []
    anti_pattern_keywords = [
        "no ", "avoid ", "never ", "prohibit", "forbid", "forbidden",
        "do not ", "don't ", "must not ", "shall not ", "should not ",
        "cannot ", "can't ", "disallow", "prohibited", "disallowed",
        "prevent", "preclude", "block", "ban ", "restrict",
    ]
    constraint_keywords = [
        "must ", "must not ", "shall ", "shall not ", "should ", "should not ",
        "required", "require ", "requirement",
        "use ", "use only ", "only use ", "only ",
        "enforce", "enforce ", "enforced",
        "constrain", "constrain ", "constrained",
        "only allow ", "allow only ",
    ]
    
    for line in text.split("\n"):
        line = line.strip()
        if len(line) < 20:
            continue
        line_lower = line.lower()
        if any(p in line_lower for p in anti_pattern_keywords):
            constraints.append(line)
        elif any(p in line_lower for p in constraint_keywords):
            constraints.append(line)
    return constraints
