"""Stage 1: link site/assets/css/base.css into every standard template and
remove page-local rules that are byte-equivalent (normalized) to it.

Safety model:
- base.css is linked BEFORE all inline styles -> any rule we fail to
  remove still wins locally; nothing can visually regress via cascade.
- Only exact normalized matches are removed.
- Excluded: og-* templates, _snippets, the user's WIP files, homepage
  (its coral/home-v2 system is intentionally self-contained).
"""
import re
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"
BASE_CSS_REL = "/assets/css/base.css"

# User's in-flight article registration - hands off.
WIP = {
    "scripts/ensure_og_coverage.py",
    "scripts/generate_og_images.py",
    "site/insights/all/index.html",
    "site/insights/index.html",
    "site/insights/topics/ai-coding-agents/index.html",
    "site/sitemap.xml",
}
EXCLUDE_NAMES_PREFIX = ("og-",)


def iter_pages():
    for p in sorted(SITE.rglob("*.html")):
        rel = p.relative_to(SITE.parent)
        rp = p.relative_to(SITE).as_posix()
        if p.name.startswith(EXCLUDE_NAMES_PREFIX):
            continue
        if "_snippets" in p.parts:
            continue
        if rel.as_posix() in WIP or ("site/" + rp) in WIP:
            continue
        if rp == "index.html":  # homepage keeps its self-contained system
            continue
        yield p


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse_rules(css: str, media=""):
    """Yield (media, selector_norm, full_text_span, start, end) top-level rules."""
    rules = []
    i = 0
    n = len(css)
    while i < n:
        b = css.find("{", i)
        if b == -1:
            break
        head = css[i:b]
        # find matching close brace
        depth = 1
        j = b + 1
        while j < n and depth:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        body = css[b + 1:j - 1]
        sel = norm(head.rstrip("{"))
        if sel.startswith("@media"):
            for inner_media, inner_sel, span, s2, e2 in parse_rules(body, sel):
                rules.append((inner_media or sel, inner_sel,
                              css.index("{", i) if False else None, None, None))
            # store spans relative to body for inner handling below
        else:
            rules.append((media, sel, None, i, j))
        i = j
    return rules


def dedup(css: str, base_keys: set) -> str:
    """Remove top-level rules and @media-inner rules matching base_keys."""
    out = []
    i = 0
    n = len(css)
    while i < n:
        b = css.find("{", i)
        if b == -1:
            out.append(css[i:])
            break
        head = css[i:b]
        sel = norm(head.rstrip("{ \t\r\n"))
        depth = 1
        j = b + 1
        while j < n and depth:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        body = css[b + 1:j - 1]
        trailing = css[j:j+1]  # usually } consumed; keep newline after

        if sel.startswith("@media"):
            new_body = dedup_inner(body, base_keys, sel)
            if norm(new_body):
                out.append(css[i:j])
            else:
                # drop empty media block including one trailing newline
                k = j
                while k < n and css[k] in "\r\n":
                    k += 1
                i = k
                continue
        else:
            key = (sel, norm(body))
            if key not in base_keys:
                out.append(css[i:j])
        i = j
    return "".join(out)


def dedup_inner(body: str, base_keys: set, media: str) -> str:
    out = []
    i = 0
    n = len(body)
    while i < n:
        b = body.find("{", i)
        if b == -1:
            out.append(body[i:])
            break
        head = body[i:b]
        sel = norm(head.rstrip("{ \t\r\n"))
        depth = 1
        j = b + 1
        while j < n and depth:
            if body[j] == "{":
                depth += 1
            elif body[j] == "}":
                depth -= 1
            j += 1
        rbody = body[b + 1:j - 1]
        key = (media, sel, norm(rbody))
        if key not in base_keys:
            out.append(body[i:j])
        i = j
    return "".join(out)


def build_base_keys() -> set:
    css = (SITE / "assets/css/base.css").read_text(encoding="utf-8")
    keys = set()
    # top-level
    i = 0
    n = len(css)
    while i < n:
        b = css.find("{", i)
        if b == -1:
            break
        head = css[i:b]
        sel = norm(head.rstrip("{ \t\r\n"))
        depth = 1
        j = b + 1
        while j < n and depth:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        body = css[b + 1:j - 1]
        if sel.startswith("@media"):
            m = sel
            ii = 0
            nn = len(body)
            while ii < nn:
                bb = body.find("{", ii)
                if bb == -1:
                    break
                hh = body[ii:bb]
                ss = norm(hh.rstrip("{ \t\r\n"))
                dd = 1
                jj = bb + 1
                while jj < nn and dd:
                    if body[jj] == "{":
                        dd += 1
                    elif body[jj] == "}":
                        dd -= 1
                    jj += 1
                rb = body[bb + 1:jj - 1]
                keys.add((m, ss, norm(rb)))
                ii = jj
        elif sel.startswith("@"):  # ignore other at-rules
            pass
        else:
            keys.add((sel, norm(body)))
        i = j
    return keys


LINK_TAG = f'  <link rel="stylesheet" href="{BASE_CSS_REL}">\n'


def insert_link(html: str) -> tuple[str, bool]:
    if BASE_CSS_REL in html:
        return html, False
    anchor = '<link rel="stylesheet" href="/assets/css/fonts.css">'
    if anchor in html:
        return html.replace(anchor, anchor + "\n" + LINK_TAG.rstrip("\n"), 1), True
    m = re.search(r"<style>", html)
    if m:
        return html[:m.start()] + LINK_TAG + html[m.start():], True
    return html, False


def main():
    base_keys = build_base_keys()
    print(f"base rules indexed: {len(base_keys)}")
    linked = deduped_files = 0
    total_removed = 0

    for p in iter_pages():
        raw = p.read_bytes()
        crlf = b"\r\n" in raw
        t = raw.decode("utf-8")
        orig = t

        t, did_link = insert_link(t)
        linked += int(did_link)

        # dedup inside every style block
        def repl(m):
            nonlocal total_removed
            block = m.group(0)
            before = norm(block).count(";") + norm(block).count("}")
            new = dedup(block, base_keys)
            after = norm(new).count(";") + norm(block).count("}")
            total_removed += max(0, before - after)
            return new
        t = re.sub(r"(?s)<style>.*?</style>", repl, t)

        if t != orig:
            p.write_bytes(t.encode("utf-8"))
            deduped_files += 1

    print(f"linked base.css: {linked} files")
    print(f"files with rules removed: {deduped_files}")
    print(f"approx rules removed: {total_removed}")


if __name__ == "__main__":
    main()
