# OG Card System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace 280 hand-maintained `site/og-*.html` render sources with one data-driven renderer over a committed manifest, shipping cards as `og-v2.png`.

**Architecture:** A YAML manifest keyed by page path holds card copy. Family is derived from URL path; Editorial motif from a topic rule; both overridable per entry. Five HTML family templates render via pinned Playwright + Chromium using local woff2. Cutover runs in three separable stages so "the new system works" and "the rollback material is gone" are never proven in the same step.

**Tech Stack:** Python 3.12 (stdlib + `pyyaml`), Playwright 1.58.0 / Chromium 145.0.7632.6, HTML/CSS templates, `unittest`, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-21-og-card-system-design.md`

## Global Constraints

- Output is exactly **1200×630 px**, no skew, no letterbox.
- **No source type below 30px** in any family template.
- Colour tokens only, from `docs/site/cta-system.md`: `--bg #0c0c0d`, `--surface #141416`, `--border2 #2e2e34`, `--text #e8e8ec`, `--muted #a8a8b8`, `--quiet #88889a`, `--accent #b5cc7a`, `--teal #8be0c8`, `--action #ea735e`, `--error #ff5c7a`, `--warn #f6b94b`. **No lime `#c8f060`.**
- Identity text is **"Mneme HQ"**, never "Mneme".
- Red (`--error`) appears **only** when a card's `tone` is `failure`. `tone` is explicit in the manifest and never generated.
- Fonts are **local woff2 only** from `site/assets/fonts/`. No Google Fonts `@import`.
- Renderer pins: `playwright==1.58.0`, Chromium `145.0.7632.6`, `device_scale_factor=1`.
- House voice (`PUBLISHING.md:206`): never the word "bottleneck"; no em dashes as connective tissue. Enforced as advisory lint with per-entry escapes, not a blanket character ban.
- Asset versioning (`PUBLISHING.md:105`): changed static assets ship under a **new filename**. Cards are `og-v2.png`. Never overwrite `og.png`.
- Check scripts follow the house pattern: collect `errors`, print `ERROR -- {e}`, print a summary count, `return 1 if errors else 0`, `sys.exit(main())`.
- Test scripts follow the house pattern: `scripts/test_<module>.py`, `unittest`, import the module under test by bare name, run as `python scripts/test_<module>.py`.
- `scripts/sweep_accent_sage.py --check` must pass at every commit.

---

## File Structure

| File | Responsibility |
|---|---|
| `site/og/cards.yaml` | The manifest. One record per page path. Human-edited. |
| `scripts/og_manifest.py` | Load/validate manifest; derive family from path; derive motif from topic; resolve a page to a fully-populated card record. No rendering. |
| `scripts/og_geometry.py` | The eight Editorial motifs as SVG. Pure function of (slug, motif, tone). No I/O. |
| `templates/og/_base.css` | Shared card stylesheet: type scale, tokens, `@font-face`. |
| `templates/og/{brand,proof,integration,editorial,comparison}.html` | One layout per family. |
| `scripts/render_og.py` | Manifest → HTML → PNG via Playwright. `--strict`, `--out`, version-pin assertion, dimension + type-floor assertions. |
| `scripts/seed_og_manifest.py` | One-shot: extract copy from the 280 legacy templates into `cards.yaml`. Deleted in Stage C. |
| `scripts/check_og_coverage.py` | CI gate: strict coverage, reproducibility, `lines`↔`headline` consistency. |
| `scripts/lint_og_voice.py` | CI gate: house voice with escapes. |
| `scripts/sync_og_meta.py` | Repoint `og:image`/`twitter:image` to `og-v2.png` and add the four metadata tags. |
| `scripts/test_*.py` | Unit tests, one per module above. |
| `.github/workflows/og-cards-check.yml` | Runs the three checks. |

**Manifest format note.** YAML is chosen over JSON because the manifest's purpose is human-edited editorial copy across 322 entries, where comments and unquoted multi-word strings matter. Cost: `pyyaml` is used nowhere else in `scripts/`, so the CI workflow needs a `pip install pyyaml` step. That cost is accepted deliberately.

---

## Task 1: Manifest loader — path→family derivation

