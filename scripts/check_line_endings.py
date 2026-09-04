#!/usr/bin/env python3
"""Fail CI when a change rewrites a file's newline convention.

Line endings are a byte-level property, so no Mneme constraint expresses
them at any version. `mneme check` matches text tokens in the file contents
it is handed -- the governance workflow now feeds those contents as well as
the changed-path list -- but a newline convention is not a token in the text.
This is the byte-level counterpart to check_encoding.py.

The failure mode this catches is silent and expensive. A Python helper that
does:

    text = path.read_text(encoding="utf-8")   # universal newlines: CRLF -> LF
    ...
    path.write_bytes(text.encode("utf-8"))    # writes LF

rewrites every line of a CRLF file while changing only a handful of
characters. The content edit is correct, the diff is unreviewable, and
nothing in the existing checks notices. It happened twice in the demo-page
work: once to 29 files, and once to site/index.html, which showed 411
insertions and 411 deletions with zero content changes.

The rule is deliberately narrow. It does not impose a convention on the
repository -- site/index.html is legitimately mixed (1097 CRLF + 409 LF) --
it only asserts that a file's existing convention is preserved. New files
are exempt.

Usage:
  python scripts/check_line_endings.py              # diff against origin/main
  python scripts/check_line_endings.py <base-ref>   # diff against a ref
  python scripts/check_line_endings.py --cached <base-ref>  # staged Git bytes
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {".html", ".css", ".js", ".xml", ".txt", ".md", ".json", ".svg", ".py"}

# Below this many lines a ratio comparison is noise rather than signal.
MIN_LINES = 10


def counts(blob: bytes) -> tuple[int, int]:
    crlf = blob.count(b"\r\n")
    return crlf, blob.count(b"\n") - crlf


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, cwd=REPO_ROOT
    ).stdout


def dominant(crlf: int, lf: int) -> str | None:
    total = crlf + lf
    if total < MIN_LINES:
        return None
    if crlf > lf * 4:
        return "CRLF"
    if lf > crlf * 4:
        return "LF"
    return "mixed"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("base", nargs="?", default="origin/main")
    parser.add_argument("--cached", action="store_true",
                        help="compare the staged candidate, excluding Git checkout EOL conversion")
    args = parser.parse_args(argv[1:])
    base = args.base
    if not git("cat-file", "-e", f"{base}^{{commit}}") and subprocess.run(
        ["git", "cat-file", "-e", f"{base}^{{commit}}"], cwd=REPO_ROOT
    ).returncode:
        print(f"[eol-check] SKIP (base ref {base!r} not available)")
        return 0

    diff_args = ["diff", "--name-only"]
    if args.cached:
        diff_args.append("--cached")
    changed = git(*diff_args, base).splitlines()
    findings: list[str] = []
    checked = 0

    for name in changed:
        if Path(name).suffix.lower() not in TEXT_SUFFIXES:
            continue
        path = REPO_ROOT / name
        if not args.cached and not path.exists():
            continue
        before = subprocess.run(
            ["git", "show", f"{base}:{name}"], capture_output=True, cwd=REPO_ROOT
        ).stdout
        if not before:
            continue  # new file: it defines its own convention
        if args.cached:
            candidate = subprocess.run(
                ["git", "show", f":{name}"], capture_output=True, cwd=REPO_ROOT
            )
            if candidate.returncode:
                continue  # deleted from the candidate
            after = candidate.stdout
        else:
            after = path.read_bytes()
        checked += 1
        b_crlf, b_lf = counts(before)
        a_crlf, a_lf = counts(after)
        was, now = dominant(b_crlf, b_lf), dominant(a_crlf, a_lf)
        if was and now and was != now:
            findings.append(
                f"    {name}\n"
                f"        was {was:5} ({b_crlf} CRLF / {b_lf} LF)"
                f"  ->  now {now:5} ({a_crlf} CRLF / {a_lf} LF)"
            )

    if not findings:
        print(f"[eol-check] OK ({checked} changed text files compared against {base})")
        return 0

    print(f"[eol-check] FAIL ({len(findings)} file(s) changed newline convention)")
    print()
    print("\n".join(findings))
    print()
    print("A file's newline convention must survive an edit. The usual cause is")
    print("read_text() -- its universal-newline handling turns CRLF into LF, and")
    print("a later write_bytes() persists that. Read and write bytes, decode and")
    print("encode explicitly, and assert the CRLF count is unchanged:")
    print()
    print("    raw = path.read_bytes()")
    print("    text = raw.decode('utf-8')        # no newline translation")
    print("    out = text.replace(old, new).encode('utf-8')")
    print("    assert out.count(b'\\r\\n') == raw.count(b'\\r\\n')")
    print("    path.write_bytes(out)")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
