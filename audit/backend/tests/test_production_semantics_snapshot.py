"""Semantic regression snapshots for the production Mneme engine resolution.

audit/backend/requirements.lock pins the exact engine the production image
runs. These snapshots record what that engine concludes about each Audit
fixture repository, so an engine upgrade (a reviewed change to the lock)
cannot change Audit semantics without the change appearing in the same diff.

A snapshot keeps only fields that express Audit semantics: where a decision
comes from, what it requires, how it is classified, how confident the
evidence is, the proposed guardrail, and the summary counts and scores.
Generated IDs, timestamps, the runtime engine version, temporary paths and
ordering noise are stripped.

Behaviour:
- installed mneme-hq == locked version: any difference FAILS. This is the
  locked CI job and proves exact production semantics.
- installed mneme-hq != locked version (the unconstrained CI job, or a local
  environment): a difference is reported as a SKIP with a drift summary. It is
  early warning for the next engine upgrade, not a production failure.

Regenerate after an intentional engine upgrade, in the locked environment:

    UPDATE_AUDIT_SNAPSHOTS=1 python -m pytest tests/test_production_semantics_snapshot.py
"""
from __future__ import annotations

import json
import os
import re
from importlib.metadata import version
from pathlib import Path

import pytest

from app.services.audit_persistence import AuditPersistenceService

BACKEND = Path(__file__).parents[1]
FIXTURES = Path(__file__).parents[3] / "tests" / "fixtures"
SNAPSHOTS = Path(__file__).parent / "snapshots"
LOCK = BACKEND / "requirements.lock"

FIXTURE_NAMES = (
    "adr-gadr",
    "audit-repo",
    "guardrail-ready",
    "sagarika-architecture-docs",
)


def locked_engine_version() -> str:
    match = re.search(r"(?mi)^mneme-hq==(\S+)$", LOCK.read_text(encoding="utf-8"))
    assert match, f"{LOCK} does not pin mneme-hq"
    return match.group(1)


def semantic_view(result) -> dict:
    """Project an audit response onto its deterministic, semantic fields."""
    summary = result.summary
    decisions = []
    for decision in result.decisions:
        rule = decision.proposed_rule
        decisions.append({
            "source_file": decision.source.file.replace("\\", "/"),
            "source_lines": decision.source.lines,
            "title": decision.title,
            "requirement": decision.requirement,
            "category": decision.category,
            "protection_classification": decision.protection_classification.value,
            "evidence_confidence": decision.evidence_confidence.value,
            "applies_to": sorted(decision.applies_to),
            "proposed_rule": None if rule is None else {
                "type": rule.type,
                "pattern": rule.pattern,
                "include_paths": sorted(rule.include_paths) if rule.include_paths else None,
                "exclude_paths": sorted(rule.exclude_paths),
            },
        })
    decisions.sort(key=lambda d: (d["source_file"], d["source_lines"], d["title"], d["requirement"]))
    return {
        "summary": {
            "decisions_discovered": summary.decisions_discovered,
            "protection_relevant": summary.protection_relevant,
            "protected_count": summary.protected_count,
            "mneme_ready_count": summary.mneme_ready_count,
            "requires_modelling_count": summary.requires_modelling_count,
            "guidance_count": summary.guidance_count,
            "current_protection": round(summary.current_protection, 4),
            "identified_mneme_potential": round(summary.identified_mneme_potential, 4),
            # Path separators are platform noise (Windows reports some sources
            # with backslashes), so compare POSIX-style, de-duplicated paths.
            "sources": sorted({source.replace("\\", "/") for source in summary.sources}),
            "by_category": dict(sorted(summary.by_category.items())),
        },
        "decisions": decisions,
    }


def describe_drift(expected: dict, actual: dict) -> str:
    def keyed(view):
        return {
            (d["source_file"], d["source_lines"], d["title"]): d for d in view["decisions"]
        }
    before, after = keyed(expected), keyed(actual)
    changed = sorted(key for key in before.keys() & after.keys() if before[key] != after[key])
    parts = [
        f"{len(after.keys() - before.keys())} decision(s) added",
        f"{len(before.keys() - after.keys())} removed",
        f"{len(changed)} changed",
    ]
    if expected["summary"] != actual["summary"]:
        parts.append("summary differs")
    for key in changed[:3]:
        fields = [f for f in before[key] if before[key][f] != after[key][f]]
        parts.append(f"{key[0]}:{key[1]} {fields}")
    return "; ".join(parts)


@pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
def test_fixture_semantics_match_production_snapshot(fixture_name):
    service = AuditPersistenceService(session=None)
    result = service._evaluate_p12(local_path=str(FIXTURES / fixture_name))
    actual = semantic_view(result)
    snapshot_path = SNAPSHOTS / f"{fixture_name}.json"

    installed, locked = version("mneme-hq"), locked_engine_version()
    if os.environ.get("UPDATE_AUDIT_SNAPSHOTS") == "1":
        assert installed == locked, (
            f"snapshots must be generated with the locked engine ({locked}), "
            f"not the installed {installed}"
        )
        SNAPSHOTS.mkdir(exist_ok=True)
        snapshot_path.write_text(
            json.dumps(actual, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n",
        )
        return

    assert snapshot_path.exists(), f"missing production snapshot {snapshot_path.name}"
    expected = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if actual == expected:
        return
    drift = describe_drift(expected, actual)
    if installed != locked:
        pytest.skip(
            f"semantic drift vs production snapshot: installed mneme-hq {installed}, "
            f"production lock {locked}: {drift}"
        )
    pytest.fail(
        f"{fixture_name}: Audit semantics changed under the locked engine {locked}: {drift}. "
        "If this is an intentional engine upgrade, regenerate the snapshots and review the diff."
    )
