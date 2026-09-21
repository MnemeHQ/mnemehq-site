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

    headline = raw.get("headline") or _headline_from_path(rel)

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

    return {
        "path": rel,
        "family": family,
        "headline": headline,
        "lines": lines,
        "accent": raw.get("accent"),
        "sup": raw.get("sup"),
        "rows": raw.get("rows"),
        "tone": tone,
        "motif": motif,
        "alt": raw.get("alt") or headline,
        "voice_ok": raw.get("voice_ok"),
        "variant": variant,
        "subtitle": raw.get("subtitle"),
    }
