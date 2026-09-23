#!/usr/bin/env python3
"""Regression check for the Gate B renderer defect: two different records
rendered back-to-back in the same process must never produce byte-identical
PNGs.

Background: `render_og._render` used to write every card's HTML to one
fixed temp file and load it from one fixed URL.
`http.server.SimpleHTTPRequestHandler` sends `Last-Modified` and honours
`If-Modified-Since`, so when two consecutive writes landed inside the same
filesystem-timestamp tick the server answered 304 Not Modified and
Chromium re-screenshotted the PREVIOUS card's page. On a full 322-card run
this produced 126 duplicate-hash groups covering 252 of 322 files (78%
corrupted), and it was non-deterministic between runs. It never showed up
in per-card `--only` renders, which is all the existing test suite and
manual QA had exercised -- there was never a second write in the same
process to collide with.

This script is the "actually render more than one card in a single
process and assert their bytes differ" proof `render_og.py`'s own
docstring points to. It is NOT part of `test_render_og.py` because it
needs Playwright + a pinned Chromium + Pillow, none of which the
`og-cards-check.yml` CI job installs (that job runs `pip install
pyyaml==6.0.1` only, deliberately, so `render_og.py` stays importable
without a browser). A human (or a separate CI job with Chromium available)
runs this explicitly:

  python scripts/check_og_render_unique.py

Exit 0 and "OK" on success; exit 1 with the duplicate-hash groups listed
on failure.
"""
from __future__ import annotations

import asyncio
import hashlib
import sys
import tempfile
from pathlib import Path

import og_manifest
import render_og

# A deliberately small, deliberately varied sample: different families,
# different templates, headlines of different lengths -- anything that
# renders as visibly different HTML. The defect doesn't care what the
# content is, only that two DIFFERENT records are written back-to-back in
# one browser process; any handful of distinct paths reproduces it.
SAMPLE_PATHS = [
    "compare/aider/",
    "compare/rag-vs-governance/",
    "use-cases/adr-enforcement/",
    "insights/rag-is-not-memory/",
    "demo/storage-decision/",
    "integrations/claude-code/",
    "benchmark/",
    "compare/",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def _render_sample(records: list[dict], out_dir: Path) -> None:
    await render_og._render(records, out_dir)


def check(paths: list[str] = SAMPLE_PATHS) -> list[list[str]]:
    """Render every path in `paths` in ONE process/browser and return the
    list of duplicate-hash groups (each a list of output-relative paths
    that came out byte-identical). Empty list means no duplicates.
    """
    raw = og_manifest.load(render_og.MANIFEST)
    records = [og_manifest.resolve(p, raw.get(p), strict=True) for p in paths]

    with tempfile.TemporaryDirectory(prefix="og_render_unique_") as tmp:
        out_dir = Path(tmp)
        asyncio.run(_render_sample(records, out_dir))

        by_hash: dict[str, list[str]] = {}
        for record in records:
            out_path = render_og._out_path(out_dir, record)
            digest = _sha256(out_path)
            by_hash.setdefault(digest, []).append(str(out_path.relative_to(out_dir)))

        return [group for group in by_hash.values() if len(group) > 1]


def main() -> int:
    render_og.assert_versions()
    dupes = check()
    if dupes:
        print("FAIL -- duplicate renders detected in a single process:")
        for group in dupes:
            print(f"  identical: {', '.join(group)}")
        print(
            "\nThis is the Gate B defect signature: two different records "
            "produced byte-identical output. Check render_og.py's temp-file "
            "naming, cache-busting query, and HTTP handler caching headers."
        )
        return 1
    print(f"OK -- {len(SAMPLE_PATHS)} distinct record(s) rendered in one "
          f"process, zero duplicate hashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
