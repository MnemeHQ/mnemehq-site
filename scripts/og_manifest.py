#!/usr/bin/env python3
"""Load and resolve the OG card manifest.

Family comes from the URL path, never from the legacy .tag values: those
are the drift this system exists to end (30 distinct values, many of them
singletons invented for a single card).
"""
from __future__ import annotations

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
