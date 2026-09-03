"""
P1.2 Architecture Protection Audit Models (mneme.audit/v1)

These models represent the frozen P1.2 semantic contract.
They are distinct from the legacy M0.1 models in app.models.audit.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ProtectionClassification(str, Enum):
    """P1.2 protection classification for a decision."""
    PROTECTED = "Protected"
    MNEME_READY = "Mneme-ready"
    REQUIRES_MODELLING = "Requires modelling"
    GUIDANCE = "Guidance"


class EvidenceConfidence(str, Enum):
    """Evidence confidence level - separate from protection classification."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DecisionSource(BaseModel):
    """Source location of a decision."""
    file: str
    lines: str
    model_config = ConfigDict(extra="allow")


class MnemeRule(BaseModel):
    """A Mneme rule associated with a decision."""
    type: str
    pattern: str
    description: str
    include_paths: Optional[List[str]] = None
    exclude_paths: List[str] = field(default_factory=list)
    model_config = ConfigDict(extra="allow")


class ProtectionDecision(BaseModel):
    """
    A single protection-relevant decision in the P1.2 audit.
    
    This is the scored unit in P1.2.
    """
    id: str
    title: str
    summary: str
    requirement: str
    source: DecisionSource
    protection_classification: ProtectionClassification
    evidence_confidence: EvidenceConfidence
    applies_to: List[str] = field(default_factory=list)
    proposed_rule: Optional[MnemeRule] = None
    category: str = "architecture_decision"
    model_config = ConfigDict(extra="allow")


class ProtectionSummary(BaseModel):
    """
    P1.2 audit summary with reconstructable percentages.
    
    All percentages must be reconstructable from item-level decisions.
    Guidance is excluded from the denominator.
    """
    # Raw counts (source of truth for reconstruction)
    decisions_discovered: int
    protection_relevant: int
    protected_count: int
    mneme_ready_count: int
    requires_modelling_count: int
    guidance_count: int
    
    # Derived percentages (reconstructable from counts above)
    current_protection: float  # Protected / Protection-relevant
    identified_mneme_potential: float  # (Protected + Mneme-ready) / Protection-relevant
    
    # Additional metadata
    sources: List[str] = field(default_factory=list)
    by_category: Dict[str, int] = field(default_factory=dict)
    model_config = ConfigDict(extra="allow")
    
    def __post_init__(self):
        """Validate that percentages match counts."""
        if self.protection_relevant > 0:
            expected_protection = self.protected_count / self.protection_relevant
            expected_potential = (self.protected_count + self.mneme_ready_count) / self.protection_relevant
            # Allow small floating point differences
            assert abs(self.current_protection - expected_protection) < 0.01, \
                f"current_protection {self.current_protection} != {expected_protection}"
            assert abs(self.identified_mneme_potential - expected_potential) < 0.01, \
                f"identified_mneme_potential {self.identified_mneme_potential} != {expected_potential}"
        else:
            assert self.current_protection == 0.0
            assert self.identified_mneme_potential == 0.0


class ProtectionAuditResponse(BaseModel):
    """
    Complete mneme.audit/v1 response.
    
    This is the canonical immutable payload stored in Audit.result_payload.
    """
    schema: str = "mneme.audit/v1"
    audit_id: str
    repository: str
    repository_url: Optional[str] = None
    commit_sha: str
    mneme_version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    summary: ProtectionSummary
    decisions: List[ProtectionDecision]
    model_config = ConfigDict(extra="allow")


# Legacy M0.1 models (kept for backward compatibility reference)
# These are NOT used for P1.2 audits
class LegacyGovernability(str, Enum):
    ENFORCEABLE = "enforceable"
    PARTIAL = "partial"
    GUIDANCE = "guidance"


class LegacyDecisionCategory(str, Enum):
    ARCHITECTURE_DECISION = "architecture_decision"
    AGENT_INSTRUCTION = "agent_instruction"
    CONFIG_EVIDENCE = "config_evidence"


class LegacyProposedRule(BaseModel):
    type: str
    pattern: str
    description: str


