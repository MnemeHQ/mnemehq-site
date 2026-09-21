#!/usr/bin/env python3
"""One-off sweep: retire the lime accent for sage and re-assert the CTA colour
contract (docs/site/cta-system.md).

Why this exists
---------------
A colour audit of every page found three problems the contract already
forbids, plus one the contract itself got wrong:

  1. Three colours were acting as "the primary button": coral (correct),
     mint (175 insight pages, beside the coral one) and lime (73 buttons on
     59 pages). One filled coral action per cluster is the rule.
  2. #55555f carried real text at 10-12px (2.65:1, below WCAG AA). The site
     already uses #88889a for that role on 145 pages.
  3. Eight reds and four ambers, with the error reds sitting 0-9 degrees from
     the coral action colour, so "deny" and "install" shared a hue family.
  4. Lime (#c8f060, 83% saturation) next to coral reads as signage rather
     than as a status colour, and it is the one accent that appears nowhere
     in the logo. Sage (#b5cc7a) keeps the hue and drops the chroma.

What it does
------------
  * swaps the palette hexes site-wide (lime -> sage, greys, one red, one amber)
  * rewrites .context-cta-primary as a neutral outline button
  * turns .btn-primary lime fills into the coral primary, and demotes the
    GitHub / artifact links wearing that class to .cta-btn-outline
  * moves .footer-pilot from lime to the coral outline used by the nav
  * moves eyebrow/kicker labels off the accent onto the quiet grey
  * adds --quiet and a link focus ring to base.css

Idempotent: running it twice is a no-op. Generators that emit the same CSS
(sync_shared.py, insert_contextual_ctas.py) are updated in the same commit, so
a later sync does not reintroduce the old palette.

Usage:
  python scripts/sweep_accent_sage.py [--check]

  --check  report what would change and exit 1 if anything would, without
           writing. Used to prove the sweep has fully landed.
"""
from __future__ import annotations

import argparse
import html as html_mod
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE = REPO_ROOT / "site"

# ── palette map ────────────────────────────────────────────────────────────
# Lime -> sage keeps hue 77 and drops saturation from 83% to 45%.
# Contrast on #0c0c0d: 11.06:1 (sage), 5.62:1 (quiet grey), 6.58:1 (error red),
# 11.14:1 (warn amber) -- all above the 4.5:1 AA floor.
HEX_MAP = {
    "#c8f060": "#b5cc7a",  # --accent            lime  -> sage
    "#a8d040": "#9ab35f",  # --accent-dim
    "#a9d342": "#9ab35f",  # --accent-dim (drifted duplicate)
    "#55555f": "#88889a",  # faint grey 2.65:1   -> quiet grey 5.62:1
    "#ff6b58": "#ff5c7a",  # --error       ┐
    "#ff6b6b": "#ff5c7a",  # --demo-deny   │ eight reds -> one, moved off
    "#ff7070": "#ff5c7a",  # inline red    │ the coral hue (9 deg -> 349 deg)
    "#ef4444": "#ff5c7a",  # --fail        │
    "#e05a5a": "#ff5c7a",  # inline red    ┘
    "#ff9d6e": "#f6b94b",  # --warn (orange) ┐ four ambers -> one, and out of
    "#f59e0b": "#f6b94b",  # --warn (amber)  ┘ coral's neighbourhood
}

# rgba() spellings of the lime, with any spacing and any alpha.
RGBA_LIME = re.compile(r"rgba\(\s*200\s*,\s*240\s*,\s*96\s*,")
RGBA_SAGE = "rgba(181, 204, 122,"

QUIET = "#88889a"
SAGE = "#b5cc7a"

# ── CTA rewrites ───────────────────────────────────────────────────────────
# The contextual CTA inside an article is an editorial hop, not the page's
# conversion action: neutral outline, mint on hover. One canonical rule
# replaces the two variants that had drifted apart.
CONTEXT_CTA_RULE = (
    ".context-cta-primary { display: inline-flex; align-items: center; "
    "background: transparent; color: var(--text, #e8e8ec); padding: 0.7rem 1.4rem; "
    "border: 1px solid var(--border2, #2e2e34); border-radius: 8px; "
    "font-family: 'Inter', sans-serif; font-size: 0.88rem; font-weight: 500; "
    "text-decoration: none; transition: border-color 0.15s, color 0.15s; }"
)
CONTEXT_CTA_HOVER = (
    ".context-cta-primary:hover { border-color: #8be0c8; color: #8be0c8; }"
)