**Files:**
- Create: `scripts/og_manifest.py`
- Test: `scripts/test_og_manifest.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `family_for_path(rel: str) -> str | None` returning one of `"editorial" | "integration" | "proof" | "comparison" | "brand"` or `None`; `FAMILIES: tuple[str, ...]`.

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Regression tests for the OG manifest loader."""
from __future__ import annotations

import unittest

import og_manifest as m


class TestFamilyForPath(unittest.TestCase):
    def test_editorial_prefixes(self):
        self.assertEqual(m.family_for_path("insights/rag-is-not-memory/"), "editorial")
        self.assertEqual(m.family_for_path("concepts/architectural-drift/"), "editorial")

    def test_integration_prefixes(self):
        self.assertEqual(m.family_for_path("integrations/claude-code/"), "integration")
        self.assertEqual(m.family_for_path("works-with/devin/"), "integration")
        self.assertEqual(m.family_for_path("supported-languages/python-governance/"), "integration")

    def test_proof_prefixes(self):
        self.assertEqual(m.family_for_path("demo/storage-decision/"), "proof")
        self.assertEqual(m.family_for_path("benchmark/"), "proof")
        self.assertEqual(m.family_for_path("architecture/how-retrieval-works/"), "proof")
        self.assertEqual(m.family_for_path("audit/methodology/"), "proof")

    def test_comparison_prefixes(self):
        self.assertEqual(m.family_for_path("compare/coderabbit/"), "comparison")
        self.assertEqual(m.family_for_path("use-cases/design-system-governance/"), "comparison")

    def test_brand_exact_paths(self):
        self.assertEqual(m.family_for_path(""), "brand")
        self.assertEqual(m.family_for_path("about/"), "brand")
        self.assertEqual(m.family_for_path("founder/"), "brand")
        self.assertEqual(m.family_for_path("pilot/"), "brand")

    def test_unresolved_paths_return_none(self):
        """These seven need an explicit family: in the manifest."""
        for rel in ("enterprise/trust/", "for/cto/", "for/platform/",
                    "for/principal-engineer/", "qa-glossary/",
                    "security/data-handling/",
                    "open-source-ai-coding-agent-governance/"):
            self.assertIsNone(m.family_for_path(rel), rel)

    def test_brand_exact_does_not_swallow_children(self):
        """'for/' is brand, but 'for/cto/' is deliberately unresolved."""
        self.assertEqual(m.family_for_path("for/"), "brand")
        self.assertIsNone(m.family_for_path("for/cto/"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python test_og_manifest.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'og_manifest'`

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python test_og_manifest.py -v`
Expected: PASS, 7 tests

- [ ] **Step 5: Commit**

```bash
git add scripts/og_manifest.py scripts/test_og_manifest.py
git commit -m "feat(og): derive card family from URL path"
```

---

## Task 2: Manifest loader — topic→motif rule

**Files:**
- Modify: `scripts/og_manifest.py`
- Modify: `scripts/test_og_manifest.py`

**Interfaces:**
- Consumes: `FAMILIES` from Task 1.
- Produces: `motif_for_slug(slug: str) -> str` returning one of the eight motif names; `MOTIFS: tuple[str, ...]`.

- [ ] **Step 1: Write the failing test**

Append to `scripts/test_og_manifest.py`, above the `if __name__` block:

```python
class TestMotifForSlug(unittest.TestCase):
    def test_topic_signals_select_motif(self):
        cases = {
            "architectural-drift-prevention": "branch",
            "constraint-decay-coding-agents": "branch",
            "software-factory-governance-layer": "stack",
            "emerging-ai-agent-infrastructure-stack": "stack",
            "zero-trust-for-ai-agents": "boundary",
            "migration-guardrails-for-ai-coding-agents": "boundary",
            "coordination-governance-multi-agent-systems": "connected",
            "governance-propagation": "propagation",
            "architecture-cannot-be-a-prompt-context-compaction": "broken",
            "runtime-verification-is-not-architectural-verification": "intersection",
            "why-observability-is-not-governance": "intersection",
        }
        for slug, expected in cases.items():
            self.assertEqual(m.motif_for_slug(slug), expected, slug)

    def test_no_signal_defaults_to_connected(self):
        self.assertEqual(m.motif_for_slug("what-is-the-ai-sdlc"), "connected")

    def test_result_is_always_a_known_motif(self):
        for slug in ("a", "zzz", "", "multi-agent-drift-stack"):
            self.assertIn(m.motif_for_slug(slug), m.MOTIFS)

    def test_is_deterministic(self):
        self.assertEqual(m.motif_for_slug("architectural-drift"),
                         m.motif_for_slug("architectural-drift"))

    def test_earlier_signal_wins_when_several_match(self):
        """drift beats stack, so the rule is order-defined not arbitrary."""
        self.assertEqual(m.motif_for_slug("drift-in-the-platform-stack"), "branch")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python test_og_manifest.py -v`
Expected: FAIL with `AttributeError: module 'og_manifest' has no attribute 'motif_for_slug'`

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/og_manifest.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python test_og_manifest.py -v`
Expected: PASS, 12 tests

- [ ] **Step 5: Commit**

```bash
git add scripts/og_manifest.py scripts/test_og_manifest.py
git commit -m "feat(og): derive Editorial motif from topic signals"
```

---

## Task 3: Manifest loader — record resolution and strict mode

**Files:**
- Modify: `scripts/og_manifest.py`
- Modify: `scripts/test_og_manifest.py`

**Interfaces:**
- Consumes: `family_for_path`, `motif_for_slug`.
- Produces: `load(path: Path) -> dict[str, dict]`; `resolve(rel: str, raw: dict | None, strict: bool = False) -> dict` returning a record with keys `family`, `headline`, `lines` (list[str]), `accent` (str|None), `tone`, `motif`, `alt`, `rows` (list|None); `ManifestError(Exception)`.

- [ ] **Step 1: Write the failing test**

Append to `scripts/test_og_manifest.py`:

```python
class TestResolve(unittest.TestCase):
    def test_fills_family_and_motif_from_derivation(self):
        r = m.resolve("insights/architectural-drift/",
                      {"headline": "Architectural Drift"})
        self.assertEqual(r["family"], "editorial")
        self.assertEqual(r["motif"], "branch")

    def test_explicit_fields_win_over_derivation(self):
        r = m.resolve("insights/architectural-drift/",
                      {"headline": "X", "family": "brand", "motif": "stack"})
        self.assertEqual(r["family"], "brand")
        self.assertEqual(r["motif"], "stack")

    def test_tone_defaults_to_neutral_and_is_never_derived(self):
        r = m.resolve("insights/architectural-drift/", {"headline": "X"})
        self.assertEqual(r["tone"], "neutral")

    def test_tone_failure_is_honoured(self):
        r = m.resolve("insights/x/", {"headline": "X", "tone": "failure"})
        self.assertEqual(r["tone"], "failure")

    def test_invalid_tone_raises(self):
        with self.assertRaises(m.ManifestError):
            m.resolve("insights/x/", {"headline": "X", "tone": "broken"})

    def test_alt_defaults_to_headline(self):
        r = m.resolve("insights/x/", {"headline": "Hello There"})
        self.assertEqual(r["alt"], "Hello There")

    def test_alt_override_is_kept(self):
        r = m.resolve("demo/x/", {"headline": "H", "alt": "A blocked change."})
        self.assertEqual(r["alt"], "A blocked change.")

    def test_lines_absent_yields_single_line(self):
        r = m.resolve("insights/x/", {"headline": "One Two Three"})
        self.assertEqual(r["lines"], ["One Two Three"])

    def test_lines_must_rejoin_to_headline(self):
        good = {"headline": "The Software Factory Needs a Governance Layer",
                "lines": ["The Software Factory Needs a", "Governance Layer"]}
        r = m.resolve("insights/x/", good)
        self.assertEqual(len(r["lines"]), 2)

    def test_lines_that_do_not_rejoin_raise(self):
        bad = {"headline": "The Software Factory Needs a Governance Layer",
               "lines": ["The Software Factory", "Something Else"]}
        with self.assertRaises(m.ManifestError):
            m.resolve("insights/x/", bad)

    def test_strict_mode_rejects_missing_record(self):
        with self.assertRaises(m.ManifestError):
            m.resolve("insights/x/", None, strict=True)

    def test_non_strict_derives_a_bootstrap_record(self):
        r = m.resolve("insights/why-rag-fails/", None, strict=False)
        self.assertEqual(r["family"], "editorial")
        self.assertTrue(r["headline"])

    def test_strict_mode_rejects_unresolvable_family(self):
        with self.assertRaises(m.ManifestError):
            m.resolve("qa-glossary/", {"headline": "X"}, strict=True)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python test_og_manifest.py -v`
