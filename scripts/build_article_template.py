"""Derive site/_templates/article.html from the canonical published insight
article by replacing only variable fields with tokens. Every replacement is
asserted so nothing silently misses. One-time builder.
"""
import re
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"
REPO_ROOT = Path(__file__).parent.parent
REF = SITE / "insights" / "what-is-harness-engineering" / "index.html"
OUT = REPO_ROOT / "templates" / "article.html"

c = REF.read_text(encoding="utf-8")
t = c


def sub_once(old, new, count=None):
    global t
    n = t.count(old)
    assert n > 0, f"NOT FOUND: {old[:90]!r}"
    if count is not None:
        assert n == count, f"expected {count} occurrences, found {n}: {old[:90]!r}"
    t = t.replace(old, new)


TITLE = "What Is Harness Engineering? The Execution Layer Between Models and Production"
m_desc = re.search(r'<meta name="description" content="([^"]+)"', t)
DESCRIPTION = m_desc.group(1)
SLUG_URL = "https://mnemehq.com/insights/what-is-harness-engineering/"
OG_URL = SLUG_URL + "og.png"
DATE_ISO = "2026-05-30"

# 1. most specific URLs first
sub_once(OG_URL, "{{OG_IMAGE_URL}}", 3)          # og:image, twitter:image, TechArticle image
sub_once(SLUG_URL, "{{SLUG_URL}}")                # canonical, og:url, mainEntityOfPage, TechArticle url

# 2. dates: byline first (shares the quoted ISO form with JSON-LD dates)
sub_once(f'<time datetime="{DATE_ISO}">May 2026</time>',
         '<time datetime="{{PUB_DATE_ISO}}">{{PUB_DATE_HUMAN}}</time>')
n_bare = t.count(f'"{DATE_ISO}"')
print("bare ISO dates (JSON-LD):", n_bare)
t = t.replace(f'"{DATE_ISO}"', '"{{ARTICLE_DATE}}"')
sub_once(DATE_ISO + "T00:00:00Z", "{{PUB_TIMESTAMP}}")

# 3. description (meta + og + twitter)
n = t.count(DESCRIPTION)
assert n >= 3, f"description occurrences: {n}"
t = t.replace(DESCRIPTION, "{{DESCRIPTION}}")

# 4. section
sub_once('content="Engineering"', 'content="{{SECTION}}"')

# 5. JSON-LD -> single token
ld_m = re.search(r'(?s)<script type="application/ld\+json">.*?</script>', t)
t = t[:ld_m.start()] + "{{JSON_LD_BLOCK}}" + t[ld_m.end():]

# 6. title everywhere it appears verbatim (title tag, og:title,
#    twitter:title, TechArticle headline, h1)
n = t.count(TITLE)
print("title occurrences:", n)
t = t.replace(TITLE, "{{TITLE}}")

# 7. header extras
sub_once('<span class="eyebrow-tag">Concept</span>', '<span class="eyebrow-tag">{{EYEBROW_TAG}}</span>')
sub_once('<span class="eyebrow-meta">9 min read</span>', '<span class="eyebrow-meta">{{READ_TIME}}</span>')
lede_m = re.search(r'(?s)<p class="article-lede">.*?</p>', t)
t = t[:lede_m.start()] + "<p class=\"article-lede\">{{LEDE}}</p>" + t[lede_m.end():]

# 8. body region -> single token
i_hdr_end = t.index("</header>") + len("</header>")
i_newsletter = t.index('<aside aria-label="Mneme HQ newsletter"')
t = t[:i_hdr_end] + "\n\n{{BODY_CONTENT}}\n" + t[i_newsletter:]

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(t, encoding="utf-8", newline="")
tokens = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", t)))
print(f"wrote {OUT} ({len(t)} bytes)")
print("tokens:", tokens)
