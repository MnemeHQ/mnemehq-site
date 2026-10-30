"""Contract tests for the stateless single-ADR check (POST /api/v1/check).

Covers the 2026-10-29 pilot conditions: no stored text and no body in logs,
the same text gets the same result whatever its file name, Protected is
never returned, and there is no listing or lookup route.
"""
import logging
import tempfile
from pathlib import Path

import httpx
import pytest

from app.api import check as check_api
from app.db.session import get_db
from app.main import app
from app.services import adr_check
from app.services.adr_check import check_adr


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

NYGARD_ADR = """# ADR-003: Storage engine

## Status
Accepted

## Context
Services need durable storage that every team can operate.

## Decision
The service must not use sqlite for persistent data.
Do not add MongoDB to any service.
"""

VAGUE_ADR = """# 0007. Module size

## Decision
We aim to keep modules small and easy to read where it makes sense.
"""

# Same body as MNEME_ADR with the frontmatter removed: the repository Audit
# raised ADRParseError on this when it was named ADR-*.md.
FRONTMATTERLESS_ADR = MNEME_ADR.split("---\n", 2)[2]

SHORT_RULE_ADR = """# ADR-009: Databases

## Decision
Never use mongodb.
"""

MADR_ADR = """# Use PostgreSQL for persistent data

## Context and Problem Statement
Services need one durable store that the platform team can operate.

## Decision Outcome
Chosen option: PostgreSQL. Services must not use sqlite for persistent data.
"""

ALL_ADRS = [MNEME_ADR, NYGARD_ADR, VAGUE_ADR, FRONTMATTERLESS_ADR, SHORT_RULE_ADR, MADR_ADR]

# File names and folders that change the repository Audit's channels.
FILENAMES = [
    "ADR-001-database-choice.md",
    "adr/0003-storage.md",
    "docs/adr/0003-storage.md",
    "docs/decisions/database.md",
    "CLAUDE.md",
    "examples/sample-adr.md",
    "",
]


@pytest.fixture
async def client():
    def no_database():
        raise AssertionError("the check endpoint must not open a database session")
        yield  # pragma: no cover

    check_api.limiter.reset()
    app.dependency_overrides[get_db] = no_database
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
    check_api.limiter.reset()


def _rows(payload):
    return [(r["statement"], r["line_start"], r["classification"],
             tuple(sorted((r["proposed_rule"] or {}).items())))
            for r in payload["rows"]]


# --- classification ---------------------------------------------------------

def test_prose_adr_gets_per_statement_rows_with_line_numbers():
    result = check_adr(NYGARD_ADR).to_dict()
    assert result["format"] == "prose"
    lines = {r["line_start"]: r for r in result["rows"]}
    assert lines[10]["statement"] == "The service must not use sqlite for persistent data."
    assert lines[10]["heading"] == "Decision"
    assert lines[10]["classification"] == "Requires modelling"
    assert lines[11]["classification"] == "Requires modelling"


def test_rows_are_never_duplicated():
    for text in ALL_ADRS:
        rows = _rows(check_adr(text).to_dict())
        assert len(rows) == len(set(rows)), text


def test_short_rule_is_not_dropped():
    # The loose-ADR channel drops lines under 20 characters; the check must not.
    result = check_adr(SHORT_RULE_ADR).to_dict()
    assert [r["statement"] for r in result["rows"]] == ["Never use mongodb."]
    assert result["rows"][0]["classification"] != "Guidance"


def test_mneme_format_protected_is_capped_to_mneme_ready():
    result = check_adr(MNEME_ADR).to_dict()
    assert result["format"] == "mneme"
    assert len(result["rows"]) == 1
    row = result["rows"][0]
    assert row["classification"] == "Mneme-ready"
    assert row["protected_capped"] is True
    assert row["proposed_rule"] == {"type": "FORBID_LITERAL", "pattern": "sqlite"}
    assert result["summary"]["protected_capped"] is True


