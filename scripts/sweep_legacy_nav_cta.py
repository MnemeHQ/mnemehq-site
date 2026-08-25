"""One-off sweep: remove legacy page-local lime .btn-nav-cta rules so the
outline treatment in base.css applies. Run from repo root: python scripts/sweep_legacy_nav_cta.py
"""
import re
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"

# Matches the duplicated old base.css / template inline rules, with or without
# the trailing transition declaration, and the hover variant.
PATTERNS = [
    re.compile(r"\n\s*\.nav-links a\.btn-nav-cta \{ background: var\(--accent\);[^}]*\}"),
    re.compile(r"\n\s*\.nav-links a\.btn-nav-cta:hover \{ background: var\(--accent-dim\);[^}]*\}"),
]

changed = 0
for html in sorted(SITE.rglob("*.html")):
    if html.name.startswith("og-"):
        continue
    text = html.read_text(encoding="utf-8")
    original = text
    for pat in PATTERNS:
        text = pat.sub("", text)
    if text != original:
        html.write_bytes(text.encode("utf-8"))
        changed += 1

print(f"cleaned {changed} pages")
