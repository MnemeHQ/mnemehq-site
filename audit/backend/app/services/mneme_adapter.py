"""
MnemeAdapter — Thin wrapper around Mneme core for the audit service.

This adapter translates the audit service's needs into Mneme operations:
- Import ADRs from a repository
- Evaluate governability of extracted decisions (via Mneme's assess_governability)
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
from mneme.enforcer import (
    check_prompt, 
    Severity, 
    EnforcementResult, 
    assess_governability,
    GovernabilityAssessment,
)
from mneme.decision_retriever import DecisionRetriever, ScoredDecision
from mneme.memory_store import MemoryStore


@dataclass
class ProposedRuleInfo:
    """A proposed Mneme rule extracted from a decision."""
    type: str
    pattern: str
    description: str
    include_paths: tuple[str, ...] | None = None
    exclude_paths: tuple[str, ...] = ()


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
        return assess_governability(decision)
    
    def get_proposed_rules(self, decision: Decision) -> list[ProposedRuleInfo]:
        """
        Extract proposed Mneme rules from a decision.
        
        Returns only the rules that Mneme actually enforces (typed FORBID_LITERAL rules
        and single-term anti_patterns). Does not invent rules for constraints.
        """
        proposed = []
        
        # Typed FORBID_LITERAL rules - these are always enforced
        for rule in decision.rules:
            if rule.type == "FORBID_LITERAL":
                proposed.append(ProposedRuleInfo(
                    type=rule.type,
                    pattern=rule.value,
                    description=f"{rule.type}: {rule.value}",
                    include_paths=rule.include_paths,
                    exclude_paths=rule.exclude_paths,
                ))
        
        # Single-term anti_patterns - these are always enforced (FAIL severity)
        from mneme.enforcer import _is_literal_rule
        for ap in decision.anti_patterns:
            if _is_literal_rule(ap):
                proposed.append(ProposedRuleInfo(
                    type="FORBID_LITERAL",
                    pattern=ap,
                    description=f"FORBID_LITERAL: {ap}",
                ))
        
        # Multi-term anti_patterns and "no X" constraints are NOT returned here.
        # They are enforced only for top-N retrieved decisions (multi-term)
        # or produce WARN severity (constraints), so they're not "deterministic rules"
        # in the same sense as typed FORBID_LITERAL rules.
        
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