from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import uuid
from enum import Enum

Governability = Literal["enforceable", "partial", "guidance"]

class DecisionCategory(str, Enum):
    ARCHITECTURE_DECISION = "architecture_decision"
    AGENT_INSTRUCTION = "agent_instruction"
    CONFIG_EVIDENCE = "config_evidence"

class ProposedRule(BaseModel):
    type: str
    pattern: str
    description: str

class Source(BaseModel):
    file: str
    lines: str

class ArchitecturalDecision(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    summary: str
    requirement: str
    source: Source
    governability: Governability
    appliesTo: List[str] = []
    proposedRule: Optional[ProposedRule] = None
    confidence: float = 0.9
    category: DecisionCategory = DecisionCategory.ARCHITECTURE_DECISION

class GovernanceGap(BaseModel):
    decision: str
    reason: str
    suggestedNextStep: str

class AuditSummary(BaseModel):
    totalDecisions: int
    enforceable: int
    partial: int
    guidance: int
    coverage: int
    sources: List[str]
    byCategory: dict[str, int] = {}

class AuditResult(BaseModel):
    id: str
    repository: str
    repositoryUrl: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    summary: AuditSummary
    decisions: List[ArchitecturalDecision]
    gaps: List[GovernanceGap]

class NewAuditRequest(BaseModel):
    repositoryUrl: Optional[str] = None
    localPath: Optional[str] = None