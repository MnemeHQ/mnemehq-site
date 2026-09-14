"""
markdown_discovery.py — Candidate architectural statements from ordinary
Markdown architecture documentation.

This is the minimum discovery surface added after the first Design Partner
server capture (sagarika29/ai-system-architect @ 0797e27): the autonomous
server Audit returned a single low-confidence "Project Config:
pyproject.toml" pseudo-decision while the reviewed corpus contains meaningful
documented boundaries in ordinary docs/ Markdown (architecture boundaries,
architecture guide, PRD).

Deliberate non-goals (M0 scope):
- no embeddings / vector search, no graph store, no LLM extraction pipeline;
- no PDFs, Office files, or arbitrary-document ingestion;
- no partner-specific filenames or vocabulary: eligibility comes from file
  location (docs/ Markdown), filename priority ORDER, and the decision
  intent reported by the public Mneme Core API (ADR-028,
  ``assess_decision_intent``) — ADR-026 intent semantics are owned by
  Mneme Core and are never reimplemented here.

Extraction channels (deterministic):
1. Self-describing statements: any sentence-level line whose text itself
   carries prescriptive or advisory intent markers (``must``, ``never``,
   ``fail closed``, ``should``, ``may`` ...) is a candidate statement. The
   four-tier classification is delegated to Mneme core (``assess_protection``)
   — this module never invents tiers from file or heading shape alone.
2. Section-qualified boundary bullets: list items / table rows under a
   heading that the document itself labels "deterministic" (or
   "probabilistic") are candidates, because the heading is part of the
   documented statement. A deterministic-labelled bullet is Requires
   modelling unless its own text is advisory (ADR-026: advisory wording
   outranks prescriptive markers); a probabilistic-labelled bullet is
   Guidance unless its own text is prescriptive.

False-positive controls:
- a heading alone is never a decision;
- fenced code blocks are skipped entirely;
- neutral noun phrases outside labelled sections are skipped;
- filename shape only affects candidate ORDER, never eligibility;
- statements are deduplicated (per file, and across files for identical
  section-qualified bullet texts);
- per-file and total caps bound pathological documentation trees.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from mneme.enforcer import DecisionIntent, assess_decision_intent


# Statements shorter than this are fragments (single nouns like "Logging"),
# not documented boundaries.
MIN_STATEMENT_CHARS = 15

# Safety caps for pathological documentation trees. Generous on purpose:
# the semantic gate, not the cap, is the primary filter.
MAX_STATEMENTS_PER_FILE = 40
MAX_STATEMENTS_TOTAL = 120

# Only Markdown under docs/ is scanned in M0. This is the narrowest source
# that covers the Design Partner corpus; expanding the surface is a
# deliberate later decision, not an accident of this module.
DOCS_DIR = "docs"

# Generic non-normative documentation locations: sample/example outputs are
# generated artefacts or walkthroughs, not architectural decisions. Matching
# is on generic segment names only (no partner-specific vocabulary).
_NON_NORMATIVE_SEGMENT_RE = re.compile(
    r"^(?:samples?|examples?|gallery|fixtures?|demos?)", re.IGNORECASE
)
_NON_NORMATIVE_FILENAME_RE = re.compile(
    r"(?:sample|example)", re.IGNORECASE
)

# Filename keywords that order candidates first. ORDER ONLY: a matching
# filename never creates a statement by itself.
PRIORITY_FILENAME_KEYWORDS = (
    "architecture",
    "design",
    "boundary",
    "boundaries",
    "decision",
    "principle",
    "constraint",
)

# Headings that the document itself uses to label boundary sections.
_DETERMINISTIC_HEADING_RE = re.compile(r"\bdeterministic\b", re.IGNORECASE)
_PROBABILISTIC_HEADING_RE = re.compile(r"\bprobabilistic\b", re.IGNORECASE)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_BULLET_RE = re.compile(r"^\s{0,12}(?:[-*+]|\d+[.)])\s+(.+?)\s*$")

# Industry-standard user-story template voice ("As an <role>, I ...").
# Stories describe product intent, not architectural requirements.
_USER_STORY_RE = re.compile(r"^As an?\b.{0,80}?,\s+I\b", re.IGNORECASE)


@dataclass(frozen=True)
class DiscoveredStatement:
    """One candidate architectural statement with source evidence."""

    text: str  # statement text (verbatim material, heading-qualified when labelled)
    heading: str  # nearest heading, verbatim ("" at top level)
    file: str  # repo-relative POSIX path
    line_start: int  # 1-based, inclusive
    line_end: int  # 1-based, inclusive
    origin: str  # "sentence" | "deterministic-section" | "probabilistic-section"

    @property
    def lines(self) -> str:
        return f"{self.line_start}-{self.line_end}"

    @property
    def intent(self) -> DecisionIntent:
        """Authoritative ADR-026 intent verdict from the public Core API.

        Mneme Core owns intent semantics (ADR-026/ADR-028); the site never
        reimplements advisory/prescriptive classification and never reads
        raw lexical markers.
        """
        return assess_decision_intent(self.text).intent


def _strip_inline_markup(text: str) -> str:
    """Remove harmless inline markup; keep inline code (quoted term bans)."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", text)
    text = re.sub(r"\[(.+?)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_table_row(line: str) -> bool:
    return line.lstrip().startswith("|")


def _table_cells(line: str) -> str:
    inner = line.strip().strip("|")
    cells = [c.strip() for c in inner.split("|")]
    if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
        return ""  # separator row
    return " ".join(c for c in cells if c)


def _markdown_files(repo_path: Path) -> List[Path]:
    docs = repo_path / DOCS_DIR
    if not docs.is_dir():
        return []
    files = []
    for path in docs.rglob("*.md"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_path)
        if any(_NON_NORMATIVE_SEGMENT_RE.match(part) for part in rel.parts):
            continue
        if _NON_NORMATIVE_FILENAME_RE.search(path.name):
            continue
        files.append(path)
    def sort_key(path: Path) -> tuple:
        rel = path.relative_to(repo_path).as_posix().lower()
        prioritized = any(k in Path(rel).name for k in PRIORITY_FILENAME_KEYWORDS)
        return (0 if prioritized else 1, rel)
    return sorted(files, key=sort_key)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def discover_architecture_statements(repo_path: Path) -> List[DiscoveredStatement]:
    """Discover candidate architectural statements from docs/ Markdown."""
    repo_path = Path(repo_path)
    statements: List[DiscoveredStatement] = []
    seen_in_file: set[tuple[str, str]] = set()
    seen_globally: set[str] = set()

    for path in _markdown_files(repo_path):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        rel = path.relative_to(repo_path).as_posix()
        heading = ""
        in_fence = False
        file_count = 0
        separator_lines: set[int] = {
            index for index, line in enumerate(lines, start=1)
            if _is_table_row(line) and not _table_cells(line)
        }

        for index, raw in enumerate(lines, start=1):
            stripped = raw.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            heading_match = _HEADING_RE.match(stripped)
            if heading_match:
                # A heading is never a decision by itself; it only scopes
                # the statements below it.
                heading = _strip_inline_markup(heading_match.group(2))
                continue

            is_bullet = bool(_BULLET_RE.match(raw))
            bullet_text = _BULLET_RE.match(raw).group(1) if is_bullet else ""
            is_table = _is_table_row(raw)
            content = bullet_text if is_bullet else (
                _table_cells(raw) if is_table else stripped
            )
            text = _strip_inline_markup(content)
            if len(text) < MIN_STATEMENT_CHARS:
                continue
            if is_table and index + 1 in separator_lines:
                continue  # table header row: labels, not statements
            if _USER_STORY_RE.match(text):
                continue

            origin: Optional[str] = None
            if is_bullet or is_table:
                # The document's own section label is part of a bullet's
                # statement, so a labelled section qualifies its items
                # before the bare-text channel runs.
                if _DETERMINISTIC_HEADING_RE.search(heading):
                    origin = "deterministic-section"
                elif _PROBABILISTIC_HEADING_RE.search(heading):
                    origin = "probabilistic-section"
            if origin is None and assess_decision_intent(text).intent != "neutral":
                origin = "sentence"
            if origin is None:
                continue

            if origin != "sentence":
                # Heading is part of the documented statement for
                # section-qualified bullets.
                text = f"{heading}: {text}"
                # Cross-file dedupe keys on the bullet itself so the same
                # documented boundary is not reported once per labelling
                # heading.
                global_key = _normalize(
                    _BULLET_RE.match(raw).group(1) if is_bullet else content
                )
            else:
                global_key = _normalize(text)
            key = (rel, text)
            if key in seen_in_file:
                continue
            if global_key in seen_globally:
                continue
            if len(statements) >= MAX_STATEMENTS_TOTAL:
                break
            seen_in_file.add(key)
            seen_globally.add(global_key)
            statements.append(DiscoveredStatement(
                text=text,
                heading=heading,
                file=rel,
                line_start=index,
                line_end=index,
                origin=origin,
            ))
            file_count += 1
            if file_count >= MAX_STATEMENTS_PER_FILE:
                break
        if len(statements) >= MAX_STATEMENTS_TOTAL:
            break

    return statements


def statement_to_decision(statement: DiscoveredStatement):
    """Materialize a statement as a Mneme Decision for canonical assessment.

    Mneme core stays the sole authority on classification; the rationale
    carries the source evidence (file, line range, heading).
    """
    from mneme.schemas import Decision

    decision_id = "md_" + hashlib.sha256(
        f"{statement.file}:{statement.line_start}:{statement.text}".encode("utf-8")
    ).hexdigest()[:16]
    rationale = (
        f"Discovered from {statement.file}:{statement.lines} under heading "
        f"'{statement.heading}'" if statement.heading
        else f"Discovered from {statement.file}:{statement.lines}"
    )
    return Decision(
        id=decision_id,
        decision=statement.text,
        rationale=rationale,
        scope=[],
        constraints=[],
        anti_patterns=[],
        rules=[],
        source_path=statement.file,
    )


def assess_statement(statement: DiscoveredStatement):
    """Classify a statement via Mneme core's ADR-026 tier semantics.

    Returns the canonical :class:`ProtectionDecisionReport`. Mneme core is
    the sole authority; this wrapper only resolves the document-structure
    channel for statements whose own text is neutral (the document's own
    "deterministic"/"probabilistic" labelling):
    - a self-describing sentence is always assessed by core from its text;
    - a deterministic-labelled bullet with advisory wording stays Guidance
      (ADR-026: advisory outranks prescriptive/structural markers);
    - a probabilistic-labelled bullet with prescriptive wording is still
      assessed by core from its text;
    - a neutral bullet inherits only its labelled section's meaning
      (deterministic -> requires_modelling, probabilistic -> guidance).
    """
    from mneme.enforcer import ProtectionDecisionReport, assess_protection

    decision = statement_to_decision(statement)
    if statement.origin == "sentence":
        return assess_protection(decision)
    if statement.origin == "probabilistic-section":
        if statement.intent == "prescriptive":
            return assess_protection(decision)
        return ProtectionDecisionReport(
            id=decision.id,
            decision=decision.decision,
            status="active",
            intent="guidance",
            protection_tier="guidance",
            mneme_guardrail=None,
            evidence_confidence="none",
            evidence_sources=[],
        )
    # deterministic-section
    if statement.intent == "advisory":
        return ProtectionDecisionReport(
            id=decision.id,
            decision=decision.decision,
            status="active",
            intent="guidance",
            protection_tier="guidance",
            mneme_guardrail=None,
            evidence_confidence="none",
            evidence_sources=[],
        )
    if statement.intent == "prescriptive":
        return assess_protection(decision)
    return ProtectionDecisionReport(
        id=decision.id,
        decision=decision.decision,
        status="active",
        intent="deterministic",
        protection_tier="requires_modelling",
        mneme_guardrail=None,
        evidence_confidence="none",
        evidence_sources=[],
    )
