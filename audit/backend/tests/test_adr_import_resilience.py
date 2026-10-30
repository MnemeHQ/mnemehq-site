"""One malformed or unsupported ADR must not abort the whole audit.

Core's ``compile_for_import`` refuses the entire ADR directory when any
``ADR-*.md`` file lacks frontmatter, has malformed YAML, or fails schema
validation. The audit keeps every valid file and reports the rest under the
additive ``unclassified_adr_files`` response field.
"""
from pathlib import Path

import pytest
from mneme.adr_import import compile_for_import
from mneme.adr_schema import ADRParseError

from app.services import mneme_adapter as mneme_adapter_module
from app.services.audit_persistence import AuditPersistenceService
from app.services.mneme_adapter import MnemeAdapter


MNEME_ADR = """---
id: ADR-001
title: Database Choice
status: accepted
date: 2026-01-15
priority: foundational
scope: database
---

# ADR-001: Database Choice

## Decision
Use PostgreSQL for all persistent application data.

## Constraints
- FORBID_LITERAL: sqlite
"""

MNEME_ADR_2 = """---
id: ADR-002
title: Package Manager
status: accepted
date: 2026-01-16
priority: normal
scope: tooling
---

# ADR-002: Package Manager

## Decision
Use uv for Python dependency management.

## Constraints
- FORBID_LITERAL: pipenv
"""

NYGARD_ADR = """# ADR-003: Message Queue

## Status
Accepted

## Context
Services need asynchronous communication.

## Decision
We will use RabbitMQ for all inter-service messaging. Do not use Kafka.
"""

MADR_ADR = """# ADR-004: Use REST for public APIs

## Context and Problem Statement
Public clients need a stable API style.

## Decision Outcome
Chosen option: REST over HTTP, because every client already supports it.
"""

BROKEN_YAML_ADR = """---
id: ADR-005
title: Broken
status: [accepted
---

## Decision
Never ship this.
"""

SCHEMA_INVALID_ADR = """---
id: ADR-006
title: Capitalised status
status: Accepted
date: 2026-02-01
priority: normal
scope: api
---

## Decision
Use gRPC internally.

## Constraints
- FORBID_LITERAL: thrift
"""


def _repo(tmp_path: Path, files: dict[str, str]) -> Path:
    repo = tmp_path / "repo"
    for name, content in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return repo


def _audit(repo: Path) -> dict:
    response = AuditPersistenceService(session=None)._evaluate_p12(local_path=str(repo))
    return response.model_dump(mode="json")


