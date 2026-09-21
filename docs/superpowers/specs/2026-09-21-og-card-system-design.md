# OG card system — five families, one data-driven renderer

Date: 2026-09-21
Status: approved design, not yet implemented
Supersedes in practice: the `og-<slug>.html` pipeline described in `PUBLISHING.md` §OG images (source ADR-007, superseded by ADR-016)

---

## 1. Why

A GTM audit of the social cards found they read as "technical documentation"
rather than as Mneme HQ, and that they are illegible at the size people
actually see them. Investigation of the repo confirmed the diagnosis and
turned up four drift problems the audit did not name.

### Verified state

| Fact | Measured |
|---|---|
| Render sources | 280 `site/og-*.html` |
| `TEMPLATE_MAP` entries | 283 lines, 280 unique keys, 279 unique outputs |
| Committed `og.png` | 300 — of which **22 are produced by no generator** |
| Those 22 | **all 22 are advertised by a live page**; none is safe to delete |
| Committed `site/assets/og/*.jpg` | 46 — **referenced by zero pages**, written by no script |
| Homepage card | `og-home-v2.png`, a static file **outside `TEMPLATE_MAP`**; the `og-homepage.html` → `site/og.png` pair the generator maintains is unused by `site/index.html` |
| Pages | 322 `index.html`, **all** carry `og:image` |
| `og:image:width` / `:height` / `:alt` / `twitter:image:alt` | **0 of 322** |
| Category tags | 30 distinct values, including `Concept` (33) vs `Concepts` (3) and `Docs · 0.9.0` (2) vs `Docs` (1) |

### The legibility problem, precisely

The generic template renders an 11px tag, 12px URL, 15px subtitle and a
median 42px heading into a 1200×630 image. LinkedIn's desktop feed shows
that file at ~552px and a phone at ~360px — a 0.30 scale. So the 11px tag
arrives at **3.3px** and the subtitle at **4.5px**. They are texture, not
information.

### What the audit got wrong

The audit proposed shortening editorial headlines across the set as days of
work. Measured: of 274 templates carrying a heading, **259 are already ≤8
words** and only 4 exceed 10. The copy is not the problem — the type size
is. That work moves into the renderer and largely disappears.

### Non-goals

- `audit/frontend/src/styles.css` (~30 `rgba(200,240,96,…)` lime declarations)
  and its build output `site/audit/workspace/`. Tracked separately.
- Re-authoring page content. Only card headlines are authored here.
- Any change to which URL a page advertises as its `og:image`, except the
  homepage, which is corrected to join the system.

---

## 2. Design

### 2.1 The governing constraint

**It is one 1200×630 image.** LinkedIn and mobile scale that same file down;
there is no separate mobile asset. Legibility is therefore bought by
**cutting copy, not by inflating type**. A card that needs more words needs
fewer words.

Acceptance surface is **360px**. A card that fails at 360px fails.

### 2.2 Type scale

Source sizes at 1200×630, with rendered size at the two review widths.

| Element | Legacy | **New** | @552px | @360px |
|---|---|---|---|---|
| Headline (auto-fit) | 42 | **61–94** | 28–43 | 18.3–28.2 |
| Identity "Mneme HQ" | 26 | **42** | 19.3 | 12.6 |
| Category label | 11 | **30** | 13.8 | 9.0 |
| Supporting sentence | 15 | **38** | 17.5 | 11.4 |
| Proof / comparison value | — | **44** | 20.2 | 13.2 |
| Functional label | 11 | **30–32** | 13.8–14.7 | 9.0–9.6 |
| Printed URL | 12 | **removed** | — | — |

**Floor: nothing renders below 30px source.** The URL is removed outright —
the social platform already shows the domain, so it was spending the card's
most legible real estate on redundancy.

Headline auto-fit, sized on the **longest line** so a deliberate break does
not shrink the card:

| Longest line | Size |
|---|---|
| ≤38 chars | 94px |
| ≤62 chars | 78px |
| ≤92 chars | 70px |
| else | 61px |

The regular serif stays at editorial weight, not display weight. **The
italic sage phrase is the brand device and is preserved exactly.**

### 2.3 The five families

Counts are measured from the existing `.tag` values across the 280 templates.

| Family | Cards | Composition |
|---|---|---|
| **Editorial** | 189 | Headline, identity, one geometry motif. Nothing else. |
| **Integration** | 25 | Verified-status pill, large platform name, one relationship object (`DECISION → MNEME → <TOOL>`), one short line. |
| **Comparison** | 21 | Proposition headline + two boxes carrying label / one word / verdict. Almost no prose. |
| **Proof** | 9 | Three rows and nothing else: decision → proposed change → verdict. No headline competing with the sequence. |
| **Brand** | 5 | Photograph + large proposition + one short line. Identity alone, no category label. |
| *unassigned* | 31 | Tags too idiosyncratic to map mechanically — see below. |

