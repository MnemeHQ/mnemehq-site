#!/usr/bin/env python3
"""
find_overlap.py - rank existing mnemehq.com pages that compete with a
proposed page for the same search intent (cannibalisation check).

Used in Stage 2 of the publish-insight skill: every scope brief's overlap
verdict must cite this script's output for the proposed title and keywords.

It scores each published page under site/ (insights, concepts, compare,
for, use-cases, docs and other hubs) by how many of the query's terms appear
in the page's <title>, <h1>, meta description, lede (standfirst), OG image
alt text and URL slug, weighted by how rare each term is across the site,
with a bonus for matching two-word phrases. It reads no further into the
body. It is a lexical screen, not a judge: a high score means "read this page
before writing", and a low score does not prove the intent is free. Search
the body as well (git grep for the key figures, entities and source names)
before calling a proposal clear.

Usage:
  python scripts/find_overlap.py "Multi-Agent Coding Needs More Than Shared Context"
  python scripts/find_overlap.py "proposed title" --keywords "multi-agent coding,agent coordination"
  python scripts/find_overlap.py "proposed title" --top 15 --min-score 20

Exit codes: 0 = ranking printed (whatever it found); 2 = the query had no
searchable terms. The script informs a human decision; it never fails a build.
"""
from __future__ import annotations

import argparse
import html
import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"

# Index surfaces, not competing pages.
SKIP_DIRS = {"insights/all", "insights/topics", "_templates", "assets", "og", ".well-known"}

STOPWORDS = set("""
a an and are as at be but by can do does for from has have how in into is it its
mneme hq mnemehq no not of on or our s so than that the their them they this to
too vs was we what when where which who why will with without you your more most
need needs new just
""".split())

WEIGHTS = {"title": 3, "h1": 2, "slug": 2, "description": 1, "lede": 1, "image_alt": 1}
PHRASE_BONUS = 2

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.I)
# The standfirst carries an article's headline finding (e.g. "240% ... 30%")
# when the title is a thesis; the OG image alt text often restates it.
LEDE_RE = re.compile(r'<p[^>]*class="[^"]*\barticle-lede\b[^"]*"[^>]*>(.*?)</p>', re.I | re.S)
IMAGE_ALT_RE = re.compile(r'<meta\s+property="og:image:alt"\s+content="([^"]*)"', re.I)
TAG_RE = re.compile(r"<[^>]+>")


def stem(word: str) -> str:
    """Light plural/gerund stemming: policies->policy, branches->branch,
    releases->release, pipelines->pipeline, engineering->engineer."""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith(("sses", "xes", "zes", "ches", "shes")):
        return word[:-2]
    if word.endswith("ing") and len(word) - 3 >= 4:
        return word[:-3]
    if word.endswith("s") and not word.endswith(("ss", "us", "is")) and len(word) > 3:
        return word[:-1]
    return word


def terms(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [stem(w) for w in words if w not in STOPWORDS and len(w) > 1]


def phrases(tokens: list[str]) -> set[str]:
    return {f"{a} {b}" for a, b in zip(tokens, tokens[1:])}


def clean(fragment: str) -> str:
    text = html.unescape(TAG_RE.sub(" ", fragment))
    text = re.sub(r"\s*[|–—-]\s*Mneme( HQ)?( Concepts)?\s*$", "", text.strip())
    return re.sub(r"\s+", " ", text)


def first(regex: re.Pattern, source: str) -> str:
    m = regex.search(source)
    return clean(m.group(1)) if m else ""


def load_pages() -> list[dict]:
    pages = []
    for index in sorted(SITE.rglob("index.html")):
        rel = index.parent.relative_to(SITE).as_posix()
        if rel == ".":
            rel = ""
        if any(rel == d or rel.startswith(d + "/") for d in SKIP_DIRS):
            continue
        source = index.read_text(encoding="utf-8", errors="replace")
        pages.append({
            "path": "/" + (rel + "/" if rel else ""),
            "title": first(TITLE_RE, source),
            "h1": first(H1_RE, source),
            "description": first(DESC_RE, source),
            "lede": first(LEDE_RE, source),
            "image_alt": first(IMAGE_ALT_RE, source),
            "slug": rel.rsplit("/", 1)[-1].replace("-", " "),
        })
    return pages


def rarity(pages: list[dict]) -> dict[str, float]:
    """Inverse document frequency over each page's title, h1, description and slug.

    Words on most pages ("ai", "governance", "coding") count for little;
    words on few pages ("frontier", "bottleneck") count for a lot.
    """
    df: dict[str, int] = {}
    for page in pages:
        seen = set()
        for field in WEIGHTS:
            seen |= set(terms(page[field]))
        for t in seen:
            df[t] = df.get(t, 0) + 1
    n = len(pages)
    return {t: math.log((n + 1) / (c + 1)) for t, c in df.items()}


def score(page: dict, q_terms: set[str], q_phrases: set[str],
          idf: dict[str, float]) -> tuple[float, list[str]]:
    total, hits = 0.0, set()
    default = max(idf.values(), default=1.0)
    for field, weight in WEIGHTS.items():
        tokens = terms(page[field])
        matched = q_terms & set(tokens)
        total += weight * sum(idf.get(t, default) for t in matched)
        hits |= matched
        shared = q_phrases & phrases(tokens)
        total += PHRASE_BONUS * weight * len(shared)
        hits |= shared
    return total, sorted(hits)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("title", help="proposed page title")
    ap.add_argument("--keywords", default="",
                    help="comma-separated target keywords, added to the query")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--min-score", type=float, default=10.0)
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    query_text = " ".join([args.title] + args.keywords.split(","))
    q_tokens = terms(query_text)
    q_terms, q_phrases = set(q_tokens), set()
    for chunk in [args.title] + args.keywords.split(","):
        q_phrases |= phrases(terms(chunk))
    if not q_terms:
        print("FATAL: query has no searchable terms", file=sys.stderr)
        return 2

    pages = load_pages()
    idf = rarity(pages)
    ranked = []
    for page in pages:
        s, hits = score(page, q_terms, q_phrases, idf)
        if s >= args.min_score:
            ranked.append((s, page, hits))
    ranked.sort(key=lambda r: (-r[0], r[1]["path"]))

    print(f"query terms: {', '.join(sorted(q_terms))}")
    if not ranked:
        print("no page scored at or above --min-score; check intent by hand anyway")
        return 0
    for s, page, hits in ranked[: args.top]:
        print(f"{s:>5.1f}  {page['path']}")
        print(f"     {page['title'] or page['h1']}")
        print(f"     matched: {', '.join(hits)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