def test_protected_never_appears_for_any_input():
    for text in ALL_ADRS:
        result = check_adr(text).to_dict()
        assert "Protected" not in {r["classification"] for r in result["rows"]}
        assert "protected_count" not in result["summary"]


def test_madr_decision_outcome_is_read():
    result = check_adr(MADR_ADR).to_dict()
    assert result["format"] == "prose"
    rule = [r for r in result["rows"] if "must not use sqlite" in r["statement"]]
    assert rule and rule[0]["heading"] == "Decision Outcome"
    assert rule[0]["classification"] == "Requires modelling"


def test_temp_files_are_removed_when_the_check_fails(monkeypatch):
    created = []
    real = tempfile.mkdtemp

    def recording(*args, **kwargs):
        path = real(*args, **kwargs)
        created.append(Path(path))
        return path

    def explode(root):
        raise RuntimeError("discovery failed")

    monkeypatch.setattr(adr_check.tempfile, "mkdtemp", recording)
    monkeypatch.setattr(adr_check, "discover_architecture_statements", explode)
    with pytest.raises(RuntimeError):
        check_adr(NYGARD_ADR)
    assert created and not any(p.exists() for p in created)


def test_frontmatterless_adr_does_not_crash():
    result = check_adr(FRONTMATTERLESS_ADR).to_dict()
    assert result["format"] == "prose"


def test_malformed_frontmatter_falls_back_to_statements():
    broken = "---\nid: ADR-005\nstatus: [accepted\n---\n\n## Decision\nThe API must not call the database directly.\n"
    result = check_adr(broken).to_dict()
    assert result["format"] == "prose"
    assert any("must not call the database" in r["statement"] for r in result["rows"])


def test_neutral_lines_are_listed_not_hidden():
    result = check_adr(NYGARD_ADR).to_dict()
    unclassified = {u["line"]: u["text"] for u in result["unclassified_lines"]}
    assert unclassified == {4: "Accepted"}
    # Headings are structure, not unread content.
    assert not any(t.startswith("#") for t in unclassified.values())
    assert result["summary"]["unclassified_count"] == len(unclassified)


def test_result_is_deterministic():
    for text in ALL_ADRS:
        assert check_adr(text).to_dict() == check_adr(text).to_dict()


def test_temp_files_are_removed(monkeypatch):
    created = []
    real = tempfile.mkdtemp

    def recording(*args, **kwargs):
        path = real(*args, **kwargs)
        created.append(Path(path))
        return path

    monkeypatch.setattr(adr_check.tempfile, "mkdtemp", recording)
    for text in ALL_ADRS:
        check_adr(text)
    assert created and not any(p.exists() for p in created)


# --- filename invariance (regression) --------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("text", ALL_ADRS)
async def test_same_text_same_result_whatever_the_filename(client, text):
    baseline = await client.post("/api/v1/check", json={"kind": "adr", "text": text})
    assert baseline.status_code == 200
    expected = baseline.json()
    for filename in FILENAMES:
        response = await client.post(
            "/api/v1/check",
            json={"kind": "adr", "text": text, "filename": filename, "path": filename},
        )
        assert response.status_code == 200
        assert response.json() == expected, filename


def test_placement_never_depends_on_caller_input():
    # Only the text's format picks the path; both paths are constants.
    assert adr_check.MNEME_FORMAT_PATH == "adr/ADR-000-pasted.md"
    assert adr_check.PROSE_PATH == "docs/pasted-adr.md"


# --- HTTP contract ----------------------------------------------------------