The 30 drifted tag values collapse as follows:

- **Editorial** ← Insights, Concept, Concepts, Industry Analysis, Worldview,
  Category Education, Framework, AI-Assisted Migrations
- **Comparison** ← Compare, Use case, and the per-use-case one-offs
- **Integration** ← Integration, Works With, Languages
- **Proof** ← Demo Scenario (PASS/WARN/FAIL), Interactive Demo, Benchmark,
  Architecture, Methodology
- **Brand** ← About, Get in touch, Enterprise, founder, pilot

**31 templates carry tags that cannot be mapped by rule** and need explicit
`family:` entries — among them `analysis`, `guide`, `report analysis`,
`security analysis`, `category distinction`, `agentic development`,
`architectural intent enforcement`, `for ctos`, `platform engineering`,
`principal engineers`, `docs · 0.9.0`, and 6 templates with no tag at all.
These are the clearest evidence of the taxonomy drift the manifest exists to
end: each was invented once, for one card, and never reused.

### 2.4 Editorial geometry

~180 hand-drawn metaphors is not feasible and 180 identical ones is the
current problem. Instead: **eight semantic primitives, selected
deterministically from the slug hash**, so every card differs, reproducibly,
at zero per-card cost.

`connected` · `broken` · `boundary` · `branch` · `stack` · `intersection` ·
`propagation` · `isolated`

Two fields govern meaning:

- `motif` — optional explicit choice; otherwise `sha256(slug)` picks one.
- `tone` — `neutral` (default) or `failure`.

**Red appears only when `tone: failure`.** A card about drift, denial or
violation earns the red marker; a card about a governance layer does not. In
`neutral` tone the highlight is sage alone. This was the single largest
correction during design review: an unconditional pass/fail motif asserts
"something was blocked" on every insight, which is false for most of them.

### 2.5 Colour

Inherits the contract in `docs/site/cta-system.md` unchanged:

| Token | Hex | Use on cards |
|---|---|---|
| `--accent` sage | `#b5cc7a` | Held decisions, shipped status, the italic phrase |
| `--error` | `#ff5c7a` | Blocked verdicts — `tone: failure` only |
| `--warn` | `#f6b94b` | Advisory / partial states on comparison cards |
| `--quiet` | `#88889a` | Category labels |
| `--text` / `--muted` | `#e8e8ec` / `#a8a8b8` | Headline / supporting |

No lime. `scripts/sweep_accent_sage.py --check` must continue to pass; it
excludes `og-*.html` today, and after cutover those files no longer exist.

---

## 3. Architecture

### 3.1 `site/og/cards.yaml` — the manifest

One entry per page path. This is the drift fix: card content becomes one
reviewable file instead of 280 hand-edited HTML documents.

```yaml
insights/software-factory-governance-layer:
  family: editorial
  headline: The Software Factory Needs a|Governance Layer
  accent: Governance Layer        # the italic sage phrase
  motif: stack                    # optional; slug hash picks one if absent
  tone: neutral                   # neutral | failure
  # alt: omitted -> falls back to headline

demo/storage-decision:
  family: proof
  rows:
    - [ADR-014, Postgres is the record., held]
    - [AGENT, Add MongoDB., neutral]
    - [BLOCKED, Before the commit., denied]
  alt: Mneme blocks an agent change that violates an architectural decision.
```

Field notes:

- `|` in `headline` marks a **deliberate line break**. A headline card's line
  break is a typographic decision, so it lives in the data rather than being
  left to the wrapping engine.
- `alt` is optional and **defaults to `headline`**. Proof, integration and
  comparison cards override it, because their meaning is in the proof object
  rather than the words above it.
- Missing entry → the renderer derives `headline` from the page's `<title>`
  and `family` from its URL path, and the coverage check reports it.

### 3.2 Scripts

| Script | Responsibility |
|---|---|
| `scripts/render_og.py` | Loads the manifest, dispatches to one of five family templates, renders via Playwright using **local woff2** (drops the Google Fonts `@import` all 280 templates carry), writes PNGs. |
| `scripts/check_og_coverage.py` | CI gate. Every page has a card; every card has a page; no orphaned outputs; no card whose generator no longer exists. |
| `scripts/check_og_voice.py` | CI gate on manifest copy: rejects "bottleneck" and em dashes used as connective tissue, per `PUBLISHING.md:206`. |
| `scripts/sync_og_meta.py` | Writes `og:image:width` (1200), `og:image:height` (630), `og:image:alt`, `twitter:image:alt` into all 322 pages. |

