#!/usr/bin/env python3
"""Fail if site copy still describes pre-0.10.0 Decision MCP storage behaviour.

mneme-hq 0.10.0 made the persisted Decision Index authoritative: the MCP
server reads it from project memory, refuses to start without it, and sees
accepted decisions without a restart. These phrases described 0.9.x and
would now send a reader into an exit-2 startup error or a false limitation.

Usage: python scripts/check_stale_mcp_claims.py [--root PATH]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = ("site", "templates")
SUFFIXES = {".html", ".txt", ".md", ".yaml", ".yml", ".json"}
FORBIDDEN = (
    "Canonical reads are optional",
    "proposal-store-only server",
    "run with proposals only",
    "Known limitations in 0.9.0",
    "Known 0.9.0 boundaries",
    "not automatically loaded into the MCP server",
    "not yet automatically unified with the MCP server",
    "not automatically composed into MCP",
    "restart the MCP process before expecting",
    "add a hidden project-memory canonical input",
    # version_id also hashes the source occurrence and predecessor version;
    # only content_digest is derived from content alone.
    "content-derived version",
)


def find_hits(root: Path) -> list[str]:
    hits = []
    for name in SCAN_DIRS:
        base = root / name
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.suffix not in SUFFIXES or not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for n, line in enumerate(text.splitlines(), 1):
                lowered = line.lower()
                for phrase in FORBIDDEN:
                    if phrase.lower() in lowered:
                        hits.append(f"{path.relative_to(root).as_posix()}:{n}: {phrase}")
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    hits = find_hits(args.root)
    for hit in hits:
        print(hit)
    print(f"stale-mcp-claims: {'FAIL' if hits else 'OK'} ({len(hits)} hit(s))")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