Expected: FAIL with `AttributeError: module 'og_manifest' has no attribute 'resolve'`

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/og_manifest.py`:

```python
import re
from pathlib import Path

import yaml

TONES = ("neutral", "failure")


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
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python test_og_manifest.py -v`
Expected: PASS, 25 tests

- [ ] **Step 5: Commit**

```bash
git add scripts/og_manifest.py scripts/test_og_manifest.py
git commit -m "feat(og): resolve manifest records with strict-mode coverage"
```

---

## Task 4: Editorial geometry — eight motifs

**Files:**
- Create: `scripts/og_geometry.py`
- Test: `scripts/test_og_geometry.py`

**Interfaces:**
- Consumes: `MOTIFS` from `og_manifest`.
- Produces: `render(slug: str, motif: str, tone: str = "neutral", size: int = 286) -> str` returning an SVG string.

**Reference implementation:** the reviewed mockup builder in the session scratchpad produced these eight motifs; port its `_node`/`_ring`/`_cross`/`_line` helpers and per-motif branches verbatim, then add the tests below.

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Regression tests for Editorial card geometry."""
from __future__ import annotations

import re
import unittest

import og_geometry as g
import og_manifest as m

SAGE, RED = "#b5cc7a", "#ff5c7a"


class TestGeometry(unittest.TestCase):
    def test_every_motif_renders_svg(self):
        for motif in m.MOTIFS:
            svg = g.render("any-slug", motif)
            self.assertTrue(svg.startswith("<svg"), motif)
            self.assertIn("</svg>", svg)

    def test_unknown_motif_raises(self):
        with self.assertRaises(ValueError):
            g.render("s", "spiral")

    def test_neutral_tone_never_emits_red(self):
        """The single most important rule: a governance-layer card must not
        assert that something was blocked."""
        for motif in m.MOTIFS:
            self.assertNotIn(RED, g.render("slug", motif, tone="neutral"), motif)

    def test_failure_tone_emits_red(self):
        for motif in m.MOTIFS:
            self.assertIn(RED, g.render("slug", motif, tone="failure"), motif)

    def test_sage_present_in_neutral(self):
        for motif in m.MOTIFS:
            self.assertIn(SAGE, g.render("slug", motif, tone="neutral"), motif)

    def test_no_lime_anywhere(self):
        for motif in m.MOTIFS:
            for tone in ("neutral", "failure"):
                self.assertNotIn("#c8f060", g.render("s", motif, tone))

    def test_deterministic_for_same_slug(self):
        self.assertEqual(g.render("abc", "connected"), g.render("abc", "connected"))

    def test_hash_varies_geometry_within_a_motif(self):
        """Cards sharing a motif must still differ."""
        a = g.render("alpha-slug", "connected")
        b = g.render("beta-slug", "connected")
        self.assertNotEqual(a, b)

    def test_declares_its_motif(self):
        self.assertIn('data-motif="stack"', g.render("s", "stack"))

    def test_respects_size(self):
        svg = g.render("s", "connected", size=400)
        self.assertIn('width="400"', svg)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python test_og_geometry.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'og_geometry'`

- [ ] **Step 3: Write the implementation**

Port the mockup's geometry module, adding a motif guard and tone gate. The signature and the two invariants the tests pin are:

```python
#!/usr/bin/env python3
"""The eight Editorial motifs.

Motif is chosen semantically upstream (og_manifest.motif_for_slug); this
module only draws. The slug hash varies geometry *within* the chosen
motif -- node positions, which edges exist, which node is highlighted --
so cards sharing a motif still differ.

Red appears only when tone == "failure". In neutral tone the highlight is
sage alone.
"""
from __future__ import annotations

import hashlib
import math

from og_manifest import MOTIFS

GREY, DIM, SAGE, RED = "#4a4a54", "#34343c", "#b5cc7a", "#ff5c7a"


def render(slug: str, motif: str, tone: str = "neutral", size: int = 286) -> str:
    if motif not in MOTIFS:
        raise ValueError(f"unknown motif {motif!r}; expected one of {MOTIFS}")
    d = hashlib.sha256(slug.encode()).digest()
    fail = tone == "failure"
    mark = RED if fail else SAGE
    parts: list[str] = []
    # ... per-motif branches, ported from the reviewed mockup ...
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
            f'data-motif="{motif}" class="og-geometry">{"".join(parts)}</svg>')
```

