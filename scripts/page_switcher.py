"""Shared renderer for the breadcrumb dropdown used by scripts/sync_docs_nav.py
and scripts/sync_integrations_nav.py: a <details> listing every sibling page,
grouped, with the current page marked. Styles live in
site/assets/css/base.css under "Page switcher (docs / integrations)".

Not a CLI on its own -- import render_block() from the two sync scripts.
"""
from __future__ import annotations

import re

START = "<!-- mneme:page-switcher:start -->"
END = "<!-- mneme:page-switcher:end -->"
BLOCK_PAT = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)

# Matches either breadcrumb style in use: `<li aria-current="page">Text</li>`
# (docs pages) and `<li><span aria-current="page">Text</span></li>` (a few
# integration pages).
CURRENT_CRUMB_PAT = re.compile(
    r'<li aria-current="page">[^<]*</li>'
    r'|<li><span aria-current="page">[^<]*</span></li>'
)

CHEVRON = (
    '<svg class="page-switcher-chevron" width="10" height="10" viewBox="0 0 10 10" '
    'aria-hidden="true"><path d="M2 3.5 5 6.5 8 3.5" fill="none" stroke="currentColor" '
    'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

# Close on Escape (returning focus to the toggle) and on outside click.
SCRIPT = """<script>
(function(){
  var d = document.currentScript.parentNode.querySelector('.page-switcher');
  if (!d) return;
  document.addEventListener('click', function(e){ if (d.open && !d.contains(e.target)) d.open = false; });
  d.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && d.open) { d.open = false; d.querySelector('summary').focus(); }
  });
})();
</script>"""


def render_block(
    *,
    current_label: str,
    groups: list[tuple[str, list[tuple[str, str, bool]]]],
    more_href: str,
    more_label: str,
    aria_label: str,
    sr_noun: str,
) -> str:
    """groups: [(group_title, [(href, label, is_current), ...]), ...]"""
    group_html = []
    for title, items in groups:
        links = "\n".join(
            f'          <li><a href="{href}"'
            + (' aria-current="page"' if is_current else "")
            + f">{label}</a></li>"
            for href, label, is_current in items
        )
        group_html.append(
            '      <div class="page-switcher-group">\n'
            f'        <div class="page-switcher-label">{title}</div>\n'
            f"        <ul>\n{links}\n        </ul>\n"
            "      </div>"
        )
    return (
        f'{START}<li class="page-switcher-item">\n'
        '    <details class="page-switcher">\n'
        f'      <summary><span class="page-switcher-sr">Current {sr_noun}: </span>{current_label} {CHEVRON}'
        f'<span class="page-switcher-sr"> (show all {sr_noun}s)</span></summary>\n'
        # A div, not <nav>: several pages carry bare `nav { position: sticky }`
        # rules that would otherwise restyle the panel.
        f'      <div class="page-switcher-panel" role="navigation" aria-label="{aria_label}">\n'
        + "\n".join(group_html)
        + f'\n      <a class="page-switcher-more" href="{more_href}">{more_label} &rarr;</a>\n'
        "      </div>\n"
        "    </details>\n"
        f"{SCRIPT}\n"
        f"    </li>{END}"
    )


def splice(text: str, block: str) -> tuple[str, bool]:
    """Insert/replace the switcher block in a page's HTML. Returns (new_text, ok)."""
    if START in text:
        return BLOCK_PAT.sub(lambda _: block, text, count=1), True
    matches = CURRENT_CRUMB_PAT.findall(text)
    if len(matches) == 1:
        return CURRENT_CRUMB_PAT.sub(lambda _: block, text, count=1), True
    return text, False
