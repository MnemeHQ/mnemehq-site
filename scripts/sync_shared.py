#!/usr/bin/env python3
"""
Sync canonical nav and footer snippets across all site HTML files.
Skips og-*.html templates, site/_snippets/, and the generated audit SPA shell.
Run before deploy or any time snippets change.
"""
import re
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"
SNIPPETS = SITE / "_snippets"

def load(name):
    return (SNIPPETS / name).read_text(encoding="utf-8").rstrip("\n")

NAV_HTML      = load("nav.html")
FOOTER_HTML   = load("footer.html")
FOOTER_CSS    = load("footer.css")
HAMBURGER_CSS = load("nav-hamburger.css")
HAMBURGER_JS  = load("nav-hamburger.js")
ACTIVE_JS     = load("nav-active.js")
CTA_ANALYTICS_JS = load("cta-analytics.js")

NAV_PAT    = re.compile(r"<nav>(.*?)</nav>", re.DOTALL)
# Canonical site footers carry an inline style signature; article/section
# footers use class attributes and must NOT be caught by this pattern.
FOOTER_PAT = re.compile(
    r'<footer style="border-top: 1px solid var\(--border\); padding: 3rem 2rem 1\.5rem; text-align: left;">(.*?)</footer>',
    re.DOTALL,
)

HAMBURGER_JS_BLOCK = f"<script>\n{HAMBURGER_JS}\n</script>"
ACTIVE_JS_BLOCK    = f"<script><!-- nav-active -->\n{ACTIVE_JS}\n</script>"

# â”€â”€ Accessibility primitives â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SKIP_LINK_HTML = (
    '<a href="#main-content" class="skip-link">Skip to content</a>'
)
SKIP_LINK_CSS = (
    ".skip-link { position: absolute; left: -9999px; top: 0; z-index: 1000; "
    "background: var(--accent, #c8f060); color: #0c0c0d; padding: 0.6rem 1.1rem; "
    "border-radius: 0 0 6px 0; font-family: 'DM Mono', monospace; font-size: 0.8rem; "
    "text-decoration: none; }\n"
    "    .skip-link:focus { left: 0; }"
)
REDUCED_MOTION_CSS = (
    "@media (prefers-reduced-motion: reduce) {\n"
    "      html { scroll-behavior: auto !important; }\n"
    "      *, *::before, *::after { transition-duration: .01ms !important; animation-duration: .01ms !important; }\n"
    "    }"
)

# â”€â”€ Marketing pixels â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# REMOVED: RB2B visitor identification + its consent banner.
# The patterns below are retained so the previously-injected blocks are stripped
# from any page that still carries them. Nothing is injected.
MK_HEAD_BLOCK = MK_BODY_BLOCK = ""

MK_HEAD_PAT = re.compile(r"\n?<!-- mneme:marketing-head:start -->.*?<!-- mneme:marketing-head:end -->", re.DOTALL)
MK_BODY_PAT = re.compile(r"<!-- mneme:marketing-body:start -->.*?<!-- mneme:marketing-body:end -->\n?", re.DOTALL)

updated = []
skipped_og = []
skipped_snippet = []