The five family templates live in `templates/og/` as HTML with a shared
stylesheet, so layout stays CSS rather than hand-computed pixel maths.

**House-voice gate rationale.** Headlines previously lived in 280 HTML files
that no check inspected. Moving them into one manifest makes them checkable
for the first time — and during design review two of the mockup headlines
violated house voice ("bottleneck"; an em dash as connective tissue). Without
the gate, the manifest simply becomes a faster way to ship the same errors.

### 3.3 Generators in scope

`gen_benchmark_visual.py`, `gen_benchmark_square.py` and
`gen_architecture_visual.py` carry `ACCENT = (200, 240, 96)` and move to
sage `(181, 204, 122)`; their outputs are regenerated.

`verify_pr1.py` … `verify_pr4.py` assert on computed
`backgroundColor === 'rgb(200, 240, 96)'`. After the sage sweep these
assertions match nothing and would report success-by-vacuity. They are
updated to the current token or retired with the PRs they verified.

---

## 4. Cutover

Build alongside; delete only after parity and QA pass.

1. **Renderer lands dark.** `render_og.py` writes to `site/og-staging/`.
   Nothing the site serves changes. Legacy pipeline still runs.
2. **Manifest seeded from the existing templates.** The 280 `.heading`,
   `.tag` and `.subtitle` values are extracted mechanically — they are
   already curated copy — then the 4 headlines over 10 words are rewritten
   and family/tone/motif assigned.
3. **Coverage parity.** `check_og_coverage.py` must show every one of the 322
   pages resolving to a card, with no orphans, before anything is swapped.
4. **Visual QA** at 552px and 360px across a sample spanning all five
   families, plus every Brand and Proof card (small N, high value).
5. **Swap.** `render_og.py` writes to the real paths. `og-home-v2.png` is
   replaced by a Brand-family card at `site/og.png` and `site/index.html`
   updated to point at it, bringing the homepage inside the system.
6. **Delete**, in one commit: 280 `site/og-*.html`, `generate_og_images.py`
   and its `TEMPLATE_MAP`, `ensure_og_coverage.py`, and the 46 dead
   `site/assets/og/*.jpg`.

   **The 22 unreproducible `og.png` are not deleted.** Every one of them is
   advertised by a live page, so they are live cards that no generator can
   rebuild — the worst category in the inventory, and invisible until you
   cross-reference outputs against `TEMPLATE_MAP`. Each gets a manifest entry
   in step 2 like any other card, at which point the new renderer reproduces
   it and the stale binary is overwritten rather than removed. Their 21
   insight pages plus `/for/cto/`, `/for/platform/`,
   `/for/principal-engineer/` and the site-root `og.png` are the acceptance
   list for step 3: if any of them still lacks a reproducible source, the
   cutover does not proceed.
7. **Metadata sweep** across 322 pages.
8. **Docs.** `PUBLISHING.md` §OG images is rewritten: its design table still
   specifies lime `#c8f060` and an "italic accent word in `#c8f060`", and its
   `[OP]` process still describes `og-<slug>.html` + `ensure_og_coverage.py`.
   `docs/site/cta-system.md` §8's line "OG images: any new page still follows
   the AGENTS.md og-template pipeline — unaffected" becomes false and is
   updated.

Rollback: steps 1–4 change nothing served. After step 5, reverting the commit
restores the legacy pipeline, since deletion is deliberately held to step 6.

---

## 5. Verification

| Check | Gate |
|---|---|
| Every page resolves to a card, no orphans | `check_og_coverage.py`, CI |
| No "bottleneck", no connective em dash in manifest copy | `check_og_voice.py`, CI |
| No source type below 30px in any family template | assertion in `render_og.py` tests |
| All outputs exactly 1200×630 | assertion after render |
| Palette contract intact | `sweep_accent_sage.py --check` |
| 360px legibility | manual QA at cutover; contact sheet at 1200/552/360 |
| Line endings / encoding unchanged | existing `check_line_endings.py`, `check_encoding.py` |

A regenerate-and-diff CI job catches cards that drift from their manifest
entry — the failure mode that produced the current 22 unreproducible PNGs.

---

## 6. Consequences

- Adding a page becomes **one manifest entry**, not one HTML file plus one
  `TEMPLATE_MAP` line plus a generator run.
- 280 template files, 2 scripts and 46 dead binaries leave the repo.
- 22 live cards stop being unreproducible.
- Card copy becomes reviewable in a single diff and checkable by CI for the
  first time.
- The homepage card stops being a special case.
- Editorial cards gain genuine visual variety without per-card design work.
- Cost: the manifest is a new artifact to keep honest. The coverage check is
  what keeps it honest, and it is the gate that does not exist today.