Each branch must satisfy: at least one `SAGE` element in every tone, and at
least one `RED` element when and only when `fail`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python test_og_geometry.py -v`
Expected: PASS, 10 tests

- [ ] **Step 5: Commit**

```bash
git add scripts/og_geometry.py scripts/test_og_geometry.py
git commit -m "feat(og): eight semantic Editorial motifs with tone-gated red"
```

---

## Task 5: Family templates and shared stylesheet

**Files:**
- Create: `templates/og/_base.css`
- Create: `templates/og/brand.html`, `proof.html`, `integration.html`, `editorial.html`, `comparison.html`
- Test: `scripts/test_og_templates.py`

**Interfaces:**
- Produces: five templates using `{{placeholder}}` substitution with keys `identity`, `family_label`, `lines_html`, `sup`, `rows_html`, `geometry`, `badge`, `name`, `chain_html`, `box_html`. `_base.css` defines `.frame`, `.body`, `.top`, `.id`, `.fam`, `.rule`, `h1`, `h1 em`, `.sup`.

**Type scale (exact, from the spec):** headline auto-fit 61/70/78/94 by longest-line length (≤38→94, ≤62→78, ≤92→70, else 61); identity 42; category 30; supporting 38; proof/comparison value 44; functional label 30–32. Frame padding `46px 56px 50px`.

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Structural tests for the five OG family templates."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

TPL = Path(__file__).resolve().parent.parent / "templates" / "og"
FAMILIES = ("brand", "proof", "integration", "editorial", "comparison")
LIME = ("#c8f060", "#a8d040", "#a9d342", "200,240,96", "200, 240, 96")


class TestTemplates(unittest.TestCase):
    def test_all_families_exist(self):
        for f in FAMILIES:
            self.assertTrue((TPL / f"{f}.html").is_file(), f)
        self.assertTrue((TPL / "_base.css").is_file())

    def _all_text(self):
        return "\n".join((TPL / n).read_text(encoding="utf-8")
                         for n in [f"{f}.html" for f in FAMILIES] + ["_base.css"])

    def test_no_type_below_30px(self):
        for size in re.findall(r"font-size:\s*(\d+)px", self._all_text()):
            self.assertGreaterEqual(int(size), 30, f"{size}px is below the 30px floor")

    def test_no_lime(self):
        text = self._all_text()
        for token in LIME:
            self.assertNotIn(token, text, token)

    def test_no_google_fonts(self):
        self.assertNotIn("fonts.googleapis.com", self._all_text())

    def test_fonts_are_local_woff2(self):
        css = (TPL / "_base.css").read_text(encoding="utf-8")
        self.assertIn("assets/fonts/", css)
        self.assertIn(".woff2", css)

    def test_identity_is_mneme_hq(self):
        for f in FAMILIES:
            html = (TPL / f"{f}.html").read_text(encoding="utf-8")
            if "Mneme" in html:
                self.assertIn("Mneme HQ", html, f)

    def test_no_printed_url(self):
        self.assertNotIn("mnemehq.com/", self._all_text())

    def test_brand_has_no_category_label(self):
        """Brand cards carry the identity alone."""
        self.assertNotIn("{{family_label}}",
                         (TPL / "brand.html").read_text(encoding="utf-8"))

    def test_editorial_has_geometry_and_no_supporting_copy(self):
        html = (TPL / "editorial.html").read_text(encoding="utf-8")
        self.assertIn("{{geometry}}", html)
        self.assertNotIn("{{sup}}", html)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python test_og_templates.py -v`
Expected: FAIL on `test_all_families_exist`

- [ ] **Step 3: Write the templates**

Port the reviewed v3 mockups. `_base.css` holds the shared shell:

```css
@font-face{font-family:'IS';src:url('../../site/assets/fonts/InstrumentSerif-400.woff2')format('woff2');font-weight:400;font-style:normal}
@font-face{font-family:'IS';src:url('../../site/assets/fonts/InstrumentSerif-400-italic.woff2')format('woff2');font-weight:400;font-style:italic}
@font-face{font-family:'DM';src:url('../../site/assets/fonts/DMMono-500.woff2')format('woff2');font-weight:500}
@font-face{font-family:'IN';src:url('../../site/assets/fonts/Inter-600.woff2')format('woff2');font-weight:600}
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0c0c0d;--surface:#141416;--border:#222226;--border2:#2e2e34;
--text:#e8e8ec;--muted:#a8a8b8;--quiet:#88889a;--accent:#b5cc7a;
--teal:#8be0c8;--action:#ea735e;--error:#ff5c7a;--warn:#f6b94b}
body{width:1200px;height:630px;background:var(--bg);overflow:hidden;position:relative;
font-family:'DM',monospace;-webkit-font-smoothing:antialiased}
.frame{position:absolute;inset:0;padding:46px 56px 50px;display:flex;flex-direction:column;z-index:2}
.body{flex:1;display:flex;flex-direction:column;justify-content:center;min-height:0}
.top{display:flex;align-items:baseline;gap:20px;flex:none}
.id{font-family:'IS',serif;font-size:42px;color:var(--text);letter-spacing:-.5px;line-height:1}
.fam{font-family:'DM',monospace;font-size:30px;font-weight:500;color:var(--quiet);
letter-spacing:.1em;text-transform:uppercase;line-height:1;white-space:nowrap}
.rule{flex:1;height:1px;background:var(--border2);margin-bottom:9px}
h1{font-family:'IS',serif;color:var(--text);letter-spacing:-1.6px;line-height:1.05;font-weight:400}
h1 em{font-style:italic;color:var(--accent)}
.sup{font-family:'IN',sans-serif;font-size:38px;line-height:1.35;color:var(--muted);
font-weight:600;letter-spacing:-.3px}
```

`editorial.html` (the 222-card case) is the shape all five follow:

```html
<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="_base.css"></head>
<body>
{{geometry}}
<div class="frame">
  <div class="top"><span class="id">Mneme HQ</span><span class="fam">{{family_label}}</span><span class="rule"></span></div>
  <div class="body" style="max-width:784px"><h1 style="font-size:{{headline_px}}px">{{lines_html}}</h1></div>
</div>
</body></html>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python test_og_templates.py -v`
Expected: PASS, 9 tests

- [ ] **Step 5: Commit**

```bash
git add templates/og scripts/test_og_templates.py
git commit -m "feat(og): five family templates on a shared 30px-floor scale"
```

---

## Task 6: Renderer with pinned browser and output assertions

**Files:**
- Create: `scripts/render_og.py`
- Test: `scripts/test_render_og.py`
- Modify: `requirements.txt` (create if absent)

