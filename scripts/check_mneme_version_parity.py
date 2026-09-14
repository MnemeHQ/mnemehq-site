#!/usr/bin/env python
"""Guard the audit backend's Mneme engine dependency (dynamic floor model).

Root cause this guards (P0, 2026-09-12): production served Audit responses
with ``mneme_version: 0.6.0`` while the supported DP/local workflow used
0.7.0, because audit/backend/requirements.txt held a manually maintained
exact pin (``mneme-hq==0.6.0``) that nothing bumped when the engine
released. Nothing failed; the drift was only visible in a partner's audit
export.

Model now enforced (site review, 2026-09-13):

1. audit/backend/requirements.txt must consume a published Mneme release
   DYNAMICALLY through an explicit minimum floor (``mneme-hq>=X.Y.Z``).
   A manually maintained exact ``==`` pin is the failure mode itself and
   is rejected.
2. The declared floor must be satisfiable: it may not demand an
   unpublished engine (floor <= latest release served by PyPI).
3. The EXACT resolved version is recorded at validation/build time from
   the installed distribution (``importlib.metadata.version``) — the
   deployment reproduces it in the image, and every Audit result already
   carries it as ``mneme_version``. ``>=`` is never assumed to mean the
   running engine IS the floor.

Run in CI after ``pip install -r audit/backend/requirements.txt``.
Network is used only to read PyPI's public JSON index.
"""
from __future__ import annotations

import importlib.metadata
import json
import re
import sys
import urllib.request
from pathlib import Path

REQUIREMENTS_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parents[1] / "audit" / "backend" / "requirements.txt"
)
PYPI_INDEX = "https://pypi.org/pypi/mneme-hq/json"
PYPI_TIMEOUT_SECONDS = 30


def parse_version(value: str) -> tuple[int, ...]:
    parts = tuple(int(piece) for piece in re.findall(r"\d+", value))
    return parts or (0,)


def read_requirement() -> tuple[tuple[int, ...], str]:
    for line in REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("mneme-hq"):
            continue
        match = re.fullmatch(r"mneme-hq>=(\d+(?:\.\d+)*)", stripped)
        if not match:
            print(
                f"FAIL: {REQUIREMENTS_PATH} must consume mneme-hq through a "
                f"dynamic floor (mneme-hq>=X.Y.Z); found {stripped!r}. "
                f"An exact '==' pin is the production-drift failure mode "
                f"this guard exists to prevent."
            )
            raise SystemExit(1)
        return parse_version(match.group(1)), stripped
    print(f"FAIL: {REQUIREMENTS_PATH} has no mneme-hq requirement")
    raise SystemExit(1)


def latest_published() -> tuple[int, ...]:
    with urllib.request.urlopen(PYPI_INDEX, timeout=PYPI_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return parse_version(payload["info"]["version"])


def resolved_version() -> str:
    try:
        return importlib.metadata.version("mneme-hq")
    except importlib.metadata.PackageNotFoundError:
        return ""


def main() -> int:
    if not REQUIREMENTS_PATH.exists():
        print(f"FAIL: requirements file not found: {REQUIREMENTS_PATH}")
        return 1
    floor, floor_text = read_requirement()
    try:
        published = latest_published()
    except (OSError, ValueError, KeyError) as exc:
        print(f"FAIL: could not read the published mneme-hq floor: {exc}")
        return 1
    if floor > published:
        print(
            f"FAIL: {floor_text} demands mneme-hq "
            f"{'.'.join(map(str, floor))}, but the latest published release "
            f"is {'.'.join(map(str, published))}. An unsatisfiable floor "
            f"must never be declared."
        )
        return 1
    resolved = resolved_version()
    if not resolved:
        print(
            "FAIL: mneme-hq is not installed in this environment; install "
            "audit/backend/requirements.txt before running this guard so "
            "the exact resolved version can be recorded."
        )
        return 1
    print(
        f"OK: {floor_text} is a satisfiable dynamic floor (latest published: "
        f"{'.'.join(map(str, published))})"
    )
    print(f"RESOLVED_MNEME_HQ_VERSION={resolved}")
    if parse_version(resolved) < floor:
        print(
            f"FAIL: resolved mneme-hq {resolved} is below the declared floor "
            f"{'.'.join(map(str, floor))}"
        )
        return 1
    print("OK: resolved version satisfies the declared floor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
