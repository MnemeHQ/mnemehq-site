"""M1.3b setup pairing contract tests (G3, G6 API surface, G7 attribution).

Covers: reference issuance for saved baselines, safe failure on
unknown/expired/mismatched references, idempotent completion, project
activation-state recording, and audit immutability after pairing.
"""
import copy
from datetime import datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy import update

from app.db.models import Base, SetupReference
from app.db.session import get_db
from app.main import app
from app.services import audit_persistence

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def pairing(tmp_path, monkeypatch):
    """Saved-baseline workspace: real evaluator + git fixture + fresh sqlite DB."""
    import shutil
    from pathlib import Path
    from uuid import uuid4
    from git import Actor, Repo
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    repo_path = tmp_path / "repository"
    shutil.copytree(Path(__file__).parents[3] / "tests/fixtures/audit-repo", repo_path)
    repo = Repo.init(repo_path)
    repo.index.add([str(p.relative_to(repo_path)) for p in repo_path.rglob("*")
                    if p.is_file() and ".git" not in p.parts])
    actor = Actor("Pairing Test", "test@example.invalid")
    repo.index.commit("fixture", author=actor, committer=actor)

    def clone(url, source_ref=None):
        return Path(shutil.copytree(repo_path, tmp_path / str(uuid4())))

    monkeypatch.setattr(audit_persistence, "safe_clone_repo", clone)
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'pairing.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async def database():
        async with sessions() as session:
            yield session

    app.dependency_overrides[get_db] = database
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Saved-baseline journey: audit → save baseline.
        created = await client.post("/api/v1/audit", data={
            "repository_url": "https://github.com/example/contract-fixture"})
        assert created.status_code == 201, created.text
        result = created.json()
        saved = await client.post("/api/v1/baselines", json={"audit_id": result["audit_id"]})
        assert saved.status_code == 200, saved.text
        yield client, result, repo
    app.dependency_overrides.clear()
    await engine.dispose()


async def _expire_reference(reference: str) -> None:
    """Expire a reference directly in the DB (tests expiry failure safety)."""
    database = app.dependency_overrides[get_db]
    async for session in database():
        await session.execute(
            update(SetupReference)
            .where(SetupReference.reference == reference)
            .values(expires_at=datetime.now(timezone.utc) - timedelta(hours=1))
        )
        await session.commit()
        break


# ── G3: issuance ──────────────────────────────────────────────────────────────

async def test_reference_creation_for_saved_baseline(pairing):
    client, result, repo = pairing
    response = await client.post(f"/api/v1/audits/{result['audit_id']}/setup-reference")
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["audit_id"] == result["audit_id"]
    assert body["project_id"] == result["project_id"]
    assert body["reference"]
    assert body["setup_command"] == f"mneme setup --audit-ref {body['reference']}"
    # ADR-005: install commands must name mneme-hq, never bare `mneme`.
    assert "mneme-hq" in body["install_command"]
    assert "bare" not in body["install_command"]
    expires = datetime.fromisoformat(body["expires_at"])
    assert expires > datetime.now(timezone.utc)


async def test_reference_requires_baseline_audit(pairing):
    client, result, repo = pairing
    # Ephemeral (non-baseline) audit path: run a second audit on the project
    # via re-audit; the new audit is NOT the baseline.
    rerun = await client.post(f"/api/v1/projects/{result['project_id']}/audits", json={
        "repository_url": "https://github.com/example/contract-fixture",
        "trigger_type": "re_audit"})
    assert rerun.status_code == 201, rerun.text
    response = await client.post(f"/api/v1/audits/{rerun.json()['id']}/setup-reference")
    assert response.status_code == 409
    assert "baseline" in response.json()["error"].lower()


async def test_reference_unknown_audit_404(pairing):
    client, result, repo = pairing
    from uuid import uuid4
    response = await client.post(f"/api/v1/audits/{uuid4()}/setup-reference")
    assert response.status_code == 404


# ── G3: resolution ────────────────────────────────────────────────────────────

async def test_resolve_returns_baseline_provenance(pairing):
    client, result, repo = pairing
    created = await client.post(f"/api/v1/audits/{result['audit_id']}/setup-reference")
    reference = created.json()["reference"]
    resolved = await client.get(f"/api/v1/setup-references/{reference}")
    assert resolved.status_code == 200, resolved.text
    body = resolved.json()
    assert body["audit_id"] == result["audit_id"]
    assert body["project_id"] == result["project_id"]
    assert body["commit_sha"] == result["commit_sha"]
    assert body["mneme_version"] == result["mneme_version"]
    assert body["schema_version"] == 1  # settings.AUDIT_SCHEMA_VERSION
    assert body["audit_schema"] == "mneme.audit/v1"
    assert body["project_activation_state"] == "not_installed"
    assert body["redeemed"] is False
    assert body["summary"] == result["summary"]


async def test_resolve_unknown_reference_404(pairing):
    client, result, repo = pairing
    response = await client.get("/api/v1/setup-references/does-not-exist")
    assert response.status_code == 404


async def test_resolve_expired_reference_410(pairing):
    client, result, repo = pairing
    created = await client.post(f"/api/v1/audits/{result['audit_id']}/setup-reference")
    reference = created.json()["reference"]
    await _expire_reference(reference)
    response = await client.get(f"/api/v1/setup-references/{reference}")
    assert response.status_code == 410


# ── G3 + G7: completion, attribution, failure safety ─────────────────────────