**Interfaces:**
- Consumes: `og_manifest.load/resolve`, `og_geometry.render`, `templates/og/*`.
- Produces: `fit(text: str) -> int`; `build_html(record: dict) -> str`; `assert_versions() -> None`; CLI `python scripts/render_og.py [--strict] [--out DIR] [--only PATH]`.

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Regression tests for the OG renderer."""
from __future__ import annotations

import unittest

import render_og as r


class TestFit(unittest.TestCase):
    def test_bands_match_the_spec(self):
        self.assertEqual(r.fit(["short"]), 94)                       # <=38
        self.assertEqual(r.fit(["x" * 38]), 94)
        self.assertEqual(r.fit(["x" * 39]), 78)                      # <=62
        self.assertEqual(r.fit(["x" * 62]), 78)
        self.assertEqual(r.fit(["x" * 63]), 70)                      # <=92
        self.assertEqual(r.fit(["x" * 92]), 70)
        self.assertEqual(r.fit(["x" * 93]), 61)

    def test_sizes_on_longest_line_not_total(self):
        """A deliberate break must not shrink the card."""
        one = r.fit(["The Software Factory Needs a Governance Layer"])
        two = r.fit(["The Software Factory Needs a", "Governance Layer"])
        self.assertGreater(two, one)

    def test_never_below_the_floor(self):
        self.assertGreaterEqual(r.fit(["x" * 500]), 30)


class TestBuildHtml(unittest.TestCase):
    def _rec(self, **kw):
        base = {"path": "insights/x/", "family": "editorial",
                "headline": "Architectural Drift", "lines": ["Architectural Drift"],
                "accent": "Drift", "sup": None, "rows": None,
                "tone": "neutral", "motif": "branch", "alt": "Architectural Drift"}
        base.update(kw)
        return base

    def test_accent_phrase_becomes_italic_em(self):
        html = r.build_html(self._rec())
        self.assertIn("<em>Drift</em>", html)

    def test_lines_become_explicit_breaks(self):
        html = r.build_html(self._rec(
            headline="A B", lines=["A", "B"], accent=None))
        self.assertIn("<br>", html)

    def test_editorial_embeds_geometry(self):
        self.assertIn("data-motif=\"branch\"", r.build_html(self._rec()))

    def test_neutral_editorial_has_no_red(self):
        self.assertNotIn("#ff5c7a", r.build_html(self._rec()))

    def test_html_escapes_copy(self):
        html = r.build_html(self._rec(
            headline="A & B", lines=["A & B"], accent=None))
        self.assertIn("&amp;", html)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python test_render_og.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'render_og'`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""Render OG cards from site/og/cards.yaml.

Rendering is pinned. An unpinned browser makes "deterministic" cards
produce pixel diffs whenever Chromium changes underneath them, which is
how a regenerate-and-diff gate turns into noise.

Usage:
  python scripts/render_og.py --strict --out site
  python scripts/render_og.py --only insights/rag-is-not-memory/
"""
from __future__ import annotations

import argparse
import asyncio
import html as html_mod
import sys
from pathlib import Path

import og_geometry
import og_manifest

REPO = Path(__file__).resolve().parent.parent
TPL = REPO / "templates" / "og"
MANIFEST = REPO / "site" / "og" / "cards.yaml"
CARD_NAME = "og-v2.png"          # PUBLISHING.md:105 -- never overwrite og.png
WIDTH, HEIGHT = 1200, 630
PLAYWRIGHT_PIN = "1.58.0"
CHROMIUM_PIN = "145.0.7632.6"
TYPE_FLOOR = 30

FAMILY_LABEL = {"editorial": None, "integration": "Integration",
                "comparison": "Comparison", "proof": "Demo", "brand": None}


def fit(lines: list[str]) -> int:
    """Size on the LONGEST LINE so a deliberate break never shrinks the card."""
    n = max((len(x) for x in lines), default=0)
    return 94 if n <= 38 else 78 if n <= 62 else 70 if n <= 92 else 61


def _lines_html(lines: list[str], accent: str | None) -> str:
    esc = [html_mod.escape(x) for x in lines]
    out = "<br>".join(esc)
    if accent:
        a = html_mod.escape(accent)
        out = out.replace(a, f"<em>{a}</em>", 1)
    return out


def build_html(record: dict) -> str:
    tpl = (TPL / f"{record['family']}.html").read_text(encoding="utf-8")
    geometry = ""
    if record["family"] == "editorial":
        geometry = og_geometry.render(
            record["path"].rstrip("/").rsplit("/", 1)[-1],
            record["motif"], record["tone"])
    label = FAMILY_LABEL.get(record["family"]) or ""
    return (tpl
            .replace("{{geometry}}", geometry)
            .replace("{{family_label}}", html_mod.escape(label))
            .replace("{{headline_px}}", str(fit(record["lines"])))
            .replace("{{lines_html}}", _lines_html(record["lines"], record["accent"]))
            .replace("{{sup}}", html_mod.escape(record.get("sup") or "")))


def assert_versions() -> None:
    """Fail before rendering rather than emitting subtly different cards."""
    import importlib.metadata as md
    got = md.version("playwright")
    if got != PLAYWRIGHT_PIN:
        raise SystemExit(f"ERROR -- playwright {got}, pinned {PLAYWRIGHT_PIN}")
