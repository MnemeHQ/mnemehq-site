#!/usr/bin/env python3
"""Load and resolve the OG card manifest.

Family comes from the URL path, never from the legacy .tag values: those
are the drift this system exists to end (30 distinct values, many of them
singletons invented for a single card).
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
IMAGES_DIR = REPO / "site" / "assets" / "images"

FAMILIES = ("editorial", "integration", "proof", "comparison", "brand")

# Order matters only in that every prefix here is unambiguous.
_PREFIX_RULES = (
    ("insights/", "editorial"),
    ("concepts/", "editorial"),
    ("integrations/", "integration"),
    ("works-with/", "integration"),
    ("supported-languages/", "integration"),
    ("demo/", "proof"),
    ("benchmark/", "proof"),
    ("architecture/", "proof"),
    ("audit/", "proof"),
    ("standards/", "proof"),
    ("docs/", "proof"),
    ("compare/", "comparison"),
    ("use-cases/", "comparison"),
)

# Exact paths only. "for/" is the hub and is brand; "for/cto/" is a persona
# page and is resolved by an explicit manifest override instead.
_BRAND_EXACT = frozenset({
    "", "about/", "founder/", "pilot/", "contact/", "for/",
    "roadmap/", "privacy/", "pricing/", "platforms/",
})


def family_for_path(rel: str) -> str | None:
    """Derive a card family from a site-relative page path.

    `rel` is the page directory relative to site/, with a trailing slash;
    the homepage is "". Returns None when the path needs an explicit
    family: in the manifest.
    """
    if rel in _BRAND_EXACT:
        return "brand"
    for prefix, family in _PREFIX_RULES:
        if rel.startswith(prefix):
            return family
    return None


MOTIFS = ("connected", "broken", "boundary", "branch",
          "stack", "intersection", "propagation", "isolated")

# Ordered: the first matching signal wins, so a slug carrying two signals
# resolves predictably rather than by dict iteration accident.
_MOTIF_SIGNALS = (
    (("drift", "divergence", "deviation", "decay"), "branch"),
    (("compaction", "forgetting", "context-loss", "gap", "break"), "broken"),
    (("boundary", "perimeter", "zero-trust", "guardrail", "scope"), "boundary"),
    (("coordination", "multi-agent", "swarm", "orchestration", "shared"), "connected"),
    (("propagation", "continuity", "memory", "provenance", "lifecycle"), "propagation"),
    (("layer", "platform", "stack", "control-plane", "infrastructure"), "stack"),
    (("intersection", "tradeoff", "versus", "-vs-", "convergence",
      "is-not-"), "intersection"),
    (("isolation", "silo", "standalone", "single-agent"), "isolated"),
)


def motif_for_slug(slug: str) -> str:
    """Pick an Editorial motif from topic signals in the slug.

    Deterministic and semantic: the geometry should mean something, so the
    motif is never hash-chosen. (The hash varies geometry *within* a motif
    -- that lives in og_geometry.py.)
    """
    low = slug.lower()
    for signals, motif in _MOTIF_SIGNALS:
        if any(s in low for s in signals):
            return motif
    return "connected"


TONES = ("neutral", "failure")

# A hub is an Editorial listing page, not a sixth family: valid only on
# "editorial". None is the default, ordinary article card.
VARIANTS = (None, "hub")


class ManifestError(Exception):
    """A manifest record is missing, malformed, or internally inconsistent."""


ROW_KINDS = ("held", "neutral", "denied")
BOX_KINDS = ("warn", "accent")
CHAIN_KINDS = ("plain", "accent", "dim")

# The proof card's row value renders at 48px Inter 500 in a column roughly
# 790px wide on a 1200x630 card -- about 33 characters fit on one line
# before it wraps. A wrapped row grows tall enough that three rows plus the
# identity bar overflow the card, so this is a hard ceiling, not a style
# preference.
ROW_VALUE_MAX = 33

# Same frame, the row label column: roughly 14 characters fit before the
# label itself threatens the row's height budget alongside a full-width
# value line.
ROW_LABEL_MAX = 14

# Proof row values already cap at 6 words in practice -- enforce it so a
# future record can't quietly grow past what the row was designed to hold.
ROW_VALUE_MAX_WORDS = 6

# Copy budgets. The owner's rule: "Never shrink type to fit excess copy.
# If it exceeds the limit, rewrite." These exist so the renderer never has
# to rescue over-long copy with a smaller font.
#
# Headline: 10 words is a hard ceiling. 9-10 words is a warning, not a
# failure -- the documented ideal is 4-7 words, but a slightly long
# headline still fits the card; it just isn't ideal.
HEADLINE_MAX_WORDS = 10
HEADLINE_WARN_WORDS = 8

# Secondary (sup) line: same rationale, same hard ceiling.
SUP_MAX_WORDS = 10


def _word_count(text: str) -> int:
    return len(text.split())


def _validate_rows(rel: str, rows: object) -> None:
    """rows (proof): a list of [label, value, kind] triples."""
    if not isinstance(rows, list):
        raise ManifestError(f"{rel or '<home>'}: rows must be a list")
    for i, row in enumerate(rows):
        if (not isinstance(row, (list, tuple))) or len(row) != 3:
            raise ManifestError(
                f"{rel or '<home>'}: rows[{i}] must be a 3-element [label, value, kind] sequence")
        label, value, kind = row
        if not isinstance(label, str) or not isinstance(value, str):
            raise ManifestError(f"{rel or '<home>'}: rows[{i}] label and value must be strings")
        if len(label) > ROW_LABEL_MAX:
            raise ManifestError(
                f"{rel or '<home>'}: rows[{i}] label is {len(label)} chars, "
                f"over the {ROW_LABEL_MAX}-char limit")
        if len(value) > ROW_VALUE_MAX:
            raise ManifestError(
                f"{rel or '<home>'}: rows[{i}] value is {len(value)} chars, "
                f"over the {ROW_VALUE_MAX}-char limit")
        if _word_count(value) > ROW_VALUE_MAX_WORDS:
            raise ManifestError(
                f"{rel or '<home>'}: rows[{i}] value is {_word_count(value)} words, "
                f"over the {ROW_VALUE_MAX_WORDS}-word limit")
        if kind not in ROW_KINDS:
            raise ManifestError(
                f"{rel or '<home>'}: rows[{i}] kind must be one of {ROW_KINDS}, got {kind!r}")


def _validate_boxes(rel: str, boxes: object) -> None:
    """boxes (comparison): exactly two {label, value, verdict, kind} mappings."""
    if not isinstance(boxes, list) or len(boxes) != 2:
        raise ManifestError(f"{rel or '<home>'}: boxes must be a list of exactly two mappings")
    for i, box in enumerate(boxes):
        if not isinstance(box, dict):
            raise ManifestError(f"{rel or '<home>'}: boxes[{i}] must be a mapping")
        for key in ("label", "value", "verdict"):
            if not isinstance(box.get(key), str):
                raise ManifestError(f"{rel or '<home>'}: boxes[{i}] missing/invalid {key!r}")
        if box.get("kind") not in BOX_KINDS:
            raise ManifestError(
                f"{rel or '<home>'}: boxes[{i}] kind must be one of {BOX_KINDS}, "
                f"got {box.get('kind')!r}")


def _validate_chain(rel: str, chain: object) -> None:
    """chain (integration): a list of {text, kind} pills."""
    if not isinstance(chain, list):
        raise ManifestError(f"{rel or '<home>'}: chain must be a list")
    for i, item in enumerate(chain):
        if not isinstance(item, dict):
            raise ManifestError(f"{rel or '<home>'}: chain[{i}] must be a mapping")
        if not isinstance(item.get("text"), str):
            raise ManifestError(f"{rel or '<home>'}: chain[{i}] missing/invalid 'text'")
        if item.get("kind") not in CHAIN_KINDS:
            raise ManifestError(
                f"{rel or '<home>'}: chain[{i}] kind must be one of {CHAIN_KINDS}, "
                f"got {item.get('kind')!r}")


def load(path: Path) -> dict[str, dict]:
    """Read cards.yaml into {page-path: raw record}."""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ManifestError(f"{path}: top level must be a mapping")
    return data


def _slug(rel: str) -> str:
    return rel.rstrip("/").rsplit("/", 1)[-1] if rel.strip("/") else "home"


def _norm(text: str) -> str:
    """Whitespace-insensitive comparison key."""
    return re.sub(r"\s+", " ", text).strip()


def _headline_from_path(rel: str) -> str:
    """Bootstrap only. Never reached in strict mode."""
    return _slug(rel).replace("-", " ").strip().capitalize()


def resolve(rel: str, raw: dict | None, strict: bool = False) -> dict:
    """Produce a fully-populated card record for one page.

    Strict mode is what CI and deploy use: every page must carry an
    explicit record. Derived values exist for local development and
    new-page bootstrapping only -- shipping a silently-derived generic
    card is how the drift this system replaces was created.
    """
    if raw is None:
        if strict:
            raise ManifestError(f"{rel or '<home>'}: no manifest record (strict mode)")
        raw = {}
    if not isinstance(raw, dict):
        raise ManifestError(f"{rel or '<home>'}: record must be a mapping")

    family = raw.get("family") or family_for_path(rel)
    if family is None:
        raise ManifestError(
            f"{rel or '<home>'}: path does not resolve to a family; add an explicit family:")
    if family not in FAMILIES:
        raise ManifestError(f"{rel or '<home>'}: unknown family {family!r}")

    warnings: list[str] = []

    headline = raw.get("headline") or _headline_from_path(rel)

    headline_words = _word_count(headline)
    if headline_words > HEADLINE_MAX_WORDS:
        raise ManifestError(
            f"{rel or '<home>'}: headline is {headline_words} words, "
            f"over the {HEADLINE_MAX_WORDS}-word limit")
    if headline_words > HEADLINE_WARN_WORDS:
        warnings.append(
            f"{rel or '<home>'}: headline is {headline_words} words (ideal 4-7)")

    sup = raw.get("sup")
    if sup is not None:
        if family == "editorial":
            raise ManifestError(
                f"{rel or '<home>'}: family 'editorial' does not allow a 'sup'")
        sup_words = _word_count(sup)
        if sup_words > SUP_MAX_WORDS:
            message = (f"{rel or '<home>'}: sup is {sup_words} words, "
                       f"over the {SUP_MAX_WORDS}-word limit")
            if family == "brand":
                # Brand secondaries are pending the owner's own keep-or-drop
                # editorial decision (tracked separately). Until that lands,
                # an over-budget brand sup warns instead of failing strict
                # mode. TEMPORARY: remove this exemption once the brand
                # sups are resolved.
                warnings.append(message)
            else:
                raise ManifestError(message)

    image = raw.get("image")
    if image is not None:
        if family != "brand":
            raise ManifestError(
                f"{rel or '<home>'}: 'image' is only valid on the brand family, "
                f"got family {family!r}")
        if not (IMAGES_DIR / image).is_file():
            raise ManifestError(
                f"{rel or '<home>'}: image {image!r} not found under {IMAGES_DIR}")

    lines = raw.get("lines")
    if lines is None:
        lines = [headline]
    else:
        if not isinstance(lines, list) or not all(isinstance(x, str) for x in lines):
            raise ManifestError(f"{rel or '<home>'}: lines must be a list of strings")
        if _norm(" ".join(lines)) != _norm(headline):
            raise ManifestError(
                f"{rel or '<home>'}: lines do not rejoin to headline\n"
                f"  headline: {_norm(headline)!r}\n"
                f"  lines:    {_norm(' '.join(lines))!r}")

    tone = raw.get("tone", "neutral")
    if tone not in TONES:
        raise ManifestError(f"{rel or '<home>'}: tone must be one of {TONES}, got {tone!r}")

    motif = raw.get("motif") or motif_for_slug(_slug(rel))
    if motif not in MOTIFS:
        raise ManifestError(f"{rel or '<home>'}: unknown motif {motif!r}")

    variant = raw.get("variant")
    if variant not in VARIANTS:
        raise ManifestError(f"{rel or '<home>'}: variant must be one of {VARIANTS}, got {variant!r}")
    if variant == "hub" and family != "editorial":
        raise ManifestError(
            f"{rel or '<home>'}: variant: hub is only valid on the editorial family, "
            f"got family {family!r}")

    rows = raw.get("rows")
    if rows is not None:
        _validate_rows(rel, rows)

    boxes = raw.get("boxes")
    if boxes is not None:
        _validate_boxes(rel, boxes)

    badge = raw.get("badge")
    if badge is not None and not isinstance(badge, str):
        raise ManifestError(f"{rel or '<home>'}: badge must be a string")

    name = raw.get("name")
    if name is not None and not isinstance(name, str):
        raise ManifestError(f"{rel or '<home>'}: name must be a string")

    chain = raw.get("chain")
    if chain is not None:
        _validate_chain(rel, chain)

    # The owner's explicit ruling: these family-specific fields are what
    # the template tokens need to render. Missing them in strict mode is
    # exactly the data gap that shipped 85 cards with literal {{token}}
    # text on the card face -- strict must catch it, not paper over it.
    if strict:
        if family == "proof" and not rows:
            raise ManifestError(f"{rel or '<home>'}: family 'proof' requires 'rows' (strict mode)")
        if family == "comparison" and not boxes:
            raise ManifestError(
                f"{rel or '<home>'}: family 'comparison' requires 'boxes' (strict mode)")
        if family == "integration":
            missing = [name_ for name_, value in
                       (("badge", badge), ("name", name), ("chain", chain)) if not value]
            if missing:
                raise ManifestError(
                    f"{rel or '<home>'}: family 'integration' requires "
                    f"{', '.join(missing)} (strict mode)")
        if family == "brand" and not image:
            raise ManifestError(f"{rel or '<home>'}: family 'brand' requires 'image' (strict mode)")

    return {
        "path": rel,
        "family": family,
        "headline": headline,
        "lines": lines,
        "accent": raw.get("accent"),
        "sup": raw.get("sup"),
        "image": image,
        "rows": rows,
        "boxes": boxes,
        "badge": badge,
        "name": name,
        "chain": chain,
        "tone": tone,
        "motif": motif,
        "alt": raw.get("alt") or headline,
        "voice_ok": raw.get("voice_ok"),
        "variant": variant,
        "subtitle": raw.get("subtitle"),
        "warnings": warnings,
    }