FOOTER_PILOT_RULE = (
    ".footer-pilot { display:inline-flex;align-items:center;gap:0.4rem;"
    "padding:0.5rem 0.9rem;border:1px solid var(--action, #ea735e);border-radius:4px;"
    "color:var(--action-soft, #f2a08e);font-family:'DM Mono',monospace;font-size:0.72rem;"
    "letter-spacing:0.05em;text-transform:uppercase;text-decoration:none;"
    "transition:background 0.15s,color 0.15s; }"
)
FOOTER_PILOT_HOVER = (
    ".footer-pilot:hover, .footer-pilot:focus-visible "
    "{ background: var(--action, #ea735e); color:#0b0d0c; }"
)

# A .btn-primary anchor pointing at source code or a download is a secondary
# action wearing the primary's clothes. Everything else on these pages is the
# page's real conversion action and keeps the fill, now coral.
SECONDARY_LABEL = re.compile(r"github|freeze artifact", re.I)

BTN_OUTLINE_LOCAL = (
    ".btn-outline { display: inline-block; background: transparent; "
    "color: var(--text); padding: 0.65rem 1.5rem; border: 1px solid var(--border2); "
    "border-radius: 8px; font-size: 0.85rem; font-weight: 600; "
    "font-family: 'DM Mono', monospace; text-decoration: none; "
    "transition: border-color 0.15s, color 0.15s; }"
)


def site_files() -> list[Path]:
    """Every hand-maintained page and stylesheet.

    og-*.html are excluded: they are render sources for committed .jpg cards,
    so recolouring them without re-rendering would put the templates and the
    images they produce out of sync. Those get regenerated separately.
    site/audit/workspace/ is build output from audit/frontend/.
    """
    out: list[Path] = []
    for path in SITE.rglob("*"):
        if path.suffix not in {".html", ".css"} or not path.is_file():
            continue
        rel = path.relative_to(SITE).as_posix()
        if rel.startswith("audit/workspace/") or path.name.startswith("og-"):
            continue
        out.append(path)
    # Page templates ship the same CSS into every new article/page, so they
    # have to move with the site or the next `new_article.py` regresses.
    for tpl in (REPO_ROOT / "templates").glob("*"):
        if tpl.suffix in {".html", ".css"} and tpl.is_file():
            out.append(tpl)
    return [p for p in out if p.exists()]


def swap_palette(text: str) -> str:
    for old, new in HEX_MAP.items():
        text = text.replace(old, new)
    return RGBA_LIME.sub(RGBA_SAGE, text)


def rewrite_context_cta(text: str) -> str:
    text = re.sub(r"\.context-cta-primary\s*\{[^}]*\}", CONTEXT_CTA_RULE, text)
    return re.sub(r"\.context-cta-primary:hover\s*\{[^}]*\}", CONTEXT_CTA_HOVER, text)


def rewrite_footer_pilot(text: str) -> str:
    text = re.sub(r"\.footer-pilot\s*\{[^}]*\}", FOOTER_PILOT_RULE, text)
    return re.sub(
        r"\.footer-pilot:hover,\s*\.footer-pilot:focus-visible\s*\{[^}]*\}",
        FOOTER_PILOT_HOVER,
        text,
    )


def rewrite_btn_primary(text: str, has_base_css: bool) -> str:
    """Coral fill for the real action; outline for the GitHub/download links."""
    rule = re.search(r"\.btn-primary\s*\{[^}]*\}", text)
    if not rule or "var(--accent)" not in rule.group(0):
        return text

    fixed = rule.group(0).replace("background: var(--accent)", "background: var(--action, #ea735e)")
    text = text[: rule.start()] + fixed + text[rule.end():]
    text = re.sub(
        r"(\.btn-primary:hover\s*\{[^}]*?background:\s*)var\(--accent-dim\)",
        r"\1var(--action-dim, #c95a46)",
        text,
    )
    text = re.sub(
        r"(\.btn-primary:hover\s*\{[^}]*?background:\s*)#9ab35f",
        r"\1var(--action-dim, #c95a46)",
        text,
    )

    outline_class = "cta-btn-outline" if has_base_css else "btn-outline"
    needs_local_rule = False

    def demote(match: re.Match[str]) -> str:
        nonlocal needs_local_rule
        anchor, label = match.group(0), match.group("label")
        plain = html_mod.unescape(label).replace("→", "").strip()
        if not SECONDARY_LABEL.search(plain):
            return anchor
        needs_local_rule = True
        return re.sub(
            r'class="(?:[^"]*\s)?btn-primary(?:\s[^"]*)?"',
            f'class="{outline_class}"',
            anchor,
            count=1,
        )

    text = re.sub(
        r'<a[^>]*class="(?:[^"]*\s)?btn-primary(?:\s[^"]*)?"[^>]*>(?P<label>[^<]*)',
        demote,
        text,
    )

    if needs_local_rule and not has_base_css and ".btn-outline {" not in text:
        anchor_rule = re.search(r"\.btn-primary\s*\{[^}]*\}", text)
        if anchor_rule:
            text = (
                text[: anchor_rule.end()]
                + "\n    "
                + BTN_OUTLINE_LOCAL
                + text[anchor_rule.end():]
            )
    return text


