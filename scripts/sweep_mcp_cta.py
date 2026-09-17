"""Insert the shared 'Use Mneme through MCP' cross-integration CTA into
every integration detail page except the MCP page itself.

Idempotent via the 'mcp-cross-cta' marker: re-running after a partial
apply only touches files that don't already have it. Mirrors the pattern
in scripts/sweep_integration_cta.py (regex-locate the existing
integration-end-cta block, insert immediately after it).
"""
import re
from pathlib import Path

SITE = Path(__file__).parent.parent / "site" / "integrations"

# Native integrations get "Prefer MCP?" wording; everyone else gets the
# generic "Use Mneme through MCP" wording.
NATIVE = {"claude-code", "codex-cli", "kiro", "hermes"}

GENERIC_CARD = (
    '\n<div class="mcp-cross-cta">\n'
    '  <div class="mcp-cross-cta__text">\n'
    '    <span class="mcp-cross-cta__eyebrow">Use Mneme through MCP</span>\n'
    "    <p>Connect Mneme's Decision Index to MCP-compatible agents and tools. "
    "Query applicable architectural decisions, retrieve provenance, and expose "
    "decision context without coupling the consumer to Mneme internals.</p>\n"
    "  </div>\n"
    '  <a href="/integrations/mcp/" class="mcp-cross-cta__link" data-cta-intent="mcp" '
    'data-cta-position="end" data-cta-component="mcp_cross_cta">Explore MCP &rarr;</a>\n'
    "</div>"
)

NATIVE_CARD = (
    '\n<div class="mcp-cross-cta">\n'
    '  <div class="mcp-cross-cta__text">\n'
    '    <span class="mcp-cross-cta__eyebrow">Prefer MCP?</span>\n'
    "    <p>Mneme also exposes its Decision Index through a standard MCP server "
    "for interoperable access from compatible tools.</p>\n"
    "  </div>\n"
    '  <a href="/integrations/mcp/" class="mcp-cross-cta__link" data-cta-intent="mcp" '
    'data-cta-position="end" data-cta-component="mcp_cross_cta">Explore MCP &rarr;</a>\n'
    "</div>"
)

# Matches either the "cta-block integration-end-cta" or "cta-band
# integration-end-cta" wrapper, capturing through its two closing </div>s.
END_CTA_BLOCK = re.compile(
    r'(<div class="(?:cta-block|cta-band) integration-end-cta">.*?</div>\s*</div>)',
    re.DOTALL,
)

changed = []
skipped = []
for d in sorted(SITE.iterdir()):
    if not d.is_dir() or d.name == "mcp":
        continue
    f = d / "index.html"
    if not f.exists():
        continue
    text = f.read_text(encoding="utf-8")
    if "mcp-cross-cta" in text:
        skipped.append(d.name)
        continue
    card = NATIVE_CARD if d.name in NATIVE else GENERIC_CARD
    new_text, n = END_CTA_BLOCK.subn(lambda m: m.group(1) + card, text, count=1)
    if n == 0:
        print(f"WARNING: no integration-end-cta block found in {d.name}, skipping")
        continue
    f.write_bytes(new_text.encode("utf-8"))
    changed.append(d.name)

for c in changed:
    print(f"updated: {c}")
for s in skipped:
    print(f"already present, skipped: {s}")
print(f"\n{len(changed)} pages updated, {len(skipped)} already had the card")
