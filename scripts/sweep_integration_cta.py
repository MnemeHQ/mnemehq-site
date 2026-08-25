"""PR2 sweep: integration detail pages.
- Article-style pages: insert per-tool setup cluster before </header>;
  replace lime 'View on GitHub' end-block primary with coral Install + text link.
- Hero-style pages (hero-ctas): replace contents with setup primary +
  evidence outline (keeps existing evidence URL) + pilot text link.
Idempotent via 'Set up Mneme with' marker.
"""
import re
from pathlib import Path

SITE = Path(__file__).parent.parent / "site" / "integrations"

TOOLS = {
    "adr-import": "ADR import",
    "agent-sdk": None,  # not a dir; safe
    "antigravity": "Antigravity",
    "claude-agent-sdk": "the Claude Agent SDK",
    "claude-code": "Claude Code",
    "codex-cli": "Codex CLI",
    "copilot": "GitHub Copilot",
    "cursor": "Cursor",
    "github-actions": "GitHub Actions",
    "gitlab": "GitLab CI",
    "jetbrains": "JetBrains IDEs",
    "microsoft-agent-forge": "Microsoft Agent Forge",
    "opencode": "OpenCode",
    "paperclip": "Paperclip",
    "perplexity": "Perplexity",
    "vscode": "VS Code",
    "warp": "Warp",
}

HERO_CLUSTER = (
    '<div class="cta-row" style="margin-top:1.5rem;">\n'
    '    <a href="/docs/#quickstart" class="cta-btn-primary" data-cta-intent="setup" '
    'data-cta-position="hero" data-cta-component="hero_cluster">Set up Mneme with {tool}</a>\n'
    '    <a href="https://github.com/MnemeHQ/mneme" class="cta-btn-outline" data-cta-intent="github" '
    'data-cta-position="hero" data-cta-component="hero_cluster">View source on GitHub</a>\n'
    '    <a href="/pilot/" class="cta-link" data-cta-intent="pilot" data-cta-position="hero" '
    'data-cta-component="hero_cluster">Running it across a team? Request a pilot &rarr;</a>\n'
    '  </div>'
)

END_INSTALL = (
    '<a href="/docs/#quickstart" class="cta-btn-primary" data-cta-intent="install" '
    'data-cta-position="end" data-cta-component="end_block">Install Mneme</a>\n'
    '      <a href="https://github.com/MnemeHQ/mneme" class="cta-link" data-cta-intent="github" '
    'data-cta-position="end" data-cta-component="end_block">View source on GitHub &rarr;</a>'
)

END_PATTERNS = [
    re.compile(r'<a href="https://github\.com/MnemeHQ/mneme" class="btn-primary">View on GitHub &rarr;</a>'),
    re.compile(r'<a href="https://github\.com/MnemeHQ/mneme" class="btn-primary">View on GitHub &rarr;</a>'),
    re.compile(r'<a href="https://github\.com/MnemeHQ/mneme" class="btn-primary">Get started on GitHub</a>'),
]

changed = []
for d in sorted(SITE.iterdir()):
    f = d / "index.html"
    if not f.exists() or d.name == "index.html":
        continue
    slug = d.name
    tool = TOOLS.get(slug)
    if not tool:
        continue
    text = f.read_text(encoding="utf-8")
    orig = text
    notes = []

    if "Set up Mneme with" not in text:
        if "</header>" in text and 'class="hero"' not in text:
            text = text.replace("</header>", HERO_CLUSTER.format(tool=tool) + "\n  </header>", 1)
            notes.append("hero-cluster")
        elif "hero-ctas" in text:
            m = re.search(r'<div class="hero-ctas">\s*(.*?)\s*</div>', text, re.DOTALL)
            if m:
                inner = m.group(1)
                ev = re.search(r'href="(https://github\.com/MnemeHQ/mneme/pull/\d+)"', inner)
                evidence = ev.group(1) if ev else None
                cluster = (
                    '<div class="hero-ctas">\n'
                    f'            <a href="/docs/#quickstart" class="cta-btn-primary" data-cta-intent="setup" '
                    f'data-cta-position="hero" data-cta-component="hero_cluster">Set up Mneme with {tool}</a>\n'
                )
                if evidence:
                    cluster += (
                        f'            <a href="{evidence}" class="cta-btn-outline" target="_blank" rel="noopener" '
                        f'data-cta-intent="evidence" data-cta-position="hero" data-cta-component="hero_cluster">Evidence</a>\n'
                    )
                else:
                    cluster += (
                        '            <a href="https://github.com/MnemeHQ/mneme" class="cta-btn-outline" '
                        'data-cta-intent="github" data-cta-position="hero" data-cta-component="hero_cluster">View source on GitHub</a>\n'
                    )
                cluster += (
                    '            <a href="/pilot/" class="cta-link" data-cta-intent="pilot" data-cta-position="hero" '
                    'data-cta-component="hero_cluster">Running it across a team? Request a pilot &rarr;</a>\n'
                    '          </div>'
                )
                text = text[:m.start()] + cluster + text[m.end():]
                notes.append("hero-ctas-replaced")

    # End-block lime GitHub primary -> coral install + text link
    for pat in END_PATTERNS:
        if pat.search(text):
            text = pat.sub(END_INSTALL, text, count=1)
            notes.append("end-block")
            break

    if text != orig:
        f.write_bytes(text.encode("utf-8"))
        changed.append(f"{slug}: {', '.join(notes)}")

for c in changed:
    print(c)
print(f"{len(changed)} integration pages updated")
