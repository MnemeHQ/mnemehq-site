#!/usr/bin/env python3
"""Fail when the /setup/ chooser drifts from the integration catalogue.

The catalogue, site/integrations/index.html, is the source of truth for which
integrations exist, how they are grouped and what status each has. The chooser
data, site/assets/js/setup-chooser-data-v1.js, copies that. This check makes
sure the copy stays exact:

1. Every integration card in the catalogue's coding-agent, editor, orchestrator,
   software-factory, CI and runtime sections has exactly one chooser option in
   the matching group, with the same name and the same status line.
2. Every chooser option (except "Other / not listed") is a card in the catalogue.
3. Where a catalogue card links somewhere, the option's "page" is that link.
4. Every setup guide an option points to exists under site/setup/.
5. The built /setup/ page's no-JavaScript fallback lists every option.

Usage:
    python scripts/check_setup_chooser.py   # exit 0 when in sync, 1 otherwise
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "site" / "integrations" / "index.html"
DATA_JS = ROOT / "site" / "assets" / "js" / "setup-chooser-data-v1.js"
HUB = ROOT / "site" / "setup" / "index.html"

# catalogue section id -> chooser group id. The coding-agents section holds two
# groups: cards after its "Editors and hosts without a Mneme hook" sub-heading
# belong to "editors".
SECTION_GROUP = {
    "coding-agents": "agents",
    "agent-orchestrators": "orchestrators",
    "software-factories": "factories",
    "ci-and-enforcement": "ci",
    "runtime-and-policy": "runtime",
}
EDITORS_HEADING = "Editors and hosts without a Mneme hook"

CARD_RE = re.compile(
    r'<(a|div) class="int-card[^"]*"(?: href="([^"]*)")?>\s*'
    r'<div class="int-status">(.*?)</div>\s*<h3>(.*?)</h3>',
    re.S,
)


def text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def catalogue_cards() -> list[dict]:
    page = CATALOGUE.read_text(encoding="utf-8")
    cards = []
    for section_id, group in SECTION_GROUP.items():
        m = re.search(rf'<section class="layer" id="{section_id}">(.*?)</section>', page, re.S)
        if not m:
            raise SystemExit(f"catalogue section #{section_id} not found")
        body = m.group(1)
        split = body.find(EDITORS_HEADING) if section_id == "coding-agents" else -1
        for c in CARD_RE.finditer(body):
            g = "editors" if split != -1 and c.start() > split else group
            cards.append({"group": g, "href": c.group(2) or "", "status": text(c.group(3)), "name": text(c.group(4))})
    return cards


def chooser_data() -> dict:
    src = DATA_JS.read_text(encoding="utf-8")
    marker = "window.MNEME_SETUP_CHOOSER = "
    return json.loads(src[src.index(marker) + len(marker) : src.rindex(";")])


def main() -> int:
    errors: list[str] = []
    cards = catalogue_cards()
    data = chooser_data()
    options = [o for o in data["options"] if o["group"] != "other"]

    def key(group: str, name: str) -> tuple[str, str]:
        return group, name

    by_key: dict[tuple[str, str], list[dict]] = {}
    for o in options:
        by_key.setdefault(key(o["group"], o.get("catalogue_name", o["name"])), []).append(o)

    seen = set()
    for c in cards:
        k = key(c["group"], c["name"])
        found = by_key.get(k, [])
        if len(found) != 1:
            errors.append(f"catalogue card {c['name']!r} ({c['group']}) has {len(found)} chooser options, expected 1")
            continue
        o = found[0]
        seen.add(o["id"])
        if o["status"] != c["status"]:
            errors.append(f"{o['id']}: status {o['status']!r} != catalogue {c['status']!r}")
        if c["href"] and o["page"] != c["href"]:
            errors.append(f"{o['id']}: page {o['page']!r} != catalogue link {c['href']!r}")

    for o in options:
        if o["id"] not in seen:
            errors.append(f"chooser option {o['id']!r} is not a card in the catalogue")

    for o in data["options"]:
        for href in (o.get("guide"), o.get("page")):
            if href and href.startswith("/") and not (ROOT / "site" / href.strip("/") / "index.html").exists():
                errors.append(f"{o['id']}: {href} has no index.html under site/")

    if HUB.exists():
        hub = HUB.read_text(encoding="utf-8")
        m = re.search(r'<div class="chooser-fallback" data-chooser-fallback>(.*?)\n</div>', hub, re.S)
        fallback = text(m.group(1)) if m else ""
        for o in data["options"]:
            if o["name"] not in fallback:
                errors.append(f"/setup/ fallback list is missing {o['name']!r}; rebuild with scripts/build_setup_page.py")
    else:
        errors.append("site/setup/index.html is missing; run scripts/build_setup_page.py")

    if errors:
        print("check_setup_chooser: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"check_setup_chooser: OK ({len(cards)} catalogue cards, {len(data['options'])} chooser options)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
