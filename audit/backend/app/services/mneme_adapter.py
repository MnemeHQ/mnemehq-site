"""
MnemeAdapter — Thin wrapper around Mneme core for the audit service.

This adapter translates the audit service's needs into Mneme operations:
- Import ADRs from a repository
- Evaluate governability of extracted decisions (via Mneme's assess_governability)
- Generate proposed Mneme rules from decisions
- Assess governability of arbitrary constraints (for non-ADR sources)

All Mneme semantics (what is enforceable, how rules match, path applicability)
are delegated to Mneme core. This adapter does NOT duplicate Mneme logic.
"""
from __future__ import annotations

import re
import shutil
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional

from mneme.adr_compiler import validate_corpus
from mneme.adr_import import compile_for_import, ImportReport
from mneme.adr_parser import parse_adr_file
from mneme.adr_schema import ADR, ADRParseError, ADRValidationError
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


@dataclass(frozen=True)
class SkippedADR:
    """An ``ADR-*.md`` file that Mneme's strict ADR import could not use."""
    path: str  # repo-relative, POSIX separators
    reason: str
    detail: str


_ADR_ID = re.compile(r"ADR-\d+")


def _parse_failure_reason(message: str) -> str:
    if "missing YAML frontmatter" in message:
        return "missing_frontmatter"
    if "unterminated YAML frontmatter" in message:
        return "unterminated_frontmatter"
    if "malformed YAML frontmatter:" in message:
        return "malformed_yaml"
    return "invalid_frontmatter"


