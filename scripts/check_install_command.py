#!/usr/bin/env python3
"""ADR-005 enforcement gate: published install commands must name `mneme-hq`.

`mneme` on PyPI is an unrelated, abandoned third-party package (a Flask/MongoDB
note-taking app, v0.201, last released 2014, Python 2.7 only) that this project
neither owns nor controls. Publishing `pip install mneme` does not merely give
readers a broken command -- it directs them to install from a namespace outside
our control. The correct distribution is `mneme-hq`; the import root and CLI
are both `mneme`.

ADR-005 lives in the core repository (MnemeHQ/mneme, docs/adr/) and has
forbidden this since 2026-05-04, but it went unenforced. On 2026-08-06 the
violation was found live on mnemehq.com across three pages -- and three of the
occurrences were inside JSON-LD, where the wrong command was syndicated to
search rich results and AI answer engines rather than merely displayed
(fixed in #7).

This repository is separate from core since the website extraction and does not
inherit the core repository's gate, so it needs its own. This is it.

Usage:
    python scripts/check_install_command.py             # scan tracked files
    python scripts/check_install_command.py --self-test # verify the matcher

Exit codes:
    0 = no violations
    1 = violations found (listed on stdout)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# Match an install command naming the bare `mneme` distribution, without
# matching `mneme-hq` or longer identifiers.
VIOLATION = re.compile(
    r"\b(?:pip|pipx|uv pip)\s+install\s+(?P<flags>(?:-[\w-]+\s+)*)mneme(?!-hq)(?![\w-])"
)

CORRECT = "mneme-hq"
CORE_VERSION = json.loads(
    (Path(__file__).with_name("core_version.json")).read_text(encoding="utf-8")
)["minimum_version"]

# `pip install -e mneme` / `--editable mneme` takes a *local directory path*,
# not a PyPI distribution name, so it never resolves to the wrong package.
EDITABLE_FLAGS = ("-e", "--editable")

SCANNED_SUFFIXES = {".html", ".htm", ".md", ".py", ".txt", ".yml", ".yaml", ".json"}

# Paths where the forbidden string is a deliberate artifact rather than an
# instruction to a reader. Each entry needs a reason.
ALLOWLIST: dict[str, str] = {
    # This gate must name the forbidden form to detect and explain it.
    # Without this entry the check fails on itself the moment it is committed.
    "scripts/check_install_command.py": "the gate's own pattern and messages",
}


def is_allowlisted(path: str) -> str | None:
    for prefix, reason in ALLOWLIST.items():
        if path.startswith(prefix):
            return reason
    return None


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, check=True
    ).stdout
    return [p for p in out.splitlines() if Path(p).suffix.lower() in SCANNED_SUFFIXES]


def is_violation(line: str) -> bool:
    match = VIOLATION.search(line)
    if not match:
        return False
    if any(f in EDITABLE_FLAGS for f in match.group("flags").split()):
        return False
    # A line naming both the correct and the forbidden form is a
    # correct-vs-wrong comparison, not an instruction.
    return CORRECT not in line


def scan(paths: list[str]) -> list[tuple[str, int, str]]:
    findings: list[tuple[str, int, str]] = []
    for path in paths:
        if is_allowlisted(path):
            continue
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if is_violation(line):
                findings.append((path, lineno, line.strip()))
    return findings


SELF_TEST_CASES: list[tuple[str, bool]] = [
    ("pip install mneme", True),
    ("<pre><code>pip install mneme", True),
    ("pipx install mneme", True),
    ("uv pip install mneme", True),
    ("      - run: pip install mneme", True),
    ("    - pip install mneme", True),
    ("pip install --upgrade mneme", True),
    ("pip install mneme-hq", False),
    (f'pipx install "mneme-hq&gt;={CORE_VERSION}"', False),
    ("pip install -e mneme", False),
    ("pip install --editable mneme", False),
    ("pipx install ./mneme", False),
    ("| pip install command | `pip install mneme-hq` | `pip install mneme` |", False),
    ("mneme check --mode warn", False),
    ("python -m mneme check", False),
    ("pip install mneme_hq", False),
    ("pip install mnemex", False),
]


def self_test() -> int:
    failures = 0
    for line, expected in SELF_TEST_CASES:
        got = is_violation(line)
        if got != expected:
            failures += 1
            print(f"FAIL  got={got} want={expected}  {line}")
    if failures:
        print(f"\nself-test: {failures} failure(s)")
        return 1
    print(f"self-test: OK ({len(SELF_TEST_CASES)} cases)")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()

    findings = scan(tracked_files())
    if not findings:
        print("ADR-005 install-command gate: OK (no `pip install mneme` found)")
        return 0

    print("ADR-005 VIOLATION: the PyPI distribution is `mneme-hq`, not `mneme`.")
    print()
    print("The bare name installs an unrelated, abandoned third-party package")
    print("this project does not own. Publish this instead:")
    print()
    print(f'    pipx install "mneme-hq>={CORE_VERSION}"')
    print()
    print(f"{len(findings)} occurrence(s):")
    for path, lineno, line in findings:
        print(f"  {path}:{lineno}: {line}")
    print()
    print("If a line legitimately contrasts the correct and forbidden forms,")
    print("name `mneme-hq` on the same line.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
