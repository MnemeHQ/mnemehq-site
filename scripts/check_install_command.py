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

The gate also rejects an unquoted version range such as
`pip install mneme-hq>=0.9.2`. The shell reads `>` as a redirect, so that
command installs an unpinned `mneme-hq` and writes a file named `=0.9.2`.
Found live on 2026-10-04 across the homepage, integration pages and JSON-LD.

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

# Match an install command whose `mneme-hq` requirement carries a range operator
# with no quote before it. Quoted forms put `"`, `'`, `\"` or `&quot;` between
# `install` and `mneme-hq`, so they never match. Exact `==` pins are shell-safe.
UNQUOTED_RANGE = re.compile(
    r"\b(?:pip|pipx|uv pip)\s+install\s+(?:-[\w-]+\s+)*"
    # A `<` that opens an HTML tag (`mneme-hq</code>`) is not a range.
    r"mneme-hq(?:\[[^\]\s]*\])?(?:>|<(?=[=\d\s])|&gt;|&lt;)"
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

UNQUOTED_ALLOWLIST: dict[str, str] = {
    "scripts/check_install_command.py": "the gate's own pattern and messages",
    # The synchronizer's self-test pins how it rewrites an unpinned command;
    # it is a test fixture, not published copy.
    "scripts/sync_core_version.py": "synchronizer self-test fixture",
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


def is_unquoted_range(line: str) -> bool:
    return UNQUOTED_RANGE.search(line) is not None


Finding = tuple[str, int, str]


def scan(paths: list[str]) -> tuple[list[Finding], list[Finding]]:
    findings: list[Finding] = []
    unquoted: list[Finding] = []
    for path in paths:
        check_name = not is_allowlisted(path)
        check_quotes = not any(path.startswith(p) for p in UNQUOTED_ALLOWLIST)
        if not (check_name or check_quotes):
            continue
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if check_name and is_violation(line):
                findings.append((path, lineno, line.strip()))
            if check_quotes and is_unquoted_range(line):
                unquoted.append((path, lineno, line.strip()))
    return findings, unquoted


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


UNQUOTED_TEST_CASES: list[tuple[str, bool]] = [
    ("pip install mneme-hq>=0.9.2", True),
    ("      - run: pip install mneme-hq>=0.9.2", True),
    ("    - pip install mneme-hq>=0.9.2", True),
    ("<code>pip install mneme-hq&gt;=0.9.2</code>", True),
    ("pipx install mneme-hq[mcp]>=0.9.2", True),
    ("pip install --upgrade mneme-hq<1.0", True),
    ('pip install "mneme-hq>=0.9.2"', False),
    ("pip install 'mneme-hq>=0.9.2'", False),
    ('"text": "pip install \\"mneme-hq>=0.9.2\\" && mneme init"', False),
    ("writeText('pip install &quot;mneme-hq>=0.9.2&quot;')", False),
    (f'pipx install "mneme-hq&gt;={CORE_VERSION}"', False),
    ("pipx install mneme-hq==0.9.2", False),
    ("pip install mneme-hq", False),
    ("<code>pip install mneme-hq</code>", False),
    ("Released as mneme-hq>=0.9.2", False),
]


def self_test() -> int:
    failures = 0
    suites = ((is_violation, SELF_TEST_CASES), (is_unquoted_range, UNQUOTED_TEST_CASES))
    for check, cases in suites:
        for line, expected in cases:
            got = check(line)
            if got != expected:
                failures += 1
                print(f"FAIL  {check.__name__} got={got} want={expected}  {line}")
    if failures:
        print(f"\nself-test: {failures} failure(s)")
        return 1
    print(f"self-test: OK ({len(SELF_TEST_CASES) + len(UNQUOTED_TEST_CASES)} cases)")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()

    findings, unquoted = scan(tracked_files())
    if not findings and not unquoted:
        print("ADR-005 install-command gate: OK (no `pip install mneme` or unquoted range found)")
        return 0

    if unquoted:
        print("UNQUOTED VERSION RANGE: the shell reads `>` and `<` as redirects.")
        print()
        print(f'    pip install "mneme-hq>={CORE_VERSION}"')
        print()
        print('Quote for the context: \\" inside a JSON string, &quot; inside an HTML attribute.')
        print()
        print(f"{len(unquoted)} occurrence(s):")
        for path, lineno, line in unquoted:
            print(f"  {path}:{lineno}: {line}")
        print()
        if not findings:
            return 1

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
