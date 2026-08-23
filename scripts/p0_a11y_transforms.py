"""P0 a11y transforms applied mechanically across site templates.

Each function is idempotent. Run once; safe to re-run.
"""
import re
import sys
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"


def iter_pages():
    for p in sorted(SITE.rglob("*.html")):
        if p.name.startswith("og-"):
            continue
        if "_snippets" in p.parts:
            continue
        yield p


def fix_nav_cta_specificity(text):
    """Raise .btn-nav-cta color-rule specificity above '.nav-links a'.

    Only touches the standalone base + hover rules. Layout-only references
    (media queries, :not() lists) are left alone. Homepage excluded by caller
    because .home-v2 .btn-nav-cta (coral) must keep winning there.
    """
    n = 0

    def sub_base(m):
        nonlocal n
        n += 1
        return m.group(0)

    # base rule
    new, k = re.subn(r"(?<![\w.-])\.btn-nav-cta \{", ".nav-links a.btn-nav-cta {", text)
    n += k
    # hover rule
    new, k = re.subn(r"(?<![\w.-])\.btn-nav-cta:hover \{", ".nav-links a.btn-nav-cta:hover {", new)
    n += k
    # revert layout-only refs that we accidentally renamed back
    new = new.replace(".nav-links a.btn-nav-cta { margin-top", ".btn-nav-cta { margin-top")
    return new, n


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "cta"
    changed = 0
    for p in iter_pages():
        rel = p.relative_to(SITE)
        raw = p.read_bytes()
        crlf = b"\r\n" in raw
        text = raw.decode("utf-8")
        original = text

        if which == "cta":
            if rel == Path("index.html"):
                continue
            text, _ = fix_nav_cta_specificity(text)

        if text != original:
            p.write_bytes(text.encode("utf-8"))
            changed += 1
            print(f"  fixed {rel}")
    print(f"{which}: {changed} files changed")


if __name__ == "__main__":
    main()