```

Add the async render loop: start a `SimpleHTTPRequestHandler` rooted at the
repo so `_base.css` and `site/assets/fonts/*.woff2` resolve, assert
`browser.version == CHROMIUM_PIN`, screenshot each card with
`clip={"x":0,"y":0,"width":WIDTH,"height":HEIGHT}` and
`device_scale_factor=1`, then assert every written PNG is exactly
1200×630 via `PIL.Image.open(p).size`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python test_render_og.py -v`
Expected: PASS, 8 tests

- [ ] **Step 5: Pin the dependency and commit**

```bash
printf 'playwright==1.58.0\npyyaml==6.0.1\npillow>=11.0\n' >> requirements.txt
git add scripts/render_og.py scripts/test_render_og.py requirements.txt
git commit -m "feat(og): pinned renderer with dimension and type-floor gates"
```

---

## Task 7: Seed the manifest from the legacy templates

**Files:**
- Create: `scripts/seed_og_manifest.py` (one-shot; deleted in Task 13)
- Create: `site/og/cards.yaml`

**Interfaces:**
- Consumes: `og_manifest.family_for_path`.
- Produces: `site/og/cards.yaml` with one record per page (322 expected).

- [ ] **Step 1: Write the seeder**

Extract `.heading`, `.tag` and `.subtitle` from each `site/og-*.html`, map
each template to its page via the existing `TEMPLATE_MAP` in
`scripts/generate_og_images.py`, and emit YAML keyed by page path. Carry
`headline` from `.heading` and, for non-Editorial families only, `sup` from
`.subtitle`. Do **not** carry `.tag` — family comes from the path.

- [ ] **Step 2: Run it and inspect**

```bash
python scripts/seed_og_manifest.py
python - <<'PY'
import yaml
d = yaml.safe_load(open('site/og/cards.yaml', encoding='utf-8'))
print(len(d), 'records')
PY
```
Expected: ~280 records seeded; the gap to 322 is pages that never had a template.

- [ ] **Step 3: Hand-complete the manifest**

Three edits no script should guess:

1. **Seven explicit `family:` overrides** — `enterprise/trust/`, `for/cto/`,
   `for/platform/`, `for/principal-engineer/`, `qa-glossary/`,
   `security/data-handling/`, `open-source-ai-coding-agent-governance/`.
2. **Four over-long headlines rewritten** to ≤10 words —
   `insights/mckinsey-agentic-software-delivery-governance/` (15w),
   `insights/future-of-software-engineering-after-vibe-coding/` (13w),
   `insights/zero-trust-for-ai-agents-architectural-governance/` (12w),
   `insights/github-ai-agent-validation-trust-layer/` (11w).
3. **Records for every page the seeder missed**, until strict mode passes.

Assign `tone: failure` only to drift/denial/violation topics. Add `lines:`
where a deliberate break reads better. Add `alt:` on every Proof,
Integration and Comparison card.

- [ ] **Step 4: Verify strict resolution**

```bash
python scripts/render_og.py --strict --out /tmp/og-dryrun --dry-run
```
Expected: 322 records resolve, zero `ManifestError`.

- [ ] **Step 5: Commit**

```bash
git add site/og/cards.yaml scripts/seed_og_manifest.py
git commit -m "feat(og): seed the card manifest from the legacy templates"
```

---

## Task 8: Coverage check

**Files:**
- Create: `scripts/check_og_coverage.py`
- Test: `scripts/test_check_og_coverage.py`

**Interfaces:**
- Consumes: `og_manifest`.
- Produces: `main() -> int`; helpers `pages() -> list[str]`, `advertised() -> dict[str, str]`.

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Regression tests for the OG coverage gate."""
from __future__ import annotations

import unittest

import check_og_coverage as c
import og_manifest as m


class TestCoverage(unittest.TestCase):
    def test_flags_page_without_record(self):
        errs = c.audit(pages=["insights/a/"], manifest={}, advertised={})
        self.assertTrue(any("no manifest record" in e for e in errs))

    def test_flags_record_without_page(self):
        errs = c.audit(pages=[], manifest={"insights/ghost/": {"headline": "X"}},
                       advertised={})
        self.assertTrue(any("ghost" in e for e in errs))

    def test_flags_lines_headline_mismatch(self):
        errs = c.audit(
            pages=["insights/a/"],
            manifest={"insights/a/": {"headline": "A B C", "lines": ["A", "Z"]}},
            advertised={})
        self.assertTrue(any("rejoin" in e for e in errs))

    def test_flags_advertised_image_with_no_source(self):
        errs = c.audit(pages=["insights/a/"],
                       manifest={"insights/a/": {"headline": "X"}},
                       advertised={"insights/a/": "legacy/og.png"})
        self.assertTrue(any("not reproducible" in e for e in errs))

    def test_clean_manifest_passes(self):
        errs = c.audit(pages=["insights/a/"],
                       manifest={"insights/a/": {"headline": "X"}},
                       advertised={"insights/a/": "insights/a/og-v2.png"})
        self.assertEqual(errs, [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python test_check_og_coverage.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

`audit(pages, manifest, advertised) -> list[str]` returns errors for: a page
with no record; a record with no page; `lines` that do not rejoin (catch
`ManifestError` from `og_manifest.resolve(..., strict=True)`); an advertised
`og:image` that is not `<path>/og-v2.png`. `main()` gathers real inputs,
prints `ERROR -- {e}` per error plus a summary, returns 1 on any error.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python test_check_og_coverage.py -v`
Expected: PASS, 5 tests

- [ ] **Step 5: Commit**

```bash
git add scripts/check_og_coverage.py scripts/test_check_og_coverage.py
git commit -m "feat(og): strict coverage and reproducibility gate"
```

---

## Task 9: Voice lint with escapes

**Files:**
- Create: `scripts/lint_og_voice.py`
- Test: `scripts/test_lint_og_voice.py`

**Interfaces:**
- Produces: `findings(record: dict) -> list[str]`; `main() -> int`.

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Regression tests for the OG house-voice lint."""
from __future__ import annotations

import unittest

import lint_og_voice as v


class TestVoice(unittest.TestCase):
    def test_flags_bottleneck(self):
        f = v.findings({"headline": "The review bottleneck", "voice_ok": None})
        self.assertTrue(any("bottleneck" in x for x in f))

    def test_flags_connective_em_dash(self):
        f = v.findings({"headline": "Enforced early — before the commit",
                        "voice_ok": None})
        self.assertTrue(any("em dash" in x for x in f))

    def test_escape_suppresses_a_finding(self):
        """A quoted external report title may legitimately contain the word."""
        f = v.findings({"headline": 'On "The Bottleneck Myth" report',
                        "voice_ok": ["quoted external title"]})
        self.assertEqual(f, [])

    def test_clean_copy_passes(self):
        self.assertEqual(v.findings({"headline": "Architectural Drift",
                                     "voice_ok": None}), [])

    def test_checks_alt_and_sup_too(self):
        f = v.findings({"headline": "Fine", "sup": "A bottleneck appears",
                        "voice_ok": None})
        self.assertTrue(f)

    def test_en_dash_and_hyphen_are_not_flagged(self):
        self.assertEqual(v.findings({"headline": "Multi-agent 2024–2026 work",
                                     "voice_ok": None}), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python test_lint_og_voice.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

Scan `headline`, `sup`, `alt` and each `rows` value for `bottleneck`
(case-insensitive, word boundary) and `—` (U+2014 only — **not** `–` U+2013
or `-`). A truthy `voice_ok` on the record suppresses that record's
findings. `main()` prints `ERROR -- {e}` and returns 1 on unescaped
findings.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python test_lint_og_voice.py -v`
Expected: PASS, 6 tests

- [ ] **Step 5: Commit**

```bash
git add scripts/lint_og_voice.py scripts/test_lint_og_voice.py
git commit -m "feat(og): house-voice lint with per-entry escapes"
```

---

## Task 10: CI workflow

**Files:**
- Create: `.github/workflows/og-cards-check.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: check og cards

# Gates the data-driven OG card system: strict manifest coverage, card
# reproducibility, and house voice. Does NOT render (Chromium in CI is a
# separate concern); rendering determinism is pinned in render_og.py.
#
# Validators: scripts/check_og_coverage.py, scripts/lint_og_voice.py

on:
  pull_request:
    branches: [main]
    paths:
      - 'site/og/**'
      - 'site/**/index.html'
      - 'templates/og/**'
      - 'scripts/**'
  push:
    branches: [main]
    paths:
      - 'site/og/**'
      - 'templates/og/**'
      - 'scripts/**'