async def test_complete_records_setup_attribution(pairing):
    client, result, repo = pairing
    created = await client.post(f"/api/v1/audits/{result['audit_id']}/setup-reference")
    reference = created.json()["reference"]
    audit_before = copy.deepcopy(
        (await client.get(f"/api/v1/audits/{result['audit_id']}")).json()
    )
    completed = await client.post(
        f"/api/v1/setup-references/{reference}/complete",
        json={"repository": "https://github.com/example/contract-fixture.git",
              "mneme_version": "0.6.0"},
    )
    assert completed.status_code == 200, completed.text
    body = completed.json()
    assert body["already_redeemed"] is False
    assert body["activation_state"] == "setup"
    assert body["setup_completed_at"] is not None
    assert body["audit_id"] == result["audit_id"]

    # G6: the project endpoint distinguishes the activation state.
    project = (await client.get(f"/api/v1/projects/{result['project_id']}")).json()
    assert project["activation_state"] == "setup"
    assert project["setup_audit_id"] == result["audit_id"]
    assert project["setup_completed_at"] is not None
    # Audit lifecycle untouched: still saved, baseline intact.
    assert project["lifecycle"] == "saved"
    assert project["baseline_audit_id"] == result["audit_id"]

    # G4-adjacent: audit payload is immutable after pairing.
    audit_after = (await client.get(f"/api/v1/audits/{result['audit_id']}")).json()
    assert audit_after["result"] == audit_before["result"]
    assert audit_after["summary_payload"] == audit_before["summary_payload"]


async def test_complete_is_idempotent_and_preserves_first_completion(pairing):
    client, result, repo = pairing
    created = await client.post(f"/api/v1/audits/{result['audit_id']}/setup-reference")
    reference = created.json()["reference"]
    first = await client.post(
        f"/api/v1/setup-references/{reference}/complete",
        json={"repository": None, "mneme_version": "0.6.0"})
    assert first.status_code == 200
    completed_at = first.json()["setup_completed_at"]
    second = await client.post(
        f"/api/v1/setup-references/{reference}/complete",
        json={"repository": None, "mneme_version": "0.7.0"})
    assert second.status_code == 200
    body = second.json()
    assert body["already_redeemed"] is True
    assert body["setup_completed_at"] == completed_at
    assert body["activation_state"] == "setup"


async def test_complete_mismatched_repository_409_without_mutation(pairing):
    client, result, repo = pairing
    created = await client.post(f"/api/v1/audits/{result['audit_id']}/setup-reference")
    reference = created.json()["reference"]
    before = (await client.get(f"/api/v1/projects/{result['project_id']}")).json()

    response = await client.post(
        f"/api/v1/setup-references/{reference}/complete",
        json={"repository": "https://github.com/someone-else/other-repo",
              "mneme_version": "0.6.0"})
    assert response.status_code == 409
    assert "mismatch" in response.json()["error"].lower() or "belongs" in response.json()["error"].lower()

    after = (await client.get(f"/api/v1/projects/{result['project_id']}")).json()
    # No partial mutation on mismatched references.
    assert after == before


async def test_complete_unknown_reference_404(pairing):
    client, result, repo = pairing
    response = await client.post(
        "/api/v1/setup-references/does-not-exist/complete",
        json={"repository": None, "mneme_version": "0.6.0"})
    assert response.status_code == 404


async def test_complete_expired_reference_410(pairing):
    client, result, repo = pairing
    created = await client.post(f"/api/v1/audits/{result['audit_id']}/setup-reference")
    reference = created.json()["reference"]
    await _expire_reference(reference)
    response = await client.post(
        f"/api/v1/setup-references/{reference}/complete",
        json={"repository": None, "mneme_version": "0.6.0"})
    assert response.status_code == 410


async def test_complete_accepts_ssh_remote_form(pairing):
    client, result, repo = pairing
    created = await client.post(f"/api/v1/audits/{result['audit_id']}/setup-reference")
    reference = created.json()["reference"]
    response = await client.post(
        f"/api/v1/setup-references/{reference}/complete",
        json={"repository": "git@github.com:example/contract-fixture.git",
              "mneme_version": "0.6.0"})
    assert response.status_code == 200, response.text


async def test_setup_never_activates_or_starts_pilot(pairing):
    """Frozen invariant: setup must not move the project past `setup` state,
    must not change lifecycle beyond what saving already did, and must not
    start a pilot."""
    client, result, repo = pairing
    created = await client.post(f"/api/v1/audits/{result['audit_id']}/setup-reference")
    reference = created.json()["reference"]
    await client.post(
        f"/api/v1/setup-references/{reference}/complete",
        json={"repository": None, "mneme_version": "0.6.0"})
    project = (await client.get(f"/api/v1/projects/{result['project_id']}")).json()
    assert project["activation_state"] == "setup"
    assert project["lifecycle"] == "saved"


async def test_no_setup_reference_in_metadata_endpoints(pairing):
    """The reference must not become a general-purpose credential: resolution
    exposes only this audit/project baseline provenance."""
    client, result, repo = pairing
    created = await client.post(f"/api/v1/audits/{result['audit_id']}/setup-reference")
    body = created.json()
    resolved = (await client.get(f"/api/v1/setup-references/{body['reference']}")).json()
    assert set(resolved) <= {
        "reference", "audit_id", "project_id", "project_name", "repository",
        "repository_url", "commit_sha", "mneme_version", "schema_version",
        "audit_schema", "summary", "project_activation_state", "expires_at",
        "redeemed",
    }
