"""
Stateless single-ADR check for the free ADR checker page.

One pasted ADR is classified in-process by the shipped Audit pipeline and
nothing is kept. The differences from a repository Audit are deliberate:

- The caller supplies text only, never a file name. The text is written to a
  fixed path chosen by its format, so the same ADR always gets the same
  result (the repository Audit's channels depend on file name and folder).
- Exactly one channel runs. A Mneme-format ADR (valid YAML frontmatter) goes
  through core's canonical ADR import; anything else goes through the
  per-statement docs channel, which gives line-level rows and has no
  Decision-heading or 20-character cutoff.
- Protected is never returned. Pasted text has no repository, hook or CI
  behind it, so the best it can show is that a rule is ready to enforce.
  A Protected row is reported as Mneme-ready with ``protected_capped``.
- No database, no project row, no result storage. The temp dir is removed
  in ``finally``. The text is never logged.
"""
from __future__ import annotations

import re
import shutil
import tempfile
from dataclasses import dataclass, field
from importlib.metadata import version
from pathlib import Path
from typing import List, Optional

from app.models.protection_audit import ProtectionClassification
from app.services.markdown_discovery import (
    MAX_STATEMENTS_PER_FILE,
    discover_architecture_statements,
)
from app.services.mneme_adapter import MnemeAdapter
from app.services.p12_adapter import build_protection_decision, collect_p12_inputs

MAX_TEXT_BYTES = 64 * 1024

# Fixed placements. Chosen by format, never by anything the caller names.
MNEME_FORMAT_PATH = "adr/ADR-000-pasted.md"
PROSE_PATH = "docs/pasted-adr.md"

MAX_UNCLASSIFIED_LINES = 200

_FRONTMATTER_RE = re.compile(r"\A﻿?---[ \t]*\r?\n")
_HEADING_RE = re.compile(r"^#{1,6}\s")
_TABLE_SEPARATOR_RE = re.compile(r"^\|?[\s:|-]+\|?$")


class CheckInputError(ValueError):
    """The pasted text cannot be checked (empty or too large)."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass
class CheckRow:
    statement: str
    heading: str
    line_start: Optional[int]
    line_end: Optional[int]
    classification: str
    protected_capped: bool = False
    proposed_rule: Optional[dict] = None


@dataclass
class CheckResult:
    format: str  # "mneme" | "prose"
    mneme_version: str
    rows: List[CheckRow] = field(default_factory=list)
    unclassified_lines: List[dict] = field(default_factory=list)
    truncated: bool = False

    def to_dict(self) -> dict:
        counts = {c: 0 for c in ("Mneme-ready", "Requires modelling", "Guidance")}
        for row in self.rows:
            counts[row.classification] += 1
        return {
            "kind": "adr",
            "format": self.format,
            "engine": "mneme-hq",
            "mneme_version": self.mneme_version,
            "summary": {
                "mneme_ready_count": counts["Mneme-ready"],
                "requires_modelling_count": counts["Requires modelling"],
                "guidance_count": counts["Guidance"],
                "unclassified_count": len(self.unclassified_lines),
                "protected_capped": any(r.protected_capped for r in self.rows),
                "truncated": self.truncated,
            },
            "rows": [r.__dict__ for r in self.rows],
            "unclassified_lines": self.unclassified_lines,
        }


def validate_text(text: object) -> str:
    if not isinstance(text, str) or not text.strip():
        raise CheckInputError("empty", "Paste the text of one ADR.")
    if len(text.encode("utf-8")) > MAX_TEXT_BYTES:
        raise CheckInputError("too_large", "The ADR is over the 64 KB limit.")
    return text


def size_bucket(text: str) -> str:
    """Coarse size for logs and analytics; never the text itself."""
    size = len(text.encode("utf-8"))
    if size < 1024:
        return "lt_1kb"
    if size < 4 * 1024:
        return "1_4kb"
    if size < 16 * 1024:
        return "4_16kb"
    return "16_64kb"


def _capped(classification: ProtectionClassification) -> tuple[str, bool]:
    if classification == ProtectionClassification.PROTECTED:
        return ProtectionClassification.MNEME_READY.value, True
    return classification.value, False


def _rule(decision) -> Optional[dict]:
    rule = decision.proposed_rule
    return {"type": rule.type, "pattern": rule.pattern} if rule else None


def _write(root: Path, relative: str, text: str) -> None:
    target = root / relative
    target.parent.mkdir(parents=True)
    # newline="" keeps the caller's line endings, so line numbers match.
    with target.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def _check_mneme_format(root: Path, text: str) -> Optional[List[CheckRow]]:
    """Canonical ADR import. None when core does not accept the file."""
    _write(root, MNEME_FORMAT_PATH, text)
    adapter = MnemeAdapter()
    report = adapter.load_repository(root)
    if not report.decisions:
        return None
    inputs = collect_p12_inputs(
        mneme_report=report, loose_adrs=[], agent_instructions=[],
        config_files=[], repo_path=root, markdown_statements=[],
    )
    rows = []
    for item in inputs:
        decision = build_protection_decision(item)
        classification, capped = _capped(decision.protection_classification)
        rows.append(CheckRow(
            statement=item.decision.decision,
            heading=item.decision.id,
            line_start=None,
            line_end=None,
            classification=classification,
            protected_capped=capped,
            proposed_rule=_rule(decision),
        ))
    return rows


def _unclassified(text: str, classified: set[int]) -> List[dict]:
    """Lines that carry text but produced no row, so nothing is hidden."""
    lines = []
    in_fence = False
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped or number in classified:
            continue
        if _HEADING_RE.match(stripped) or _TABLE_SEPARATOR_RE.match(stripped):
            continue
        lines.append({"line": number, "text": stripped})
    return lines[:MAX_UNCLASSIFIED_LINES]


def _check_prose(root: Path, text: str) -> tuple[List[CheckRow], List[dict], bool]:
    """Per-statement docs channel at a fixed path."""
    _write(root, PROSE_PATH, text)
    statements = discover_architecture_statements(root)
    inputs = collect_p12_inputs(
        mneme_report=_EmptyReport(), loose_adrs=[], agent_instructions=[],
        config_files=[], repo_path=root, markdown_statements=statements,
    )
    rows = []
    for statement, item in zip(statements, inputs):
        decision = build_protection_decision(item)
        classification, capped = _capped(decision.protection_classification)
        rows.append(CheckRow(
            statement=statement.text,
            heading=statement.heading,
            line_start=statement.line_start,
            line_end=statement.line_end,
            classification=classification,
            protected_capped=capped,
            proposed_rule=_rule(decision),
        ))
    classified = {line for r in rows for line in range(r.line_start, r.line_end + 1)}
    truncated = len(statements) >= MAX_STATEMENTS_PER_FILE
    return rows, _unclassified(text, classified), truncated


class _EmptyReport:
    decisions: list = []


def check_adr(text: str) -> CheckResult:
    """Classify one pasted ADR. Stores nothing; the temp dir is always removed."""
    text = validate_text(text)
    engine = version("mneme-hq")
    root = Path(tempfile.mkdtemp(prefix="mneme-check-"))
    try:
        if _FRONTMATTER_RE.match(text):
            rows = _check_mneme_format(root / "mneme", text)
            if rows is not None:
                return CheckResult(format="mneme", mneme_version=engine, rows=rows)
        rows, unclassified, truncated = _check_prose(root / "prose", text)
        return CheckResult(
            format="prose", mneme_version=engine, rows=rows,
            unclassified_lines=unclassified, truncated=truncated,
        )
    finally:
        shutil.rmtree(root, ignore_errors=True)
