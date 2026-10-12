#!/usr/bin/env python3
"""
lint_prose.py - comprehension and AI-slop filter for insight drafts.

Stage 3 of the publish-insight skill runs this on every draft body before
the final write-up. It checks three things:

  House voice (errors, exit 1): the rules PUBLISHING.md states for all
    prose -- no "bottleneck", no em dash (U+2014). Same rules as
    scripts/lint_og_voice.py, applied to article text.

  AI slop (warnings): phrases and structures that read as machine-written
    -- throat-clearing openers, emphasis crutches, filler adverbs, business
    jargon, meta-commentary, vague declaratives, and the "not X, it's Y"
    contrast family. Pattern lists follow the stop-slop skill.

  Human comprehension (warnings): average sentence length, share of very
    long sentences, Flesch reading ease, over-long paragraphs, and acronyms
    used without being expanded on first use.

Warnings are not failures; each one must be fixed or justified in the
review. A paragraph may opt out of the house-voice errors with an
HTML comment `<!-- voice-ok: <reason> -->` placed before it, for quoting
an external title verbatim (mirrors `voice_ok` in the OG manifest).

Usage:
  python scripts/lint_prose.py body.html
  python scripts/lint_prose.py site/insights/<slug>/index.html
  python scripts/lint_prose.py draft.md --max-warnings 10

Exit codes: 0 = no errors (and warnings within --max-warnings, if set)
            1 = house-voice errors, or warnings over --max-warnings
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

EM_DASH = "—"
BOTTLENECK_RE = re.compile(r"\bbottlenecks?\b", re.I)
VOICE_OK_RE = re.compile(r"<!--\s*voice-ok:\s*[^>]*-->\s*$", re.I)

# --- slop patterns (after the stop-slop skill) ---------------------------
SLOP = {
    "throat-clearing": [
        r"\bhere'?s (the thing|what|why|how|the problem)\b", r"\bthe (uncomfortable |simple )?truth is\b",
        r"\bit turns out\b", r"\blet me be clear\b", r"\bthe reality is\b", r"\bthe real \w+ is\b",
    ],
    "emphasis crutch": [
        r"\blet that sink in\b", r"\bmake no mistake\b", r"\bthis matters because\b",
        r"\bfull stop\b", r"\bhere'?s why that matters\b",
    ],
    "filler phrase": [
        r"\bat its core\b", r"\bin today'?s\b", r"\bit'?s worth noting\b", r"\bat the end of the day\b",
        r"\bwhen it comes to\b", r"\bin a world where\b",
    ],
    "filler adverb": [
        r"\b(really|literally|genuinely|honestly|simply|actually|deeply|truly|fundamentally|"
        r"inherently|inevitably|interestingly|importantly|crucially)\b",
    ],
    "jargon": [
        r"\bnavigat(e|ing) (the |these )?(challenges|complexit)", r"\bunpack(s|ing)?\b",
        r"\blean(s|ing)? into\b", r"\blandscape\b", r"\bgame[- ]changer\b", r"\bdouble down\b",
        r"\bdeep dive\b", r"\bmoving forward\b", r"\bparadigm shift\b", r"\bdelve\b", r"\btapestry\b",
        r"\bseamless(ly)?\b", r"\brobust\b", r"\bleverag(e|es|ing)\b",
    ],
    "meta-commentary": [
        r"\blet me walk you through\b", r"\bin this (section|article|post),? (we|i)\b",
        r"\bas we'?ll see\b", r"\bthe rest of this (essay|article)\b", r"\bi want to explore\b",
    ],
    "vague declarative": [
        r"\bthe (reasons|implications|stakes|consequences) are (structural|significant|high|real)\b",
        r"\bthis is the deepest problem\b",
    ],
    "binary contrast": [
        r"\bnot because\b[^.]{0,80}\.\s*because\b", r"\bisn'?t (the problem|about)\b[^.]{0,80}\.\s*it'?s\b",
        r"\b(it'?s|is) not \w+[^.,]{0,40}, (it'?s|but)\b", r"\bthe (answer|question) isn'?t\b",
        r"\bstops being\b[^.]{0,60}\bstarts being\b", r"\bnot just\b[^.]{0,60}\bbut also\b",
    ],
    "second-tier tell": [
        r"\bthe deeper (problem|issue|version) is\b", r"\bwhat'?s missing is\b",
        r"\bin practice\b", r"\bis the right framing\b", r"\bworth (watching|pulling on|tracking)\b",
    ],
}
SLOP_RE = {k: [re.compile(p, re.I) for p in v] for k, v in SLOP.items()}

# Acronyms a technical reader needs no expansion for.
KNOWN_ACRONYMS = set("""
AI API APIS CI CD CTO CIO CEO VP VPE UI UX URL HTTP HTTPS JSON YAML SQL SDK IDE OS PR PRS
LLM LLMS GPU CPU USA UK EU US PDF HTML CSS IT QA SLA OK
MIT GPL BSD FAQ ROI
PASS WARN FAIL BLOCK ALLOW DENY NOTE TODO TBD YES NO
""".split())

LONG_SENTENCE = 30          # words
MAX_AVG_SENTENCE = 22.0     # words
MAX_LONG_SHARE = 0.15
MIN_FLESCH = 30.0           # technical audience floor
MAX_PARAGRAPH = 120         # words

SKIP_BLOCKS = re.compile(r"<(script|style|pre|code|nav|footer|header|svg|table|aside)\b.*?</\1>", re.I | re.S)
PARA_RE = re.compile(r"<(p|li|blockquote|h2|h3)\b[^>]*>(.*?)</\1>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")


def extract_paragraphs(source: str, is_html: bool) -> list[tuple[str, bool]]:
    """Return (text, voice_ok) pairs for each prose block."""
    if not is_html:
        blocks = [b for b in re.split(r"\n\s*\n", source) if b.strip()]
        out, ok = [], False
        for b in blocks:
            if b.lstrip().startswith("```"):
                continue
            if VOICE_OK_RE.search(b.strip()):
                ok = True
                continue
            out.append((re.sub(r"[#>*_`]", "", b).strip(), ok))
            ok = False
        return out
    m = re.search(r"<article\b.*?</article>", source, re.I | re.S)
    body = m.group(0) if m else source
    body = SKIP_BLOCKS.sub(" ", body)
    out = []
    for match in PARA_RE.finditer(body):
        before = body[: match.start()].rstrip()
        ok = bool(VOICE_OK_RE.search(before[-200:]))
        text = re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", match.group(2)))).strip()
        if text:
            out.append((text, ok))
    return out


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", text)
    return [p for p in parts if re.search(r"[A-Za-z]", p)]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'\-]*|\d+(?:[.,]\d+)*%?", text)


def syllables(word: str) -> int:
    w = word.lower().strip("'")
    if not w.isalpha():
        return 1
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee")):
        n -= 1
    return max(1, n)


def flesch(all_sentences: list[str]) -> float:
    ws = [w for s in all_sentences for w in words(s)]
    if not ws or not all_sentences:
        return 100.0
    syl = sum(syllables(w) for w in ws)
    return 206.835 - 1.015 * (len(ws) / len(all_sentences)) - 84.6 * (syl / len(ws))


def undefined_acronyms(paragraphs: list[str]) -> list[str]:
    seen_defined, flagged = set(), []
    for text in paragraphs:
        for m in re.finditer(r"\b([A-Z]{2,6})s?\b", text):
            acr = m.group(1)
            if acr in KNOWN_ACRONYMS or acr in seen_defined or acr in flagged:
                continue
            window = text[max(0, m.start() - 80): m.end() + 80]
            if re.search(rf"\(\s*{acr}s?\s*\)", window) or re.search(rf"{acr}s?\s*\(", window):
                seen_defined.add(acr)
            else:
                flagged.append(acr)
    return flagged


def lint(paragraphs: list[tuple[str, bool]]) -> tuple[list[str], list[str], dict]:
    errors, warnings = [], []
    all_sentences: list[str] = []
    for i, (text, voice_ok) in enumerate(paragraphs, 1):
        where = f"para {i}"
        snippet = text[:70] + ("..." if len(text) > 70 else "")
        if not voice_ok:
            if BOTTLENECK_RE.search(text):
                errors.append(f"{where}: 'bottleneck' (house voice): {snippet}")
            if EM_DASH in text:
                errors.append(f"{where}: em dash U+2014 (house voice): {snippet}")
        for kind, patterns in SLOP_RE.items():
            for rx in patterns:
                for m in rx.finditer(text):
                    warnings.append(f"{where}: slop/{kind}: '{m.group(0)}'")
        n = len(words(text))
        if n > MAX_PARAGRAPH:
            warnings.append(f"{where}: comprehension/long paragraph ({n} words)")
        sents = sentences(text)
        all_sentences.extend(sents)

    lengths = [len(words(s)) for s in all_sentences]
    total_words = sum(lengths)
    avg = total_words / len(lengths) if lengths else 0.0
    long_share = sum(1 for n in lengths if n > LONG_SENTENCE) / len(lengths) if lengths else 0.0
    score = flesch(all_sentences)
    if avg > MAX_AVG_SENTENCE:
        warnings.append(f"comprehension: average sentence {avg:.1f} words (target <= {MAX_AVG_SENTENCE:.0f})")
    if long_share > MAX_LONG_SHARE:
        warnings.append(f"comprehension: {long_share:.0%} of sentences over {LONG_SENTENCE} words "
                        f"(target <= {MAX_LONG_SHARE:.0%})")
    if score < MIN_FLESCH:
        warnings.append(f"comprehension: Flesch reading ease {score:.0f} (target >= {MIN_FLESCH:.0f})")
    for acr in undefined_acronyms([t for t, _ in paragraphs]):
        warnings.append(f"comprehension: acronym '{acr}' not expanded on first use")

    stats = {"words": total_words, "sentences": len(lengths), "avg_sentence": avg,
             "long_share": long_share, "flesch": score}
    return errors, warnings, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("path", type=Path, help="draft body (.html or .md) or a built article index.html")
    ap.add_argument("--max-warnings", type=int, default=None,
                    help="also fail when warnings exceed this count")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not args.path.is_file():
        print(f"FATAL: no such file: {args.path}", file=sys.stderr)
        return 2
    source = args.path.read_text(encoding="utf-8")
    is_html = args.path.suffix.lower() in {".html", ".htm"}
    errors, warnings, s = lint(extract_paragraphs(source, is_html))

    print(f"{args.path}: {s['words']} words, {s['sentences']} sentences, "
          f"avg {s['avg_sentence']:.1f} words/sentence, "
          f"{s['long_share']:.0%} over {LONG_SENTENCE}, Flesch {s['flesch']:.0f}")
    for e in errors:
        print(f"  ERROR    {e}")
    for w in warnings:
        print(f"  warning  {w}")
    print(f"  {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors:
        return 1
    if args.max_warnings is not None and len(warnings) > args.max_warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