def _fix_eyebrow_rules(css: str) -> str:
    def fix_rule(match: re.Match[str]) -> str:
        selector, body = match.group(1), match.group(2)
        if "eyebrow" not in selector.lower() and "kicker" not in selector.lower():
            return match.group(0)
        new_body = re.sub(
            r"color:\s*(var\(--accent[^)]*\)|" + re.escape(SAGE) + r")",
            f"color: var(--quiet, {QUIET})",
            body,
        )
        return f"{selector}{{{new_body}}}"

    return re.sub(r"([^{}]+)\{([^{}]*)\}", fix_rule, css)


def rewrite_eyebrows(text: str, is_css: bool) -> str:
    """Eyebrows and kickers are labels, not status. Quiet grey, not the accent.

    In HTML only the <style> blocks are touched: the rule-splitting regex would
    otherwise treat prose and inline JS as CSS.
    """
    if is_css:
        return _fix_eyebrow_rules(text)
    return re.sub(
        r"(<style[^>]*>)(.*?)(</style>)",
        lambda m: m.group(1) + _fix_eyebrow_rules(m.group(2)) + m.group(3),
        text,
        flags=re.S,
    )


def patch_base_css(text: str) -> str:
    """Add the missing grey token and a focus ring for plain links."""
    if "--quiet:" not in text:
        text = text.replace(
            "  --muted: #a8a8b8;",
            "  --muted: #a8a8b8;\n  --quiet: #88889a;",
            1,
        )
    if "\na:focus-visible" not in text:
        text = text.replace(
            ".cta-btn-primary:focus-visible",
            "/* Plain links had no focus style of their own and fell back to the\n"
            " * browser default; the buttons keep their own rings. */\n"
            "a:focus-visible { outline: 2px solid var(--action); outline-offset: 2px; }\n\n"
            ".cta-btn-primary:focus-visible",
            1,
        )
    text = text.replace(
        " *   lime (--accent) = success + evidence states ONLY",
        " *   sage (--accent) = success + evidence states ONLY",
    )
    text = text.replace(
        " *   coral fill      = the cluster's ONE primary action (never lime)",
        " *   coral fill      = the cluster's ONE primary action (never sage)",
    )
    return text


def convert(path: Path, text: str) -> str:
    has_base_css = "assets/css/base.css" in text
    out = swap_palette(text)
    out = rewrite_context_cta(out)
    out = rewrite_footer_pilot(out)
    if path.suffix == ".html":
        out = rewrite_btn_primary(out, has_base_css)
    out = rewrite_eyebrows(out, is_css=path.suffix == ".css")
    if path.name == "base.css":
        out = patch_base_css(out)
    return out


def read(path: Path) -> str:
    """newline="" keeps CRLF/LF/mixed files byte-identical outside our edits.

    check_line_endings.py fails CI when a change rewrites a file's newline
    convention, and site/index.html is legitimately mixed.
    """
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def write(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only; exit 1 if stale")
    args = ap.parse_args()

    changed: list[str] = []
    for path in site_files():
        text = read(path)
        out = convert(path, text)
        if out == text:
            continue
        changed.append(path.relative_to(REPO_ROOT).as_posix())
        if not args.check:
            write(path, out)

    if args.check:
        if changed:
            print(f"stale: {len(changed)} file(s) still carry the old palette")
            for rel in changed[:20]:
                print(f"  {rel}")
            return 1
        print("clean: palette and CTA colour roles are in contract")
        return 0

    print(f"rewrote {len(changed)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