def _by_file(payload: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for decision in payload["decisions"]:
        out.setdefault(decision["source"]["file"], []).append(decision)
    return out


def _unclassified(payload: dict) -> dict[str, dict]:
    return {item["path"]: item for item in payload["unclassified_adr_files"]}


def test_missing_frontmatter_does_not_fail_the_audit(tmp_path):
    repo = _repo(tmp_path, {"docs/adr/ADR-001-database.md": NYGARD_ADR})

    payload = _audit(repo)

    # Core cannot import it, but the loose-ADR channel still classifies it.
    assert "docs/adr/ADR-001-database.md" in _by_file(payload)
    assert payload["unclassified_adr_files"] == []


def test_malformed_yaml_is_reported_not_fatal(tmp_path):
    repo = _repo(tmp_path, {"docs/adr/ADR-005-broken.md": BROKEN_YAML_ADR})

    payload = _audit(repo)

    assert payload["schema"] == "mneme.audit/v1"
    # Not imported as an ADR; markdown discovery may still lift a statement.
    rows = _by_file(payload).get("docs/adr/ADR-005-broken.md", [])
    assert all(not row["id"].startswith(("ADR-", "loose_")) for row in rows)
    item = _unclassified(payload)["docs/adr/ADR-005-broken.md"]
    assert item["reason"] == "malformed_yaml"
    assert "malformed YAML frontmatter" in item["detail"]
    assert str(tmp_path) not in item["detail"]


def test_mixed_format_repository_keeps_every_valid_adr(tmp_path):
    repo = _repo(tmp_path, {
        "docs/adr/ADR-001-database.md": MNEME_ADR,
        "docs/adr/ADR-002-package-manager.md": MNEME_ADR_2,
        "docs/adr/ADR-003-message-queue.md": NYGARD_ADR,
        "docs/adr/ADR-004-rest.md": MADR_ADR,
        "docs/adr/ADR-005-broken.md": BROKEN_YAML_ADR,
        "docs/adr/ADR-006-grpc.md": SCHEMA_INVALID_ADR,
    })
    clean = _repo(tmp_path / "clean", {
        "docs/adr/ADR-001-database.md": MNEME_ADR,
        "docs/adr/ADR-002-package-manager.md": MNEME_ADR_2,
    })

    payload = _audit(repo)
    by_file = _by_file(payload)

    # Mneme-format ADRs classify exactly as they do in a clean corpus.
    clean_by_file = _by_file(_audit(clean))
    for name in ("docs/adr/ADR-001-database.md", "docs/adr/ADR-002-package-manager.md"):
        strip = lambda ds: [{k: v for k, v in d.items() if k != "id"} for d in ds]
        assert strip(by_file[name]) == strip(clean_by_file[name])
        assert by_file[name][0]["proposed_rule"] is not None

    # Nygard and MADR files still go through the loose-ADR channel.
    assert "docs/adr/ADR-003-message-queue.md" in by_file
    assert "docs/adr/ADR-004-rest.md" in by_file

    unclassified = _unclassified(payload)
    assert set(unclassified) == {"docs/adr/ADR-005-broken.md", "docs/adr/ADR-006-grpc.md"}
    assert unclassified["docs/adr/ADR-005-broken.md"]["reason"] == "malformed_yaml"
    assert unclassified["docs/adr/ADR-006-grpc.md"]["reason"] == "schema_invalid"
    assert "invalid status 'Accepted'" in unclassified["docs/adr/ADR-006-grpc.md"]["detail"]


def test_clean_corpus_fallback_matches_core(tmp_path, monkeypatch):
    """The per-file fallback compiles a valid corpus exactly as core does."""
    repo = _repo(tmp_path, {
        "docs/adr/ADR-001-database.md": MNEME_ADR,
        "docs/adr/ADR-002-package-manager.md": MNEME_ADR_2,
        "docs/adr/ADR-007-database.md": MNEME_ADR.replace("id: ADR-001", "id: ADR-007").replace(
            "scope: database", "scope: database\nsupersedes: [ADR-001]"),
    })
    adr_dir = repo / "docs" / "adr"

    calls = []

    def refuse_first(path):
        calls.append(path)
        if len(calls) == 1:
            raise ADRParseError("force the per-file path")
        return compile_for_import(path)

    monkeypatch.setattr(mneme_adapter_module, "compile_for_import", refuse_first)
    fallback, skipped = MnemeAdapter()._compile_tolerant(adr_dir, repo)

    assert len(calls) == 2
    assert skipped == []
    assert fallback == compile_for_import(adr_dir)


def test_supersedes_reference_to_an_excluded_adr_is_reported(tmp_path):
    """Core rejects a supersedes target that is not in the corpus; so do we."""
    superseding = MNEME_ADR.replace("id: ADR-001", "id: ADR-007").replace(
        "scope: database", "scope: database\nsupersedes: [ADR-006]"
    )
    chained = MNEME_ADR.replace("id: ADR-001", "id: ADR-008").replace(
        "scope: database", "scope: storage\nsupersedes: [ADR-007]"
    )
    repo = _repo(tmp_path, {
        "docs/adr/ADR-002-package-manager.md": MNEME_ADR_2,
        "docs/adr/ADR-006-grpc.md": SCHEMA_INVALID_ADR,
        "docs/adr/ADR-007-database.md": superseding,
        "docs/adr/ADR-008-storage.md": chained,
    })

    adapter = MnemeAdapter()
    report = adapter.load_repository(repo)

    assert [d.id for d in report.decisions] == ["ADR-002"]
    skipped = {s.path: s for s in adapter.skipped_adrs}
    assert skipped["docs/adr/ADR-006-grpc.md"].reason == "schema_invalid"
    assert skipped["docs/adr/ADR-007-database.md"].reason == "unknown_supersedes_reference"
    assert "'ADR-006'" in skipped["docs/adr/ADR-007-database.md"].detail
    assert skipped["docs/adr/ADR-008-storage.md"].reason == "unknown_supersedes_reference"


@pytest.mark.parametrize("content, reason", [
    ("---\nid: ADR-001\nstatus: accepted\n", "unterminated_frontmatter"),
    ("---\n- just\n- a list\n---\n", "invalid_frontmatter"),
    ("---\nid: ADR-001\nsupersedes: ADR-000\n---\n", "invalid_frontmatter"),
])
def test_other_parse_failures_have_reasons(tmp_path, content, reason):
    repo = _repo(tmp_path, {
        "docs/adr/ADR-001-database.md": MNEME_ADR.replace("ADR-001", "ADR-010"),
        "docs/adr/ADR-001-bad.md": content,
    })

    adapter = MnemeAdapter()
    report = adapter.load_repository(repo)

    assert [d.id for d in report.decisions] == ["ADR-010"]
    assert [(s.path, s.reason) for s in adapter.skipped_adrs] == [
        ("docs/adr/ADR-001-bad.md", reason),
    ]


def test_duplicate_ids_exclude_both_files(tmp_path):
    repo = _repo(tmp_path, {
        "docs/adr/ADR-001-a.md": MNEME_ADR,
        "docs/adr/ADR-001-b.md": MNEME_ADR.replace("scope: database", "scope: storage"),
        "docs/adr/ADR-002-package-manager.md": MNEME_ADR_2,
    })

    adapter = MnemeAdapter()
    report = adapter.load_repository(repo)

    assert [d.id for d in report.decisions] == ["ADR-002"]
    assert {(s.path, s.reason) for s in adapter.skipped_adrs} == {
        ("docs/adr/ADR-001-a.md", "duplicate_id"),
        ("docs/adr/ADR-001-b.md", "duplicate_id"),
    }


def test_non_utf8_adr_is_reported(tmp_path):
    repo = _repo(tmp_path, {"docs/adr/ADR-002-package-manager.md": MNEME_ADR_2})
    (repo / "docs/adr/ADR-001-latin1.md").write_bytes("# Décision\n".encode("latin-1"))

    adapter = MnemeAdapter()
    report = adapter.load_repository(repo)

    assert [d.id for d in report.decisions] == ["ADR-002"]
    assert [(s.path, s.reason) for s in adapter.skipped_adrs] == [
        ("docs/adr/ADR-001-latin1.md", "unreadable"),
    ]


def test_supersession_cycle_excludes_the_cycle_only(tmp_path):
    a = MNEME_ADR.replace("id: ADR-001", "id: ADR-008").replace(
        "scope: database", "scope: database\nsupersedes: [ADR-009]")
    b = MNEME_ADR.replace("id: ADR-001", "id: ADR-009").replace(
        "scope: database", "scope: storage\nsupersedes: [ADR-008]")
    repo = _repo(tmp_path, {
        "docs/adr/ADR-008-a.md": a,
        "docs/adr/ADR-009-b.md": b,
        "docs/adr/ADR-002-package-manager.md": MNEME_ADR_2,
    })

    adapter = MnemeAdapter()
    report = adapter.load_repository(repo)

    assert [d.id for d in report.decisions] == ["ADR-002"]
    assert {(s.path, s.reason) for s in adapter.skipped_adrs} == {
        ("docs/adr/ADR-008-a.md", "supersession_cycle"),
        ("docs/adr/ADR-009-b.md", "supersession_cycle"),
    }
