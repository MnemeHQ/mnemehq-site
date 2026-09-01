import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.api import audit
from app.main import app
from app.services.safe_extract import (
    SafeExtractionError,
    _materialize_safe_repo_symlinks,
)


def _create_symlink(target: Path, link: Path, *, target_is_directory: bool = False) -> None:
    try:
        os.symlink(target, link, target_is_directory=target_is_directory)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"Symlinks are unavailable in this environment: {exc}")


def test_materializes_internal_file_symlink(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "AGENTS.md"
    target.write_text("# Agent instructions\n", encoding="utf-8")
    link = repo / "CLAUDE.md"
    _create_symlink(target, link)

    _materialize_safe_repo_symlinks(repo)

    assert not link.is_symlink()
    assert link.read_text(encoding="utf-8") == target.read_text(encoding="utf-8")


def test_rejects_symlink_that_escapes_repository(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")
    link = repo / "escape.md"
    _create_symlink(outside, link)

    with pytest.raises(SafeExtractionError, match="unsafe symlink"):
        _materialize_safe_repo_symlinks(repo)


def test_removes_internal_directory_symlink(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "docs"
    target.mkdir()
    (target / "architecture.md").write_text("architecture", encoding="utf-8")
    link = repo / "docs-alias"
    _create_symlink(target, link, target_is_directory=True)

    _materialize_safe_repo_symlinks(repo)

    assert target.is_dir()
    assert not link.exists()


def test_api_returns_structured_error_for_unsafe_repository(monkeypatch):
    async def reject_repository(**_kwargs):
        raise SafeExtractionError("Repository contains unsafe symlink: escape.md")

    monkeypatch.setattr(audit.audit_service, "analyze_repository", reject_repository)

    with TestClient(app) as client:
        response = client.post(
            "/api/audit",
            data={"repository_url": "https://github.com/example/repository"},
            headers={"Origin": "https://mnemehq.com"},
        )

    assert response.status_code == 422
    assert response.json() == {
        "success": False,
        "error": "Repository contains unsafe symlink: escape.md",
    }
    assert response.headers["access-control-allow-origin"] == "https://mnemehq.com"
