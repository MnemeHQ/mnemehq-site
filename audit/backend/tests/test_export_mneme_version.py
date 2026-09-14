"""The audit export/response must expose the running engine version.

P0 finding: production's Audit export carried "Mneme: 0.6.0" against a
0.7.0 DP/local workflow, and the mismatch was only discoverable because the
version happened to be in the export. This test pins that the canonical
mneme.audit/v1 response and the markdown export both carry the installed
mneme-hq version.
"""
import shutil
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from git import Actor, Repo
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Base
from app.db.session import get_db
from app.main import app
from app.services import audit_persistence


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
        yield client, repo
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_response_and_markdown_export_carry_engine_version(workspace):
    client, repo = workspace
    created = await client.post("/api/v1/audit", data={
        "repository_url": "https://github.com/example/contract-fixture"})
    assert created.status_code == 201, created.text
    result = created.json()
    expected = version("mneme-hq")

    # Response metadata: the running engine version, always present.
    assert result["mneme_version"] == expected

    # Markdown export: the human-facing provenance line.
    audit_id = result["audit_id"]
    export = await client.get(f"/api/v1/audits/{audit_id}/export?format=markdown")
    assert export.status_code == 200
    assert f"Mneme: {expected}" in export.text