@pytest.mark.asyncio
async def test_http_check_returns_capped_result(client):
    response = await client.post("/api/v1/check", json={"text": MNEME_ADR})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["engine"] == "mneme-hq"
    assert body["rows"][0]["classification"] == "Mneme-ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("payload, status", [
    ({"text": ""}, 422),
    ({"text": "   \n"}, 422),
    ({}, 422),
    ({"text": 42}, 422),
    ({"kind": "instructions", "text": "Never use mongodb."}, 400),
    (["not", "an", "object"], 400),
])
async def test_http_rejects_bad_input(client, payload, status):
    response = await client.post("/api/v1/check", json=payload)
    assert response.status_code == status
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_http_rejects_non_json(client):
    response = await client.post("/api/v1/check", content=b"\xff\xfe not json")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_http_enforces_size_limit(client):
    response = await client.post("/api/v1/check", json={"text": "a" * (64 * 1024 + 1)})
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_parser_failure_becomes_422_without_logging_text(client, monkeypatch, caplog):
    marker = "SECRET-ADR-MARKER-9f3c"

    def explode(text):
        raise RuntimeError(f"could not parse {text}")

    monkeypatch.setattr(check_api, "check_adr", explode)
    with caplog.at_level(logging.DEBUG):
        response = await client.post("/api/v1/check", json={"text": f"Use {marker} everywhere."})
    assert response.status_code == 422
    assert marker not in response.text
    assert not any(marker in r.getMessage() or (r.exc_text or "").find(marker) >= 0
                   for r in caplog.records)


@pytest.mark.asyncio
@pytest.mark.parametrize("base", [NYGARD_ADR, MNEME_ADR], ids=["prose", "mneme-format"])
async def test_request_body_is_never_logged(client, caplog, base):
    marker = "SECRET-ADR-MARKER-41ab"
    text = base + f"\nThe service must not call {marker} directly.\n"
    with caplog.at_level(logging.DEBUG):
        response = await client.post("/api/v1/check", json={"text": text})
    assert response.status_code == 200
    check_logs = [r for r in caplog.records if r.name == "app.check"]
    assert check_logs, "the check should log kind, size bucket, status and duration"
    for record in caplog.records:
        assert marker not in record.getMessage()
        assert marker not in str(record.args)
        assert "sqlite" not in record.getMessage()


@pytest.mark.asyncio
async def test_no_listing_or_lookup_route(client):
    paths = {p: sorted(ops) for p, ops in app.openapi()["paths"].items()
             if p.startswith("/api/v1/check")}
    assert paths == {"/api/v1/check": ["post"]}
    assert (await client.get("/api/v1/check")).status_code == 405
    assert (await client.get("/api/v1/check/anything")).status_code == 404


def test_endpoint_has_no_database_dependency():
    route = next(r for r in check_api.router.routes if r.path == "/api/v1/check")

    def calls(dependant):
        for dep in dependant.dependencies:
            yield dep.call
            yield from calls(dep)

    assert get_db not in set(calls(route.dependant))


@pytest.mark.asyncio
async def test_rate_limit_per_client(client):
    for _ in range(check_api.PER_CLIENT_LIMIT):
        ok = await client.post("/api/v1/check", json={"text": VAGUE_ADR},
                               headers={"x-forwarded-for": "198.51.100.7"})
        assert ok.status_code == 200
    limited = await client.post("/api/v1/check", json={"text": VAGUE_ADR},
                                headers={"x-forwarded-for": "198.51.100.7"})
    assert limited.status_code == 429
    other = await client.post("/api/v1/check", json={"text": VAGUE_ADR},
                              headers={"x-forwarded-for": "198.51.100.8"})
    assert other.status_code == 200


def test_rate_limit_window_and_global_cap():
    limiter = check_api.RateLimiter(per_client=2, total=3, window=60)
    assert limiter.allow("a", now=0) and limiter.allow("a", now=1)
    assert not limiter.allow("a", now=2)
    assert limiter.allow("b", now=2)
    assert not limiter.allow("c", now=3)  # global cap
    assert limiter.allow("a", now=61.5)  # window slid


def test_spoofed_forwarded_prefix_is_ignored():
    class Req:
        headers = {"x-forwarded-for": "203.0.113.1, 198.51.100.9"}
        client = None

    assert check_api.client_key(Req()) == "198.51.100.9"
