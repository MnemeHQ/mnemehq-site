#!/usr/bin/env python3
"""Link the AI agent governance pillar from every company-response article.

GSC (90 days to 2026-09-27) routes agent-governance queries to company-response
articles instead of the pillar. This inserts one canonical entry as the first
item of each article's "related essays" list, and replaces any stale entry for
the pillar so that anchor text stays consistent. Idempotent and LF-preserving.

Usage:
  python scripts/sweep_governance_pillar_link.py           # dry run
  python scripts/sweep_governance_pillar_link.py --write   # apply
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB_HREF = 'href="/insights/ai-agent-governance-two-markets/"'
CANONICAL_LI = (
    '      <li><a href="/insights/ai-agent-governance-two-markets/"><div class="rel-title">'
    'AI Agent Governance: Runtime vs. Architectural Control</div><p class="rel-desc">'
    'Runtime governance controls agent actions; architectural governance '
    'prevents drift.</p></a></li>\n'
)
TARGETS = [
    "palantir-agentic-governance-engineering-governance",
    "microsoft-agentic-transformation-playbook-ai-agent-governance",
    "microsoft-agent-platform-governance-layer",
    "microsoft-execution-containers-ai-agent-runtime-governance",
    "microsoft-project-solara-post-app-governance",
    "microsoft-agent-forge-enterprise-ai-infrastructure",
    "google-cloud-agent-registry-agent-fleet-governance",
    "google-gemini-deep-research-agent-governance",
    "gartner-ai-governance-engineering-governance",
    "ibm-2026-tech-leader-study-agent-governance",
    "snowflake-ai-data-engineering-governance-infrastructure",
    "cursor-developer-habits-report-governance-infrastructure",
    "devin-ai-software-engineer-governance",
    "bain-ai-development-lifecycle-governance",
    "bcg-ai-era-operating-models-governance",
    "stanford-ai-index-2026-engineering-governance",
    "anthropic-recursive-self-improvement-engineering-governance",
    "anthropic-claude-marketplace-ai-engineering-control-plane",
    "nvidia-nemo-agent-toolkit-engineering-governance",
    "morph-reflexes-agent-observability-engineering-governance",
    "block-builderbot-coordination-governance",
    "databricks-omnigent-agent-infrastructure-governance",
    "mckinsey-agentic-software-delivery-governance",
    "deepseek-agent-model-harness-architectural-governance",
    "antigravity-solves-coordination-not-governance",
    "claude-code-self-hosted-environments-architectural-governance",
]
LIST_RE = re.compile(
    r'(id="related-essays-label"[^>]*>.*?</div>\s*<ul class="related-list">\n)', re.S)
STALE_LI_RE = re.compile(
    r'[ \t]*<li><a href="/insights/ai-agent-governance-two-markets/">.*?</li>\n', re.S)


def insert_pillar_link(html: str) -> tuple[str, str]:
    if CANONICAL_LI in html:
        return html, "unchanged"
    m = LIST_RE.search(html)
    if not m:
        return html, "no-related-list"
    stripped, n = STALE_LI_RE.subn("", html)
    m = LIST_RE.search(stripped)
    out = stripped[: m.end()] + CANONICAL_LI + stripped[m.end():]
    return out, "replaced" if n else "inserted"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    problems = 0
    for slug in TARGETS:
        path = ROOT / "site" / "insights" / slug / "index.html"
        src = path.read_bytes().decode("utf-8")
        out, status = insert_pillar_link(src)
        print(f"{status:16} {slug}")
        if status == "no-related-list":
            problems += 1
        elif out != src and args.write:
            path.write_bytes(out.encode("utf-8"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
