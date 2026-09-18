#!/usr/bin/env python3
"""Sync the integrations switcher (breadcrumb dropdown) across every
/integrations/<slug>/ page. Mirrors scripts/sync_docs_nav.py; rendering is
shared via scripts/page_switcher.py.

INTEGRATIONS below mirrors the grouping already used on /integrations/
(see the numbered "layer" sections there): add a page to both places.
The /integrations/ index page itself has no breadcrumb and is left alone --
it already lists every integration as its main content.

Usage:
    python scripts/sync_integrations_nav.py          # rewrite pages in place
    python scripts/sync_integrations_nav.py --check  # CI: fail if stale
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from page_switcher import render_block, splice  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INTEGRATIONS_DIR = ROOT / "site" / "integrations"

# (group label, [(slug, label)]) -- labels match each page's own breadcrumb text.
INTEGRATIONS: list[tuple[str, list[tuple[str, str]]]] = [
    ("Interoperability", [
        ("mcp", "MCP"),
    ]),
    ("Enforcement", [
        ("claude-code", "Claude Code"),
        ("claude-agent-sdk", "Claude Agent SDK"),
        ("antigravity", "Google Antigravity"),
        ("paperclip", "Paperclip"),
        ("codex-cli", "Codex CLI"),
        ("langchain-langgraph", "LangChain / LangGraph"),
        ("kiro", "Kiro"),
    ]),
    ("Propagation", [
        ("cursor", "Cursor"),
        ("github-actions", "GitHub Actions"),
        ("gitlab", "GitLab CI"),
        ("adr-import", "Import Existing ADRs"),
    ]),
    ("Host environments", [
        ("vscode", "VS Code"),
        ("copilot", "GitHub Copilot"),
        ("jetbrains", "JetBrains"),
        ("warp", "Warp"),
    ]),
    ("Experimental & planned", [
        ("opencode", "OpenCode"),
        ("hermes", "Hermes Agent"),
    ]),
    ("Works alongside", [
        ("perplexity", "Perplexity"),
        ("microsoft-agent-forge", "Microsoft Agent Forge"),
    ]),
]


def href(slug: str) -> str:
    return f"/integrations/{slug}/"


def render(current: str) -> str:
    current_label = next(l for _, items in INTEGRATIONS for s, l in items if s == current)
    groups = [
        (group, [(href(s), l, s == current) for s, l in items])
        for group, items in INTEGRATIONS
    ]
    return render_block(
        current_label=current_label,
        groups=groups,
        more_href="/docs/",
        more_label="Docs",
        aria_label="All integrations",
        sr_noun="integration",
    )


def pages() -> list[tuple[str, Path]]:
    return [
        (s, INTEGRATIONS_DIR / s / "index.html")
        for _, items in INTEGRATIONS
        for s, _ in items
    ]


def sync(check: bool) -> int:
    stale = []
    for slug, path in pages():
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        eol = "\r\n" if "\r\n" in text else "\n"
        block = render(slug).replace("\n", eol)
        new, ok = splice(text, block)
        if not ok:
            print(f"sync_integrations_nav: no breadcrumb anchor in {path.relative_to(ROOT)}")
            return 1
        if new != text:
            stale.append(path)
            if not check:
                path.write_bytes(new.encode("utf-8"))
    if check and stale:
        print("sync_integrations_nav: FAIL, stale integrations switcher in:")
        for p in stale:
            print(f"  {p.relative_to(ROOT)}")
        print("Run: python scripts/sync_integrations_nav.py")
        return 1
    verb = "OK" if check else f"updated {len(stale)} page(s)"
    print(f"sync_integrations_nav: {verb} ({len(pages())} integration pages)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    return sync(ap.parse_args().check)


if __name__ == "__main__":
    sys.exit(main())
