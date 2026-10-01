"""Tests for scripts/check_audit_lock.py (the production resolution guard)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_audit_lock as guard  # noqa: E402
from lock_audit_requirements import requirements_sha256  # noqa: E402

REQUIREMENTS = "fastapi>=0.111.0\nsqlalchemy[asyncio]>=2.0.0\nmneme-hq>=0.8.0\n"


def write(tmp_path: Path, lock_body: str, requirements: str = REQUIREMENTS,
          digest: str | None = None, engine: str = "0.9.2") -> tuple[Path, Path]:
    req = tmp_path / "requirements.txt"
    req.write_text(requirements, encoding="utf-8")
    lock = tmp_path / "requirements.lock"
    header = (
        f"# requirements-sha256: {digest or requirements_sha256(req)}\n"
        f"# mneme-hq: {engine}\n"
    )
    lock.write_text(header + lock_body, encoding="utf-8")
    return req, lock


GOOD = "fastapi==0.115.0\nSQLAlchemy==2.0.36\ngreenlet==3.1.1\nmneme-hq==0.9.2\n"


def test_valid_lock_passes_and_reports_engine(tmp_path):
    req, lock = write(tmp_path, GOOD)
    errors, pins = guard.check_static(req, lock)
    assert errors == []
    assert pins["mneme-hq"] == "0.9.2"
    assert pins["sqlalchemy"] == "2.0.36"


def test_lock_may_lag_newer_engine_releases(tmp_path):
    # 0.8.0 satisfies the floor; being behind the newest release is allowed.
    req, lock = write(tmp_path, GOOD.replace("0.9.2", "0.8.0"), engine="0.8.0")
    assert guard.check_static(req, lock)[0] == []


def test_stale_lock_is_rejected_when_requirements_change(tmp_path):
    req, lock = write(tmp_path, GOOD)
    req.write_text(REQUIREMENTS + "httpx>=0.27.0\n", encoding="utf-8")
    errors, _ = guard.check_static(req, lock)
    assert any("not resolved from the current requirements.txt" in e for e in errors)
    assert any("httpx is required but not locked" in e for e in errors)


def test_hash_ignores_checkout_line_endings(tmp_path):
    req, lock = write(tmp_path, GOOD)
    req.write_bytes(REQUIREMENTS.replace("\n", "\r\n").encode("utf-8"))
    assert guard.check_static(req, lock)[0] == []


def test_locked_version_below_floor_is_rejected(tmp_path):
    req, lock = write(tmp_path, GOOD.replace("mneme-hq==0.9.2", "mneme-hq==0.7.0"), engine="0.7.0")
    errors, _ = guard.check_static(req, lock)
    assert any("below the declared floor" in e for e in errors)


def test_non_exact_lock_entry_is_rejected(tmp_path):
    req, lock = write(tmp_path, GOOD + "uvicorn>=0.30.0\n")
    errors, _ = guard.check_static(req, lock)
    assert any("not an exact name==version pin" in e for e in errors)


def test_header_engine_must_match_pin(tmp_path):
    req, lock = write(tmp_path, GOOD, engine="0.9.1")
    errors, _ = guard.check_static(req, lock)
    assert any("lock header reports mneme-hq" in e for e in errors)


def test_installed_check_flags_mismatch_and_missing():
    errors = guard.check_installed({"pytest": "0.0.0", "definitely-not-installed": "1.0"})
    assert any("pytest is installed at" in e for e in errors)
    assert any("definitely-not-installed==1.0 is locked but not installed" in e for e in errors)