permissions:
  contents: read

jobs:
  og-cards:
    name: og card manifest
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install manifest dependency
        run: pip install pyyaml==6.0.1

      - name: Unit tests
        run: |
          cd scripts
          python test_og_manifest.py
          python test_og_geometry.py
          python test_og_templates.py
          python test_render_og.py
          python test_check_og_coverage.py
          python test_lint_og_voice.py

      - name: Coverage gate
        run: python scripts/check_og_coverage.py

      - name: House-voice lint
        run: python scripts/lint_og_voice.py
```

- [ ] **Step 2: Verify locally**

```bash
cd scripts && for t in test_og_manifest test_og_geometry test_og_templates \
  test_render_og test_check_og_coverage test_lint_og_voice; do python $t.py -q || exit 1; done
cd .. && python scripts/check_og_coverage.py && python scripts/lint_og_voice.py
```
Expected: all pass, both checks exit 0.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/og-cards-check.yml
git commit -m "ci(og): gate manifest coverage and house voice"
```

---

## Task 11: Stage A acceptance — render to staging and QA

**Files:**
- Create: `site/og-staging/**` (not committed; `.gitignore` entry)

- [ ] **Step 1: Render everything to staging**

```bash
python scripts/render_og.py --strict --out site/og-staging
```
Expected: 322 cards, zero failures, every output 1200×630.

- [ ] **Step 2: Prove the 22 unreproducible cards are now covered**

This is a named acceptance list, not a spot check:

```bash
python - <<'PY'
from pathlib import Path
NAMED = [
 "for/cto/","for/platform/","for/principal-engineer/",
 "insights/agent-formation-engineering-performance-metrics/",
 "insights/agentic-resource-discovery-agent-governance/",
 "insights/agentic-workforce-visibility-crisis/",
 "insights/ai-agent-orchestration-is-not-governance/",
 "insights/ai-makes-software-more-ambitious/",
 "insights/bcg-four-pillars-agentic-ai-need-architectural-intent/",
 "insights/block-builderbot-coordination-governance/",
 "insights/enforce-engineering-standards-across-ai-assisted-teams/",
 "insights/memory-is-not-governance/","insights/mneme-vs-cursor-rules/",
 "insights/sovereign-ai-needs-sovereign-engineering/",
 "insights/stanford-ai-index-2026-engineering-governance/",
 "insights/using-ibm-bob-with-architectural-guardrails/",
 "insights/verification-starts-before-generation/",
 "insights/when-ai-agents-degrade-architectural-intent-should-not/",
 "insights/why-architectural-governance-needs-precedence-semantics/",
 "insights/why-code-review-cannot-scale-with-ai-output/",
 "insights/why-rag-fails-for-architectural-governance/", "",
]
missing=[p for p in NAMED if not (Path("site/og-staging")/p/"og-v2.png").is_file()]
print("MISSING:",missing) if missing else print("all 22 reproducible")
raise SystemExit(1 if missing else 0)
PY
```
Expected: `all 22 reproducible`, exit 0. **If any are missing, stop.**

- [ ] **Step 3: Build the QA contact sheet**

Render each card at 1200 / 552 / 360px into one HTML page: all five
families, every Brand and Proof card, each of the eight motifs at short /
medium / long headline, and every `tone: failure` card.

- [ ] **Step 4: Human visual QA gate**

Review the contact sheet. **Do not proceed to Stage B without sign-off.**
Acceptance: readable at 360px; no red on a `neutral` card; identity legible
on every card.

- [ ] **Step 5: Commit the gitignore and QA tooling only**

```bash
echo 'site/og-staging/' >> .gitignore
git add .gitignore scripts/og_contact_sheet.py
git commit -m "chore(og): stage A acceptance tooling"
```

---

## Task 12: Stage B — switch references to og-v2.png

**Files:**
- Create: `scripts/sync_og_meta.py`
- Test: `scripts/test_sync_og_meta.py`
- Modify: all `site/**/index.html`