class LegacySource(BaseModel):
    file: str
    lines: str


class LegacyArchitecturalDecision(BaseModel):
    id: str
    title: str
    summary: str
    requirement: str
    source: LegacySource
    governability: LegacyGovernability
    appliesTo: List[str] = []
    proposedRule: Optional[LegacyProposedRule] = None
    confidence: float = 0.9
    category: LegacyDecisionCategory = LegacyDecisionCategory.ARCHITECTURE_DECISION


class LegacyGovernanceGap(BaseModel):
    decision: str
    reason: str
    suggestedNextStep: str


class LegacyAuditSummary(BaseModel):
    totalDecisions: int
    enforceable: int
    partial: int
    guidance: int
    coverage: int  # Legacy: (enforceable + partial * 0.5) / total * 100
    sources: List[str]
    byCategory: Dict[str, int] = {}


class LegacyAuditResult(BaseModel):
    """Legacy M0.1 audit result - for migration/compatibility only."""
    id: str
    repository: str
    repositoryUrl: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    summary: LegacyAuditSummary
    decisions: List[LegacyArchitecturalDecision]
    gaps: List[LegacyGovernanceGap]


def create_legacy_audit_result_from_p12(p12_response: ProtectionAuditResponse) -> LegacyAuditResult:
    """
    Create a legacy M0.1 AuditResult from P1.2 response for backward compatibility.
    
    This is a LOSSY conversion - P1.2 semantics don't map 1:1 to M0.1.
    Used only for legacy API compatibility, NOT for persistence.
    """
    decisions = []
    for d in p12_response.decisions:
        # Map P1.2 protection classification to legacy governability
        if d.protection_classification == ProtectionClassification.PROTECTED:
            governability = LegacyGovernability.ENFORCEABLE
        elif d.protection_classification == ProtectionClassification.MNEME_READY:
            governability = LegacyGovernability.PARTIAL
        elif d.protection_classification == ProtectionClassification.REQUIRES_MODELLING:
            governability = LegacyGovernability.PARTIAL
        else:
            governability = LegacyGovernability.GUIDANCE
        
        decisions.append(LegacyArchitecturalDecision(
            id=d.id,
            title=d.title,
            summary=d.summary,
            requirement=d.requirement,
            source=LegacySource(file=d.source.file, lines=d.source.lines),
            governability=governability,
            appliesTo=d.applies_to,
            proposedRule=LegacyProposedRule(
                type=d.proposed_rule.type,
                pattern=d.proposed_rule.pattern,
                description=d.proposed_rule.description
            ) if d.proposed_rule else None,
            confidence=0.9 if d.evidence_confidence == EvidenceConfidence.HIGH else (
                0.6 if d.evidence_confidence == EvidenceConfidence.MEDIUM else 0.3
            ),
            category=LegacyDecisionCategory.ARCHITECTURE_DECISION,
        ))
    
    # Calculate legacy summary
    enforceable = sum(1 for d in decisions if d.governability == LegacyGovernability.ENFORCEABLE)
    partial = sum(1 for d in decisions if d.governability == LegacyGovernability.PARTIAL)
    guidance = sum(1 for d in decisions if d.governability == LegacyGovernability.GUIDANCE)
    total = len(decisions)
    
    coverage = 0
    if total > 0:
        coverage = int(((enforceable + partial * 0.5) / total) * 100)
    
    by_category = {}
    for cat in LegacyDecisionCategory:
        by_category[cat.value] = sum(1 for d in decisions if d.category == cat)
    
    legacy_summary = LegacyAuditSummary(
        totalDecisions=total,
        enforceable=enforceable,
        partial=partial,
        guidance=guidance,
        coverage=coverage,
        sources=p12_response.summary.sources,
        byCategory=by_category,
    )
    
    return LegacyAuditResult(
        id=p12_response.audit_id,
        repository=p12_response.repository,
        repositoryUrl=p12_response.repository_url,
        createdAt=p12_response.timestamp,
        summary=legacy_summary,
        decisions=decisions,
        gaps=[],  # Gaps not directly mappable
    )