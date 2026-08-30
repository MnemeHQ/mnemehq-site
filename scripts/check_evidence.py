#!/usr/bin/env python3
"""
Validates first-party evidence blocks against docs/site/evidence-contract.json
(ADR-004: public empirical claims must resolve to a verified public artifact
and carry an explicit claim boundary).

Checks, per <div class="callout callout-evidence" data-evidence-id="..."> block
on a governed page:
  ERROR  -- evidence ID has no entry in the registry
  ERROR  -- registry status for this ID is not "verified"
  ERROR  -- evidence-source href does not match the registry's source_artifact_url
  ERROR  -- a required result token is missing from the block's text
  ERROR  -- evidence-limitation element is missing or empty
  ERROR  -- a forbidden-claim string appears in the block's text

Also checks, per governed page in GOVERNED_PAGES:
  ERROR  -- the page's required evidence ID is not present exactly once
            (catches a deleted block, a duplicated block, or a page that
            substitutes a different evidence ID for its required one --
            this check does not depend on any block being found, so it
            cannot pass by omission)

Exit codes:  0 = clean   1 = errors found   2 = warnings only
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "docs" / "site" / "evidence-contract.json"

# Each governed page maps to the evidence ID(s) it must carry exactly once.
# This is the source of truth for "this page must not lose its evidence" --
# a page with zero matching blocks fails here even though there is nothing
# for check_block() to inspect.
GOVERNED_PAGES = {
    REPO_ROOT / "site" / "insights" / "how-ai-coding-agents-use-adrs" / "index.html": ["E1"],
    REPO_ROOT / "site" / "insights" / "ai-native-sdlc-architecture-layer" / "index.html": ["E2"],
}

EVIDENCE_BLOCK_RE = re.compile(
    r'<div\s+class="callout callout-evidence"\s+data-evidence-id="([^"]+)">(.*?)</div>',
    re.DOTALL,
)
CLAIM_RE = re.compile(r'<p\s+class="evidence-claim">(.*?)</p>', re.DOTALL)
LIMITATION_RE = re.compile(r'<p\s+class="evidence-limitation">(.*?)</p>', re.DOTALL)
SOURCE_RE = re.compile(r'<a\s+class="evidence-source"\s+href="([^"]*)"', re.DOTALL)

TAG_RE = re.compile(r'<[^>]+>')


def strip_tags(html: str) -> str:
    return TAG_RE.sub('', html).strip()


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def load_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_evidence_blocks(html: str):
    """Yield (evidence_id, block_html) for every evidence block on the page."""
    for m in EVIDENCE_BLOCK_RE.finditer(html):
        yield m.group(1), m.group(2)


def page_label(page: Path) -> str:
    try:
        return str(page.relative_to(REPO_ROOT))
    except ValueError:
        return str(page)


def check_block(page: Path, evidence_id: str, block_html: str, registry: dict, errors: list) -> None:
    prefix = f"  {page_label(page)} [{evidence_id}]:"

    entry = registry.get(evidence_id)
    if entry is None:
        errors.append(f"{prefix} unknown evidence ID (no registry entry)")
        return

    if entry.get("status") != "verified":
        errors.append(
            f"{prefix} status is {entry.get('status')!r}, not 'verified' -- "
            f"not eligible to cite yet"
        )
        return

    source_m = SOURCE_RE.search(block_html)
    if not source_m or source_m.group(1) != entry["source_artifact_url"]:
        found = source_m.group(1) if source_m else "(missing evidence-source link)"
        errors.append(
            f"{prefix} source mismatch -- expected {entry['source_artifact_url']!r}, got {found!r}"
        )

    claim_m = CLAIM_RE.search(block_html)
    limitation_m = LIMITATION_RE.search(block_html)

    claim_text = strip_tags(claim_m.group(1)) if claim_m else ""
    limitation_text = strip_tags(limitation_m.group(1)) if limitation_m else ""
    combined_text = f"{claim_text} {limitation_text}"

    if not limitation_text:
        errors.append(f"{prefix} evidence-limitation is missing or empty")

    for token in entry.get("required_result_tokens", []):
        if token not in combined_text:
            errors.append(f"{prefix} missing required result token {token!r}")

    lowered = combined_text.lower()
    for phrase in entry.get("forbidden_claims", []):
        if phrase.lower() in lowered:
            errors.append(f"{prefix} forbidden claim language present: {phrase!r}")


def check_governed_page(page: Path, required_ids: list, html: str, registry: dict, errors: list) -> int:
    """Check every evidence block on one page, plus that each of the page's
    required evidence IDs appears exactly once. Returns the number of blocks
    checked. This is the function that makes the checker fail-closed: it
    asserts presence independently of whatever find_evidence_blocks() finds,
    so a deleted, duplicated, or substituted block is caught even though
    there is nothing (or the wrong thing) for check_block() to inspect.
    """
    found_ids = []
    blocks_checked = 0
    for evidence_id, block_html in find_evidence_blocks(html):
        found_ids.append(evidence_id)
        blocks_checked += 1
        check_block(page, evidence_id, block_html, registry, errors)

    for required_id in required_ids:
        count = found_ids.count(required_id)
        if count != 1:
            errors.append(
                f"  {page_label(page)}: requires exactly one evidence block "
                f"for {required_id!r}, found {count}"
            )

    return blocks_checked


def main() -> int:
    if not REGISTRY.exists():
        print(f"ERROR  Registry not found: {REGISTRY}", file=sys.stderr)
        return 1

    registry = load_registry()
    errors = []
    blocks_checked = 0

    for page, required_ids in GOVERNED_PAGES.items():
        if not page.exists():
            errors.append(f"  governed page not found: {page.relative_to(REPO_ROOT)}")
            continue
        html = load_html(page)
        blocks_checked += check_governed_page(page, required_ids, html, registry, errors)

    if errors:
        print("ERRORS -- fix before opening PR:")
        for msg in errors:
            print(msg)
        return 1

    print(f"OK  {blocks_checked} evidence block(s) across {len(GOVERNED_PAGES)} governed page(s) consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
