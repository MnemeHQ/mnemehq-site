"""HTTP integration tests: real evaluator + Git fixture + fresh DB sessions."""
import copy
import io
import shutil
import zipfile
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from uuid import UUID, uuid4

import httpx
import pytest
from git import Actor, Repo
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Base
from app.db.session import get_db
from app.main import app
from app.services import audit_persistence
from app.services.comparison import comparison_engine


@pytest.fixture
async def workspace(tmp_path, monkeypatch):
    repo_path = tmp_path / "repository"
    shutil.copytree(Path(__file__).parents[3] / "tests/fixtures/audit-repo", repo_path)
    repo = Repo.init(repo_path)
    repo.index.add([str(p.relative_to(repo_path)) for p in repo_path.rglob("*")
                    if p.is_file() and ".git" not in p.parts])
    actor = Actor("Contract Test", "test@example.invalid")
    repo.index.commit("fixture", author=actor, committer=actor)

    def clone(url, source_ref=None):
        assert url == "https://github.com/example/contract-fixture"
        return Path(shutil.copytree(repo_path, tmp_path / str(uuid4())))

    monkeypatch.setattr(audit_persistence, "safe_clone_repo", clone)
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'contract.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async def database():
        async with sessions() as session:
            yield session

    app.dependency_overrides[get_db] = database
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client, repo, actor
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_reference_only_claude_http_response_is_valid(workspace):
    client, repo, actor = workspace
    root = Path(repo.working_tree_dir)
    (root / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("Never make external database calls from handlers.\n", encoding="utf-8")
    repo.index.add(["CLAUDE.md", "AGENTS.md"])
    repo.index.commit("reference-only instruction fixture", author=actor, committer=actor)
    response = await client.post("/api/v1/audit", data={
        "repository_url": "https://github.com/example/contract-fixture"})
    assert response.status_code == 201, response.text
    result = response.json()
    decisions = result['decisions']
    assert all(d['title'].strip() and d['requirement'].strip() for d in decisions)
    assert not any(d['source']['file'] == 'CLAUDE.md' for d in decisions)
    assert len([d for d in decisions if d['source']['file'] == 'AGENTS.md']) == 1


@pytest.mark.asyncio
async def test_exact_workspace_http_journey(workspace):
    client, repo, actor = workspace
    created = await client.post("/api/v1/audit", data={
        "repository_url": "https://github.com/example/contract-fixture"})
    assert created.status_code == 201, created.text
    result = created.json()
    UUID(result["audit_id"])
    UUID(result["project_id"])
    assert result["schema"] == "mneme.audit/v1"
    assert result["commit_sha"] == repo.head.commit.hexsha
    assert result["mneme_version"] == version("mneme-hq")
    assert datetime.fromisoformat(result["timestamp"]).tzinfo is not None
    assert result["decisions"]
    assert all(d.get("proposed_rule", {}).get("pattern", "").strip()
               for d in result["decisions"] if d["protection_classification"] == "Mneme-ready")
    assert len(result["decisions"]) == result["summary"]["decisions_discovered"]
    assert all(not Path(d["source"]["file"]).is_absolute() for d in result["decisions"])
    original = copy.deepcopy(result)
    pid, baseline_id = result["project_id"], result["audit_id"]
    before = (await client.get(f"/api/v1/projects/{pid}")).json()
    assert before["lifecycle"] == "ephemeral"
    assert before["baseline_audit_id"] is None

    # Exact JSON request sent by the UI, with no client-computed payload/scores.
    saved = await client.post("/api/v1/baselines", json={"audit_id": baseline_id})
    assert saved.status_code == 200, saved.text
    assert saved.json()["baseline_audit_id"] == baseline_id
    assert saved.json()["lifecycle"] == "saved"
    assert (await client.post("/api/v1/baselines", json={"audit_id": baseline_id})).status_code == 200
    assert (await client.get(f"/api/v1/audits/{baseline_id}")).json()["result"] == original

    # Each request receives a fresh session; no frontend memory involved.
    project = (await client.get(f"/api/v1/projects/{pid}")).json()
    assert len(project["audits"]) == 1
    assert datetime.fromisoformat(project["created_at"]).tzinfo is not None
    repo.index.commit("second revision", author=actor, committer=actor)
    rerun = await client.post(f"/api/v1/projects/{pid}/audits", json={
        "repository_url": "https://github.com/example/contract-fixture", "trigger_type": "re_audit"})
    assert rerun.status_code == 201, rerun.text
    latest_id = rerun.json()["id"]
    assert latest_id != baseline_id
    latest = (await client.get(f"/api/v1/audits/{latest_id}")).json()
    assert latest["commit_sha"] == repo.head.commit.hexsha != original["commit_sha"]
    assert latest["result"]["audit_id"] == latest_id
    assert latest["summary_payload"] == latest["result"]["summary"]
    project = (await client.get(f"/api/v1/projects/{pid}")).json()
    assert project["baseline_audit_id"] == baseline_id
    assert len(project["audits"]) == 2
    comparison = await client.get(f"/api/v1/projects/{pid}/compare")
    assert comparison.status_code == 200, comparison.text
    data = comparison.json()
    assert data["baseline_audit_id"] == baseline_id
    assert data["current_audit_id"] == latest_id
    assert data["baseline_summary"] == original["summary"]
    assert data["current_summary"] == latest["summary_payload"]
    assert data["current_protection_delta"] == 0
    assert data["summary"]["unchanged"] == len(data["decisions"])
    assert (await client.get(f"/api/v1/projects/{pid}/compare")).json() == data
    assert (await client.get(f"/api/v1/audits/{baseline_id}")).json()["result"] == original
    assert (await client.get(f"/api/v1/audits/{baseline_id}/export")).json() == original


@pytest.mark.asyncio
async def test_json_project_contract_and_rejected_server_paths(workspace):
    client, _, _ = workspace
    response = await client.post("/api/v1/projects", json={
        "name": "Contract test", "slug": "contract", "source_type": "github",
        "source_locator": "https://github.com/example/contract-fixture", "default_ref": None})
    assert response.status_code == 201, response.text
    pid = response.json()["id"]
    for forbidden in ("local_path", "zip_path", "commit_sha"):
        response = await client.post(f"/api/v1/projects/{pid}/audits", json={forbidden: "untrusted"})
        assert response.status_code == 422
    invalid = await client.post("/api/v1/audit", data={"repository_url": "http://localhost/private"})
    assert invalid.status_code == 400


@pytest.mark.asyncio
async def test_zip_contract_has_honest_provenance(workspace):
    client, _, _ = workspace
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("Makefile", "test:\n\techo test\n")
    response = await client.post("/api/v1/audit", files={"zip_file": ("sample.zip", archive.getvalue(), "application/zip")})
    assert response.status_code == 201, response.text
    assert response.json()["commit_sha"] == "not-applicable:archive"
    assert (await client.post("/api/v1/baselines", json={"audit_id": response.json()["audit_id"]})).status_code == 200


@pytest.mark.asyncio
async def test_real_zip_pipeline_provides_a_concrete_ready_guardrail(workspace):
    client, _, _ = workspace
    fixture = Path(__file__).parents[3] / "tests/fixtures/guardrail-ready/AGENTS.md"
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("AGENTS.md", fixture.read_text())
    response = await client.post("/api/v1/audit", files={"zip_file": ("guardrail-ready.zip", archive.getvalue(), "application/zip")})
    assert response.status_code == 201, response.text
    result = response.json()
    assert result["summary"]["mneme_ready_count"] == 1
    ready = next(d for d in result["decisions"] if d["protection_classification"] == "Mneme-ready")
    assert ready["proposed_rule"]["type"] == "FORBID_LITERAL"
    assert ready["proposed_rule"]["pattern"] == "sqlite3"
    assert ready["proposed_rule"]["description"].strip()
    assert result["commit_sha"] == "not-applicable:archive"


def test_comparison_preserves_authoritative_scores_not_row_reconstruction():
    # Deliberately distinct stored summaries prove comparison transports them.
    baseline = {"schema": "mneme.audit/v1", "summary": {"current_protection": .2, "identified_mneme_potential": .6}, "decisions": []}
    current = {"schema": "mneme.audit/v1", "summary": {"current_protection": .6, "identified_mneme_potential": .8}, "decisions": []}
    result = comparison_engine.compare(baseline, current, uuid4(), uuid4(), "a", "b", "0.6.0", "0.6.0", 1, 1)
    assert result.baseline_summary == baseline["summary"]
    assert result.current_summary == current["summary"]
    assert result.current_protection_delta == pytest.approx(.4)


def test_same_filename_at_different_paths_preserves_both_decisions(tmp_path):
    from types import SimpleNamespace
    from app.services.p12_adapter import collect_p12_inputs, build_protection_audit_response
    files = [{"name": "requirements.txt", "path": path, "content": "httpx", "lines": "1"}
             for path in ("api/requirements.txt", "tools/requirements.txt")]
    inputs = collect_p12_inputs(SimpleNamespace(decisions=[]), [], [], files, tmp_path)
    result = build_protection_audit_response("fixture", None, "test", "0.6.0", inputs, []).model_dump(mode="json")
    assert len({d["id"] for d in result["decisions"]}) == 2
    compared = comparison_engine.compare(result, result, uuid4(), uuid4(), "a", "a", "0.6.0", "0.6.0", 1, 1)
    assert compared.summary["unchanged"] == len(compared.decisions) == 2
    assert result["summary"]["guidance_count"] == 2