**Interfaces:**
- Produces: `rewrite(html: str, rel: str, alt: str) -> str`.

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Regression tests for the OG metadata sync."""
from __future__ import annotations

import unittest

import sync_og_meta as s

HEAD = ('<head>\n'
        '<meta property="og:image" content="https://mnemehq.com/insights/a/og.png" />\n'
        '<meta name="twitter:image" content="https://mnemehq.com/insights/a/og.png" />\n'
        '</head>')


class TestRewrite(unittest.TestCase):
    def test_repoints_to_og_v2(self):
        out = s.rewrite(HEAD, "insights/a/", "Alt text")
        self.assertIn("https://mnemehq.com/insights/a/og-v2.png", out)
        self.assertNotIn("/og.png", out)

    def test_adds_all_four_tags(self):
        out = s.rewrite(HEAD, "insights/a/", "Alt text")
        for tag in ('og:image:width" content="1200',
                    'og:image:height" content="630',
                    'og:image:alt" content="Alt text',
                    'twitter:image:alt" content="Alt text'):
            self.assertIn(tag, out)

    def test_is_idempotent(self):
        once = s.rewrite(HEAD, "insights/a/", "Alt text")
        twice = s.rewrite(once, "insights/a/", "Alt text")
        self.assertEqual(once, twice)

    def test_escapes_alt_text(self):
        out = s.rewrite(HEAD, "insights/a/", 'He said "no" & left')
        self.assertIn("&quot;", out)
        self.assertNotIn('content="He said "no"', out)

    def test_leaves_other_markup_untouched(self):
        src = HEAD.replace("</head>", '<title>Keep me</title>\n</head>')
        self.assertIn("<title>Keep me</title>", s.rewrite(src, "insights/a/", "A"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd scripts && python test_sync_og_meta.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write the implementation**

Rewrite `og:image` / `twitter:image` to `https://mnemehq.com/<rel>og-v2.png`
and insert the four tags after `og:image`, replacing any that already exist
so the pass is idempotent. Read and write with `newline=""` so
`check_line_endings.py` stays green.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd scripts && python test_sync_og_meta.py -v`
Expected: PASS, 5 tests

- [ ] **Step 5: Render to real paths, sync, verify**

```bash
python scripts/render_og.py --strict --out site
python scripts/sync_og_meta.py
python scripts/check_og_coverage.py
python scripts/check_line_endings.py
python scripts/check_encoding.py
python scripts/sweep_accent_sage.py --check
```
Expected: all exit 0.

- [ ] **Step 6: Commit**

```bash
git add scripts/sync_og_meta.py scripts/test_sync_og_meta.py site
git commit -m "feat(og): ship cards as og-v2.png with full image metadata"
```

- [ ] **Step 7: Deploy and verify live — HUMAN GATE**

Deploy, then confirm a sample of live `og-v2.png` URLs return 200 and the
homepage card renders in the LinkedIn Post Inspector. **Stage C does not
begin until Stage B is confirmed live.** Rollback at this point is a single
revert; the legacy pipeline is still fully present.

---

## Task 13: Stage C — cleanup, only after Stage B is live

**Files:**
- Delete: `site/og-*.html` (280), `scripts/generate_og_images.py`,
  `scripts/ensure_og_coverage.py`, `scripts/seed_og_manifest.py`,
  `site/assets/og/*.jpg` (46), superseded `site/**/og.png`, `site/og-home-v2.png`
- Modify: `PUBLISHING.md`, `docs/site/cta-system.md`

- [ ] **Step 1: Confirm nothing references what you are about to delete**

```bash
grep -rn "og-home-v2\|assets/og/" site --include='*.html' | grep -v og-v2 | head
grep -rln '/og\.png' site --include='*.html' | head
```
Expected: no output. **If anything appears, stop and fix Stage B first.**

- [ ] **Step 2: Delete the legacy pipeline**

```bash
git rm -q site/og-*.html
git rm -q scripts/generate_og_images.py scripts/ensure_og_coverage.py scripts/seed_og_manifest.py
git rm -q site/assets/og/*.jpg site/og-home-v2.png
find site -name 'og.png' -delete && git add -A site
```

- [ ] **Step 3: Update the governance docs**

In `PUBLISHING.md` §OG images: replace the `og-<slug>.html` +
`ensure_og_coverage.py` process with the manifest workflow; replace the
design table's lime `#c8f060` and "italic accent word in `#c8f060`" with
sage `#b5cc7a`; state the `og-v2.png` filename and the four metadata tags.
In `docs/site/cta-system.md` §8, replace "OG images: any new page still
follows the AGENTS.md og-template pipeline — unaffected", which is now
false.

- [ ] **Step 4: Full check sweep**

```bash
python scripts/check_og_coverage.py
python scripts/lint_og_voice.py
python scripts/sweep_accent_sage.py --check
python scripts/check_line_endings.py
python scripts/check_encoding.py
python scripts/seo_check.py
```
Expected: all exit 0.

- [ ] **Step 5: Commit**

```bash
git commit -m "chore(og): retire the legacy og-template pipeline"
```

---

## Task 14: Sage sweep for the image generators

**Files:**
- Modify: `scripts/gen_benchmark_visual.py:28`, `scripts/gen_benchmark_square.py:~27`,
  `scripts/gen_architecture_visual.py:23`, `scripts/verify_pr{1,2,3,4}.py`

Independent of Tasks 1–13; can run at any point.

- [ ] **Step 1: Move the three generators to sage**

Replace `ACCENT = (200, 240, 96)` with `ACCENT = (181, 204, 122)  # sage #b5cc7a`
in all three. In `gen_benchmark_visual.py` and `gen_benchmark_square.py` also
replace `ACCENT_DIM = (40, 62, 16)` with `(44, 54, 28)`.

- [ ] **Step 2: Regenerate and eyeball the outputs**

```bash
python scripts/gen_benchmark_visual.py
python scripts/gen_benchmark_square.py
python scripts/gen_architecture_visual.py
```
Expected: three PNGs rewritten. Confirm no lime remains visually.

- [ ] **Step 3: Fix the verify scripts**

`verify_pr1.py:57`, `verify_pr2.py:40,79`, `verify_pr3.py:115`,
`verify_pr4.py:50` assert `backgroundColor === 'rgb(200, 240, 96)'`. After
the sage sweep these match nothing and report success by vacuity. Either
update to `rgb(181, 204, 122)` or delete the script if its PR has landed.

- [ ] **Step 4: Confirm the palette gate**

```bash
python scripts/sweep_accent_sage.py --check
grep -rn "200, *240, *96\|c8f060" scripts/ || echo "no lime in scripts/"
```
Expected: `clean: palette and CTA colour roles are in contract`; no lime.

- [ ] **Step 5: Commit**

```bash
git add scripts site
git commit -m "site: retire lime in the image generators and verify scripts"
```

---

## Self-Review

**Spec coverage.** §2.1 governing constraint → Global Constraints + Task 5.
§2.2 type scale → Tasks 5, 6. §2.3 path families → Tasks 1, 7. §2.4 motif
rule + tone → Tasks 2, 4. §2.5 colour → Global Constraints, Tasks 4, 5, 14.
§3.1 manifest → Tasks 3, 7. §3.2 scripts → Tasks 6, 8, 9, 12. §3.3
determinism pins → Task 6. §3.4 generators → Task 14. §4 `og-v2.png` →
Tasks 6, 12. §5.1/5.2/5.3 three stages → Tasks 11, 12, 13. §6 verification →
Tasks 8, 9, 10, 12, 13.

**Type consistency.** `family_for_path` returns `str | None` (Task 1) and
Task 3 handles the `None`. `motif_for_slug` returns a member of `MOTIFS`
(Task 2), which `og_geometry.render` validates (Task 4). `resolve` emits
the record keys that `build_html` reads (Tasks 3, 6). `CARD_NAME =
"og-v2.png"` (Task 6) matches what Tasks 8 and 12 assert.

**Known gap, deliberate.** Task 7 Step 3 is human editorial work — seven
family overrides, four headline rewrites, `tone` assignment, `alt` on
non-Editorial cards. It cannot be specified as code because it is judgement,
so it is specified as an exhaustive checklist with strict mode as the gate.
