#!/usr/bin/env python
"""Generate audit/backend/requirements.lock, the production resolution.

audit/backend/requirements.txt stays the dynamic compatibility floor
(``name>=X.Y.Z``). This script resolves it once, in a clean virtual
environment, and writes every resolved distribution as an exact
``name==version`` pip constraint. The production Docker image installs with
``pip install -r requirements.txt -c requirements.lock``, so the Python
dependency graph of the image is reproducible and an Audit engine upgrade is
an explicit, reviewed change to this file.

Scope: Python dependencies only. The base image, apt packages and pip itself
still float, so the container build as a whole is not fully reproducible.

The resolution is platform-specific. Run it where the image is built: Linux,
CPython 3.12. From the repository root:

    docker run --rm -v "$PWD:/src" -w /src python:3.12-slim sh -c \
      "apt-get update -qq && apt-get install -y -qq git gcc >/dev/null && \
       python scripts/lock_audit_requirements.py"
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import platform
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "audit" / "backend" / "requirements.txt"
LOCK = ROOT / "audit" / "backend" / "requirements.lock"
REQUIRED_PYTHON = (3, 12)


def requirements_sha256(path: Path = REQUIREMENTS) -> str:
    """Hash requirements.txt independently of checkout line endings."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").strip() + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def resolve() -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        venv.create(tmp, with_pip=True)
        python = Path(tmp) / "bin" / "python"
        subprocess.run(
            [str(python), "-m", "pip", "install", "--quiet", "--no-cache-dir",
             "-r", str(REQUIREMENTS)],
            check=True,
        )
        frozen = subprocess.run(
            [str(python), "-m", "pip", "freeze"],
            check=True, capture_output=True, text=True,
        ).stdout
    lines = sorted((line.strip() for line in frozen.splitlines() if line.strip()),
                   key=str.lower)
    inexact = [line for line in lines if "==" not in line or " @ " in line]
    if inexact:
        raise SystemExit(f"FAIL: resolution contains non-exact entries: {inexact}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-any-platform", action="store_true",
        help="resolve on a platform other than Linux / CPython 3.12 (not for production)",
    )
    args = parser.parse_args(argv)

    on_target = sys.platform.startswith("linux") and sys.version_info[:2] == REQUIRED_PYTHON
    if not on_target and not args.allow_any_platform:
        print(
            "FAIL: the production resolution must be generated on Linux with "
            f"CPython {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} (found {sys.platform}, "
            f"{platform.python_version()}). See the docker command in this script's docstring."
        )
        return 1

    lines = resolve()
    engine = next((l.split("==", 1)[1] for l in lines if l.lower().startswith("mneme-hq==")), "")
    if not engine:
        print("FAIL: mneme-hq is missing from the resolution")
        return 1

    header = [
        "# Production resolution for the Audit backend image. GENERATED - do not edit.",
        "# Used only as pip constraints: pip install -r requirements.txt -c requirements.lock",
        "# requirements.txt remains the dynamic compatibility floor.",
        "# Regenerate with scripts/lock_audit_requirements.py (Linux, CPython 3.12).",
        "# Covers Python dependencies only; base image, apt packages and pip still float.",
        f"# generated: {_dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%d')}",
        f"# python: {platform.python_version()}",
        f"# platform: {sys.platform} {platform.machine()}",
        f"# requirements-sha256: {requirements_sha256()}",
        f"# mneme-hq: {engine}",
    ]
    LOCK.write_text("\n".join(header + lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {LOCK.relative_to(ROOT).as_posix()} ({len(lines)} distributions)")
    print(f"LOCKED_MNEME_HQ_VERSION={engine}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
