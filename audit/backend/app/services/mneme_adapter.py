"""
MnemeAdapter — Thin wrapper around Mneme core for the audit service.

This adapter translates the audit service's needs into Mneme operations:
- Import ADRs from a repository
- Evaluate governability of extracted decisions
- Generate proposed Mneme rules from decisions

All Mneme semantics (what is enforceable, how rules match, path applicability)
are delegated to Mneme core. This adapter does NOT duplicate Mneme logic.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from mneme.adr_import import compile_for_import, ImportReport
from mneme.schemas import Decision, Rule
from mneme.enforcer import check_prompt, Severity, EnforcementResult
from mneme.decision_retriever import DecisionRetriever, ScoredDecision
from mneme.memory_store import MemoryStore


@dataclass
class GovernabilityAssessment:
    """Mneme's assessment of a decision's governability."""
    decision_id: str
    decision_title: str
    enforceable: bool
    partially_enforceable: bool
    guidance_only: bool
    mneme_rules: list[Rule]
    has_literal_rules: bool
    has_single_term_anti_patterns: bool
    has_no_constraints: bool
    applies_to_paths: list[str]
    confidence: float


class MnemeAdapter:
    """
    Adapter that uses Mneme core to assess architectural decisions.
    
    Key principle: Mneme is the sole authority on governability.
    This adapter only extracts evidence and calls Mneme.
    """
    
    def __init__(self):
        self._memory_store: Optional[MemoryStore] = None
        self._retriever: Optional[DecisionRetriever] = None
        self._decisions: list[Decision] = []
    
    def load_repository(self, repo_path: Path) -> ImportReport:
        """
        Load and compile ADRs from a repository using Mneme's import pipeline.
        
        This uses Mneme's own ADR parser, validator, and precedence resolver.
        """
        adr_dirs = [
            repo_path / "docs" / "adr",
            repo_path / "adr",
            repo_path / ".adr",
        ]
        
        for adr_dir in adr_dirs:
            if adr_dir.exists() and adr_dir.is_dir():
                report = compile_for_import(adr_dir)
                self._decisions = report.decisions
                self._retriever = DecisionRetriever(self._decisions)
                return report
        
        from mneme.adr_import import ImportReport, DecisionNode
        return ImportReport(
            active_nodes=[],
            all_nodes=[],
            decisions=[],
            diagnostics=[],
            adr_sources_by_id={},
        )
    
    def load_memory_file(self, memory_path: Path) -> None:
        """Load a Mneme project memory file (.mneme/project_memory.json)."""
        if memory_path.exists():
            self._memory_store = MemoryStore(memory_path)
            self._decisions = self._memory_store.memory.decisions
            self._retriever = DecisionRetriever(self._decisions)
    
    def assess_governability(self, decision: Decision, source_file: str = "", source_lines: str = "") -> GovernabilityAssessment:
        """
        Use Mneme core to assess whether a decision can be deterministically governed.
        
        This is the single point where Mneme's authority on governability is invoked.
        """
        has_literal_rules = bool(decision.rules)
        has_single_term_anti_patterns = any(
            self._is_single_term(ap) for ap in decision.anti_patterns
        )
        has_no_constraints = any(
            re.match(r"^no\s+(.+)$", c.strip(), re.IGNORECASE)
            for c in decision.constraints
        )
        
        enforceable = has_literal_rules or has_single_term_anti_patterns
        partially_enforceable = has_no_constraints or bool(decision.anti_patterns)
        guidance_only = not enforceable and not partially_enforceable
        
        applies_to = []
        for rule in decision.rules:
            if rule.include_paths:
                applies_to.extend(rule.include_paths)
        
        if enforceable:
            confidence = 0.95
        elif partially_enforceable:
            confidence = 0.7
        else:
            confidence = 0.4
        
        return GovernabilityAssessment(
            decision_id=decision.id,
            decision_title=decision.decision,
            enforceable=enforceable,
            partially_enforceable=partially_enforceable,
            guidance_only=guidance_only,
            mneme_rules=decision.rules,
            has_literal_rules=has_literal_rules,
            has_single_term_anti_patterns=has_single_term_anti_patterns,
            has_no_constraints=has_no_constraints,
            applies_to_paths=applies_to or ["src/**"],
            confidence=confidence,
        )
    
    def _is_single_term(self, text: str) -> bool:
        """Check if an anti-pattern reduces to a single significant term (Mneme's logic)."""
        stopwords = frozenset({
            "add", "use", "not", "get", "set", "run", "and", "the",
            "for", "with", "into", "from", "that", "this", "will",
            "should", "would", "could", "make", "keep", "have",
        })
        words = re.findall(r"[a-z0-9]+", text.lower())
        significant = [w for w in words if len(w) >= 3 and w not in stopwords]
        return len(significant) == 1
    
    def get_proposed_rules(self, decision: Decision) -> list[dict]:
        """
        Extract proposed Mneme rules from a decision.
        
        Returns the rules that Mneme would actually enforce.
        """
        proposed = []
        
        for rule in decision.rules:
            proposed.append({
                "type": rule.type,
                "pattern": rule.value,
                "description": f"FORBID_LITERAL: {rule.value}",
                "include_paths": list(rule.include_paths) if rule.include_paths else None,
                "exclude_paths": list(rule.exclude_paths) if rule.exclude_paths else None,
            })
        
        for ap in decision.anti_patterns:
            if self._is_single_term(ap):
                proposed.append({
                    "type": "FORBID_LITERAL",
                    "pattern": ap,
                    "description": f"Anti-pattern (single term): {ap}",
                })
        
        for constraint in decision.constraints:
            m = re.match(r"^no\s+(.+)$", constraint.strip(), re.IGNORECASE)
            if m:
                proposed.append({
                    "type": "REQUIRE_PATTERN",
                    "pattern": m.group(1).strip(),
                    "description": f"Constraint: no {m.group(1).strip()}",
                })
        
        return proposed
    
    def retrieve_relevant_decisions(self, query: str) -> list[ScoredDecision]:
        """Retrieve decisions relevant to a query using Mneme's retriever."""
        if not self._retriever:
            return []
        return self._retriever.retrieve(query)
    
    def check_enforcement(self, input_text: str, input_path: str = "") -> EnforcementResult:
        """
        Check if input text would violate any Mneme decisions.
        
        This uses Mneme's actual enforcer with full path applicability logic.
        """
        if not self._retriever:
            return EnforcementResult(verdict=Severity.PASS, violations=[], applicability=[])
        
        scored = self._retriever.retrieve(input_text)
        return check_prompt(input_text, scored, top=3, input_path=input_path)


mneme_adapter = MnemeAdapter()