for html in sorted(SITE.rglob("*.html")):
    # Vite owns this shell; its nav is rendered by React at runtime.
    if html.relative_to(SITE).as_posix() == "audit/workspace/index.html":
        continue
    # Skip OG templates
    if html.name.startswith("og-"):
        skipped_og.append(html.name)
        continue
    # Skip snippet files themselves
    if SNIPPETS in html.parents:
        skipped_snippet.append(str(html.relative_to(SITE)))
        continue

    raw = html.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8")
    original = text

    def adapt(s):
        return s.replace("\n", "\r\n") if crlf else s

    # 1. Replace nav
    text = NAV_PAT.sub(adapt(NAV_HTML), text)

    # Pages linking base.css already carry the shared hamburger/footer/skip/
    # reduced-motion rules externally; only stamp the stylesheet reference.
    has_base_css = "/assets/css/base.css" in text

    # 2. Inject hamburger CSS if missing (use CSS rule sentinel, not HTML class attr)
    if not has_base_css and ".nav-hamburger {" not in text:
        if "</style>" in text:
            css_block = adapt("\n    " + HAMBURGER_CSS.replace("\n", "\n    "))
            text = text.replace("</style>", css_block + "\n  </style>", 1)
        else:
            print(f"  WARN: no </style> in {html.relative_to(SITE)} â€” hamburger CSS not injected")

    # 2b. Inject canonical footer link styling where a page-local rule is absent.
    # Keeping this in the shared sync path prevents default browser blue/purple
    # links on pages whose templates predate the footer CSS convention.
    if not has_base_css and "footer a {" not in text:
        if "</style>" in text:
            css_block = adapt("\n    " + FOOTER_CSS.replace("\n", "\n    "))
            text = text.replace("</style>", css_block + "\n  </style>", 1)
        else:
            print(f"  WARN: no </style> in {html.relative_to(SITE)} â€” footer CSS not injected")

    # 2c. Skip link: markup before the first nav, target id on main, CSS.
    # Sentinel is the raw attribute value â€” '.skip-link' with a dot only
    # exists in the CSS rule, not the markup, and using it here made this
    # step re-insert on every sync run.
    if 'class="skip-link"' not in text and "<body" in text:
        m = re.search(r"<nav[ >]", text)
        if m:
            text = text[:m.start()] + adapt(SKIP_LINK_HTML) + "\n" + text[m.start():]
        if re.search(r"<main(\s|>)", text):
            text = re.sub(r'<main(?![^>]*\bid=)', '<main id="main-content" tabindex="-1"', text, count=1)
        else:
            print(f"  WARN: no <main> in {html.relative_to(SITE)} â€” skip link target missing")

    # 2d. Skip-link CSS.
    if not has_base_css and 'class="skip-link"' in text and ".skip-link {" not in text and "</style>" in text:
        css_block = adapt("\n    " + SKIP_LINK_CSS.replace("\n", "\n    "))
        text = text.replace("</style>", css_block + "\n  </style>", 1)

    # 2e. Reduced-motion guard for templates without one (home-v2 has its own).
    if not has_base_css and "prefers-reduced-motion" not in text and "</style>" in text:
        css_block = adapt("\n    " + REDUCED_MOTION_CSS.replace("\n", "\n    "))
        text = text.replace("</style>", css_block + "\n  </style>", 1)

    # 2f. Pages whose site nav wrapper is <nav class="site"> never match the
    # plain-<nav> replacement above; patch the links container by attribute.
    if '<div class="nav-links">' in text and 'id="primary-nav"' not in text:
        text = text.replace('<div class="nav-links">', '<div class="nav-links" id="primary-nav">', 1)

    # 2g. Stamp base.css onto pages that lack it. New pages spawned from old
    # templates (article copies, generator output predating base.css) inherit
    # the fat inline chrome; linking the shared stylesheet here starts every
    # page on the shared system without touching its local rules. The
    # homepage is excluded on purpose: its coral/home-v2 token system is
    # self-contained and must not pick up the standard tokens.
    if (
        "/assets/css/base.css" not in text
        and "</style>" in text
        and 'class="home-v2"' not in text
        and html.relative_to(SITE).as_posix() != "index.html"
    ):
        anchor_link = '<link rel="stylesheet" href="/assets/css/fonts.css">'
        link_tag = '<link rel="stylesheet" href="/assets/css/base.css?v=20260826">'
        if anchor_link in text:
            text = text.replace(anchor_link, anchor_link + "\n  " + link_tag, 1)
        else:
            m2 = re.search(r"<style>", text)
            if m2:
                text = text[:m2.start()] + "  " + link_tag + "\n" + text[m2.start():]

    # 3. Inject hamburger JS if missing — check for any toggle handler, not just our exact block
    if "classList.toggle" not in text:
        if "</body>" in text:
            text = text.replace("</body>", adapt(HAMBURGER_JS_BLOCK) + adapt("\n") + "</body>", 1)
        else:
            print(f"  WARN: no </body> in {html.relative_to(SITE)} â€” hamburger JS not injected")

    # 4. Inject active-link JS if missing
    if "nav-active" not in text:
        if "</body>" in text:
            text = text.replace("</body>", adapt(ACTIVE_JS_BLOCK) + adapt("\n") + "</body>", 1)
        else:
            print(f"  WARN: no </body> in {html.relative_to(SITE)} â€” active-link JS not injected")

    # 4b. Inject/refresh CTA analytics handler (idempotent via marker)
    CTA_JS_BLOCK = "<script><!-- cta-analytics -->\n" + CTA_ANALYTICS_JS + "\n</script>"
    CTA_JS_PAT = re.compile(r"<script><!-- cta-analytics -->.*?</script>", re.DOTALL)
    if "cta-analytics" in text:
        text = CTA_JS_PAT.sub((lambda _m: adapt(CTA_JS_BLOCK)), text)
    elif "dataLayer" not in text:
        pass  # page has no dataLayer at all (non-GTM template); skip silently
    elif "</body>" in text:
        text = text.replace("</body>", adapt(CTA_JS_BLOCK) + adapt("\n") + "</body>", 1)
    else:
        print(f"  WARN: no </body> in {html.relative_to(SITE)} â€” cta analytics not injected")

    # 5. Replace footer (plain <footer> only, not <footer class=...>)
    text = FOOTER_PAT.sub(adapt(FOOTER_HTML), text)

    # 6. Strip any previously-injected consent/pixel blocks (idempotent via markers).
    #    lambda repl avoids re's backslash interpretation of the snippet JS.
    if MK_HEAD_PAT.search(text):
        text = MK_HEAD_PAT.sub((lambda _m: "\n" + adapt(MK_HEAD_BLOCK)) if MK_HEAD_BLOCK else (lambda _m: ""), text)
    elif MK_HEAD_BLOCK and "<!-- End Google Tag Manager -->" in text:
        text = text.replace("<!-- End Google Tag Manager -->",
                            "<!-- End Google Tag Manager -->\n" + adapt(MK_HEAD_BLOCK), 1)
    elif MK_HEAD_BLOCK and "</head>" in text:
        text = text.replace("</head>", adapt(MK_HEAD_BLOCK) + adapt("\n") + "</head>", 1)
    elif MK_HEAD_BLOCK:
        print(f"  WARN: no head anchor in {html.relative_to(SITE)} â€” consent head not injected")

    # 7. Consent banner â€” before </body>, idempotent via markers.
    if MK_BODY_PAT.search(text):
        text = MK_BODY_PAT.sub((lambda _m: adapt(MK_BODY_BLOCK) + adapt("\n")) if MK_BODY_BLOCK else (lambda _m: ""), text)
    elif MK_BODY_BLOCK and "</body>" in text:
        text = text.replace("</body>", adapt(MK_BODY_BLOCK) + adapt("\n") + "</body>", 1)
    elif MK_BODY_BLOCK:
        print(f"  WARN: no </body> in {html.relative_to(SITE)} â€” consent banner not injected")

    if text != original:
        html.write_bytes(text.encode("utf-8"))
        updated.append(f"  {html.relative_to(SITE)}")

print(f"Updated {len(updated)} files:")
for line in updated:
    print(line)
print(f"\nSkipped {len(skipped_og)} og-* templates, {len(skipped_snippet)} snippet files")