def _restore_source_paths(report: ImportReport, restore: dict[str, str]) -> ImportReport:
    """Point a report compiled from a temporary copy back at the original files."""
    def fix(path: str) -> str:
        return restore.get(path, path)

    changes = {
        "decisions": [replace(d, source_path=fix(d.source_path)) for d in report.decisions],
        "adr_sources_by_id": {k: fix(v) for k, v in report.adr_sources_by_id.items()},
    }
    # Later core releases also carry the parsed corpus on the report.
    if hasattr(report, "parsed_adrs"):
        changes["parsed_adrs"] = [
            replace(a, source_path=fix(a.source_path)) for a in report.parsed_adrs
        ]
    return replace(report, **changes)


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
        self.skipped_adrs: list[SkippedADR] = []

    def load_repository(self, repo_path: Path) -> ImportReport:
        """
        Load and compile ADRs from a repository using Mneme's import pipeline.

        This uses Mneme's own ADR parser, validator, and precedence resolver.
        Files that core cannot parse or validate are excluded one at a time and
        recorded in ``skipped_adrs``; they never abort the import of the rest.
        """
        adr_dirs = [
            repo_path / "docs" / "adr",
            repo_path / "adr",
            repo_path / ".adr",
        ]
        self.skipped_adrs = []

        for adr_dir in adr_dirs:
            if adr_dir.exists() and adr_dir.is_dir():
                report, self.skipped_adrs = self._compile_tolerant(adr_dir, repo_path)
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

    def _compile_tolerant(
        self, adr_dir: Path, repo_path: Path
    ) -> tuple[ImportReport, list[SkippedADR]]:
        """
        Run core's ``compile_for_import``, excluding files it cannot accept.

        A clean corpus goes straight through core. Otherwise each file is
        parsed and validated on its own with core's parser and validator, the
        failures are recorded, and core's ``compile_for_import`` runs again on
        a temporary copy holding only the files that passed.
        """
        try:
            return compile_for_import(adr_dir), []
        except (ADRParseError, ADRValidationError, UnicodeDecodeError, OSError):
            pass

        def relative(path: str | Path) -> str:
            try:
                return Path(path).relative_to(repo_path).as_posix()
            except ValueError:
                return Path(path).name

        def scrub(message: str, path: str | Path) -> str:
            return message.replace(str(path), relative(path))

        skipped: list[SkippedADR] = []
        valid: list[ADR] = []
        for path in sorted(adr_dir.glob("ADR-*.md")):
            try:
                adr = parse_adr_file(path)
            except ADRParseError as exc:
                skipped.append(SkippedADR(
                    relative(path), _parse_failure_reason(str(exc)), scrub(str(exc), path)
                ))
                continue
            except (UnicodeDecodeError, OSError) as exc:
                skipped.append(SkippedADR(
                    relative(path), "unreadable", f"{relative(path)}: {exc.__class__.__name__}: {exc}"
                ))
                continue
            # Per-record checks only; cross-record checks run on the survivors.
            try:
                validate_corpus([replace(adr, supersedes=[])])
            except ADRValidationError as exc:
                skipped.append(SkippedADR(
                    relative(path), "schema_invalid", scrub("; ".join(exc.errors), path)
                ))
                continue
            valid.append(adr)

        def exclude(adrs: list[ADR], reason: str, detail) -> None:
            for adr in adrs:
                skipped.append(SkippedADR(relative(adr.source_path), reason, detail(adr)))
                valid.remove(adr)

        counts: dict[str, int] = {}
        for adr in valid:
            counts[adr.id] = counts.get(adr.id, 0) + 1
        exclude(
            [a for a in valid if counts[a.id] > 1], "duplicate_id",
            lambda a: f"{relative(a.source_path)}: duplicate ADR id {a.id!r} ({counts[a.id]} files)",
        )

        # Core requires every supersedes target to be in the corpus. Excluding
        # a file can orphan a reference, so repeat until nothing changes.
        while True:
            known = {a.id for a in valid}
            dangling = [a for a in valid if any(r not in known for r in a.supersedes)]
            if not dangling:
                break
            exclude(
                dangling, "unknown_supersedes_reference",
                lambda a: (
                    f"{relative(a.source_path)}: supersedes "
                    f"{', '.join(repr(r) for r in a.supersedes if r not in known)}, "
                    f"which is not a valid Mneme-format ADR in this directory"
                ),
            )

        while valid:
            try:
                validate_corpus(valid)
                break
            except ADRValidationError as exc:
                ids = {i for e in exc.errors for i in _ADR_ID.findall(e)}
                in_cycle = [a for a in valid if a.id in ids] or list(valid)
                exclude(
                    in_cycle,
                    "supersession_cycle" if ids else "corpus_invalid",
                    lambda a: scrub("; ".join(exc.errors), a.source_path),
                )

        skipped.sort(key=lambda s: s.path)
        with tempfile.TemporaryDirectory(prefix="mneme-adr-") as tmp:
            restore: dict[str, str] = {}
            for adr in valid:
                source = Path(adr.source_path)
                shutil.copyfile(source, Path(tmp) / source.name)
                restore[str(Path(tmp) / source.name)] = adr.source_path
            report = compile_for_import(Path(tmp))
        return _restore_source_paths(report, restore), skipped
    
    def load_memory_file(self, memory_path: Path) -> None:
        """Load a Mneme project memory file (.mneme/project_memory.json)."""
        if memory_path.exists():
            self._memory_store = MemoryStore(memory_path)
            self._memory_store.load()
            self._decisions = self._memory_store.memory.decisions
            self._retriever = DecisionRetriever(self._decisions)
    
    def assess_governability(self, decision: Decision, source_file: str = "", source_lines: str = "") -> GovernabilityAssessment:
        """
        Use Mneme core to assess whether a decision can be deterministically governed.
        
        This is the single point where Mneme's authority on governability is invoked.
        """
        return assess_governability(decision)
    
    def assess_governability_from_text(
        self, 
        decision_text: str, 
        rationale: str = "",
        constraints: list[str] | None = None,
        anti_patterns: list[str] | None = None,
        scope: list[str] | None = None,
        decision_id: str = ""
    ) -> GovernabilityAssessment:
        """
        Assess governability for arbitrary text/constraints by creating a Mneme Decision.
        
        This allows the audit to evaluate non-ADR sources (CLAUDE.md, AGENTS.md, 
        loose ADRs, config files) using Mneme's authoritative governability logic.
        
        Args:
            decision_text: The core decision/constraint statement
            rationale: Why this decision was made
            constraints: List of hard constraints (e.g., "no postgres", "use Ed25519")
            anti_patterns: List of explicitly forbidden patterns
            scope: List of areas this applies to (e.g., ["auth", "storage"])
            decision_id: Optional ID for the decision
            
        Returns:
            Mneme's authoritative GovernabilityAssessment
        """
        if not decision_id:
            import uuid
            decision_id = f"audit_{uuid.uuid4().hex[:8]}"
        
        decision = Decision(
            id=decision_id,
            decision=decision_text,
            rationale=rationale or "",
            scope=scope or [],
            constraints=constraints or [],
            anti_patterns=anti_patterns or [],
            rules=[],  # Non-ADR sources don't have typed rules
            source_path="",
        )
        
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