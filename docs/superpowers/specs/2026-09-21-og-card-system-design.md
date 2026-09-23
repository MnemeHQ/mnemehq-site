# OG card system — five families, one data-driven renderer

Date: 2026-09-21
Status: approved design (revised after review), not yet implemented
Supersedes in practice: the `og-<slug>.html` pipeline described in `PUBLISHING.md` §OG images (source ADR-007, superseded by ADR-016)

---

## 1. Why

A GTM audit of the social cards found they read as "technical documentation"
rather than as Mneme HQ, and that they are illegible at the size people
actually see them. Investigation of the repo confirmed the diagnosis and
turned up drift the audit did not name.

### Verified state

| Fact | Measured |
|---|---|
| Render sources | 280 `site/og-*.html` |
| `TEMPLATE_MAP` entries | 283 lines, 280 unique keys, 279 unique outputs |
| Committed `og.png` | 300 — of which **22 are produced by no generator** |
| Those 22 | **all 22 are advertised by a live page**; none is safe to delete |
| Committed `site/assets/og/*.jpg` | 46 — **referenced by zero pages**, written by no script |
| Homepage card | `og-home-v2.png`, correctly versioned per `PUBLISHING.md:105`, but **outside `TEMPLATE_MAP`** — it has no render source and cannot be rebuilt |
| Pages | 322 `index.html`, **all** carry `og:image` |
| `og:image:width` / `:height` / `:alt` / `twitter:image:alt` | **0 of 322** |
| Category tags | 30 distinct values, incl. `Concept` (33) vs `Concepts` (3), `Docs · 0.9.0` (2) vs `Docs` (1) |

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
is.

### Non-goals

- `audit/frontend/src/styles.css` and its build output `site/audit/workspace/`.
  Tracked separately.
- Re-authoring page content. Only card copy is authored here.

---

## 2. Design

### 2.1 The governing constraint

**It is one 1200×630 image.** LinkedIn and mobile scale that same file down;
there is no separate mobile asset. Legibility is bought by **cutting copy,
not by inflating type**.

Acceptance surface is **360px**. A card that fails at 360px fails.

### 2.2 Type scale

| Element | Legacy | **New** | @552px | @360px |
|---|---|---|---|---|
| Headline (auto-fit) | 42 | **61–94** | 28–43 | 18.3–28.2 |
| Identity "Mneme HQ" | 26 | **42** | 19.3 | 12.6 |
| Category label | 11 | **30** | 13.8 | 9.0 |
| Supporting sentence | 15 | **38** | 17.5 | 11.4 |
| Proof / comparison value | — | **44** | 20.2 | 13.2 |
| Functional label | 11 | **30–32** | 13.8–14.7 | 9.0–9.6 |
| Printed URL | 12 | **removed** | — | — |

**Floor: nothing renders below 30px source.** Auto-fit sizes on the longest
line, so a deliberate break never shrinks the card:

| Longest line | Size |
|---|---|
| ≤38 chars | 94px |
| ≤62 chars | 78px |
| ≤92 chars | 70px |
| else | 61px |

The regular serif stays at editorial weight. **The italic sage phrase is the
brand device and is preserved exactly.**

### 2.3 Family assignment — by path, not by tag

**Family is derived from URL path.** The legacy `.tag` values are not
consulted: they are the drift (30 values, including singletons like
`for ctos`, `report analysis`, `category distinction`), and reading them
would carry the old taxonomy into the new system.

| Path prefix | Family | Pages |
|---|---|---|
| `insights/`, `concepts/` | **editorial** | 222 |
| `integrations/`, `works-with/`, `supported-languages/` | **integration** | 32 |
| `demo/`, `benchmark/`, `architecture/`, `audit/`, `standards/`, `docs/` | **proof** | 27 |
| `compare/`, `use-cases/` | **comparison** | 24 |
| root, `about/`, `founder/`, `pilot/`, `contact/`, `for/`, `roadmap/`, `privacy/`, `pricing/`, `platforms/` | **brand** | 10 |

This resolves **315 of 322 pages**. Seven need an explicit `family:`
override and are listed exhaustively so the migration has no unknowns:

```
enterprise/trust/            for/cto/        for/platform/
for/principal-engineer/      qa-glossary/    security/data-handling/
open-source-ai-coding-agent-governance/
```

The `/for/<role>/` pages take `brand`, matching their persona-page framing
in `PUBLISHING.md` §Persona pages.

### 2.4 Editorial geometry — semantic rule first, override second

~222 hand-drawn metaphors is not feasible and 222 identical ones is the
current problem. Motif is chosen by a **deterministic topic rule**, not by
hash, so the geometry means something:

| Topic signal in slug | Motif |
|---|---|
| drift, divergence, deviation, decay | `branch` |
| layer, platform, stack, control plane, infrastructure | `stack` |
| boundary, perimeter, scope, zero-trust, guardrail | `boundary` |
| coordination, multi-agent, shared, swarm, orchestration | `connected` |
| propagation, continuity, memory, provenance, lifecycle | `propagation` |
| gap, break, loss, compaction, forgetting | `broken` |
| intersection, tradeoff, versus, convergence | `intersection` |
| isolation, silo, standalone, single-agent | `isolated` |
| *no signal* | `connected` (default) |

**The slug hash varies the geometry *within* the chosen motif** — node
positions, edge subsets, which element is highlighted — so cards sharing a
motif still differ, while the motif itself stays meaningful.

`tone` is **explicit in the manifest, never generated**. It defaults to
`neutral`. Only `failure` introduces red. A card about a governance layer
does not assert that something was blocked.

### 2.5 Colour

Inherits `docs/site/cta-system.md` unchanged: sage `#b5cc7a` for held
decisions and shipped status, `--error` `#ff5c7a` for blocked verdicts
(`tone: failure` only), `--warn` `#f6b94b` for advisory states, `--quiet`
`#88889a` for category labels. No lime; `sweep_accent_sage.py --check` must
continue to pass.

---

## 3. Architecture

### 3.1 `site/og/cards.yaml` — the manifest

Semantic content and visual presentation are **separate fields**. Nothing
encodes typography inside a content string, so alt text, metadata, search
and any future consumer can read `headline` without knowing renderer
conventions.

```yaml
insights/software-factory-governance-layer:
  headline: The Software Factory Needs a Governance Layer   # semantic
  lines:                                                    # presentation
    - The Software Factory Needs a
    - Governance Layer
  accent: Governance Layer        # the italic sage phrase
  tone: neutral                   # neutral | failure — explicit, never derived
  # family: omitted -> derived from path (editorial)
  # motif:  omitted -> derived from topic rule (stack)
  # alt:    omitted -> falls back to headline

demo/storage-decision:
  headline: The agent proposed it. The decision refused it.
  rows:
    - [ADR-014, Postgres is the record., held]
    - [AGENT, Add MongoDB., neutral]
    - [BLOCKED, Before the commit., denied]
  alt: Mneme blocks an agent change that violates an architectural decision.
```

- `lines` is optional. Absent, the renderer wraps `headline` naturally.
  Present, it must join back to `headline` ignoring whitespace — a CI check,
  so the two cannot drift apart.
- `alt` defaults to `headline`. Proof, integration and comparison cards
  override it, because their meaning sits in the proof object rather than
  the words above it.

**Coverage is strict in production.** Every sitemap page must resolve to an
explicit manifest record before CI passes. Derived values exist for
development and new-page bootstrapping only, and `render_og.py --strict`
(the mode CI and deploy use) fails on any page lacking a record. A generic
derived card must never ship silently — that is how the current drift was
created.

### 3.2 Scripts

| Script | Responsibility |
|---|---|
| `scripts/render_og.py` | Loads manifest, dispatches to one of five family templates, renders via Playwright with local woff2. `--strict` for CI. |
| `scripts/check_og_coverage.py` | Every page has an explicit record; every record has a page; every advertised `og:image` has a reproducible source. |
| `scripts/lint_og_voice.py` | **Advisory lint, not a naive character gate** — see below. |
| `scripts/sync_og_meta.py` | Writes the four metadata tags across all pages. |

Family templates live in `templates/og/` as HTML with a shared stylesheet,
so layout stays CSS rather than hand-computed pixel maths.

**Voice lint design.** The house rules (`PUBLISHING.md:206`) are "never the
word 'bottleneck'" and "no em dashes as connective tissue". The second is
semantic: banning every `—` would be stricter than the editorial rule and
would break legitimate uses such as a quoted external title. So the lint:

- flags `bottleneck` and em-dash occurrences as **warnings by default**;
- supports a per-entry `voice_ok: [reason]` escape for legitimate cases
  (quoted report titles, external product names);
- fails CI only on flagged occurrences **without** an escape.

This keeps the rule enforced while leaving room for the cases a regex cannot
judge. Note that during design review two mockup headlines violated these
rules, so the lint is earning its place — it just should not be absolute.

### 3.3 Renderer determinism

Rendering is pinned, or "deterministic" cards produce pixel diffs whenever
the browser changes underneath them:

- `playwright==1.58.0` pinned in the project's requirements
- Chromium `145.0.7632.6` (the build that Playwright 1.58.0 installs)
- fixed `device_scale_factor=1`, viewport `1200×630`, local woff2 only
- CI asserts the resolved Chromium build matches the pin before rendering

Version bumps are a deliberate change that regenerates all cards in one
reviewable commit, never an incidental side effect of a dependency update.

### 3.4 Generators in scope

`gen_benchmark_visual.py`, `gen_benchmark_square.py` and
`gen_architecture_visual.py` carry `ACCENT = (200, 240, 96)` and move to
sage `(181, 204, 122)`; their outputs regenerate.

`verify_pr1.py` … `verify_pr4.py` assert on computed
`backgroundColor === 'rgb(200, 240, 96)'`. After the sage sweep those
assertions match nothing and report success-by-vacuity. They are updated to
the current token or retired with the PRs they verified.

---

## 4. Asset versioning — cards ship as `og-v2.png`

`PUBLISHING.md:105` is an `[OP]` rule that names this exact case:

> When a static asset (image, font) changes, ship it under a **new versioned
> filename** (`logo.png` → `logo-v2.png`; **`og.png` → `og-v2.png`**) and
> update every HTML reference in the same change. Do not rely on
> query-string cache-busting.

The reason is operational, not cosmetic: cPanel shared hosting does not
reliably overwrite files in place. **Overwriting 300 `og.png` files would
violate a standing deploy contract and could serve stale cards
indefinitely.**

Therefore:

- New cards render to `<page-path>/og-v2.png`.
- All 322 pages' `og:image` and `twitter:image` move to the new filename in
  the same change, alongside the four new metadata tags.
- Old `og.png` files become unreferenced and are removed in the cleanup step
  (§5.3), not during cutover.
- `og-home-v2.png` is superseded by `site/og-v2.png` from the Brand family,
  bringing the homepage inside the canonical system.

This also dissolves the 22-unreproducible-PNG problem: those pages get a
generated `og-v2.png` from the manifest, and the stale files they currently
point at stop being referenced.

---

## 5. Cutover — three separable stages

Deliberately **not** one step. "The new system works" and "the rollback
material is gone" are different claims and are proven at different times,
even though the eventual PR is squash-merged.

### 5.1 Stage A — build alongside (nothing served changes)

1. Renderer, five family templates, manifest schema, checks, version pins.
2. Manifest seeded: family from path (315 automatic, 7 overrides), copy
   extracted from the existing templates' `.heading`/`.subtitle`, the 4
   over-long headlines rewritten, `tone` assigned, `lines` added where a
   deliberate break is wanted.
3. Render all cards to `site/og-staging/`.
4. **Acceptance gates**, all before anything is swapped:
   - every one of the 322 pages resolves to an explicit record (`--strict`);
   - the 22 currently unreproducible cards are now reproducible — this is a
     named acceptance list, not a spot check;
   - the homepage card is a named acceptance test;
   - all outputs exactly 1200×630, no source type below 30px;
   - visual QA at 552px and 360px across all five families, every Brand and
     Proof card, plus each of the eight motifs at short/medium/long headline
     and every `tone: failure` card.

### 5.2 Stage B — switch references

5. Render to `<page-path>/og-v2.png`.
6. `sync_og_meta.py` repoints `og:image` / `twitter:image` and adds
   `og:image:width`, `og:image:height`, `og:image:alt`, `twitter:image:alt`
   across all 322 pages.
7. Deploy and verify live.

Rollback at this point is reverting one commit: the legacy templates,
generator and old `og.png` files are all still present.

### 5.3 Stage C — cleanup, only after B is proven live

8. Delete 280 `site/og-*.html`, `generate_og_images.py` and its
   `TEMPLATE_MAP`, `ensure_og_coverage.py`, the 46 dead
   `site/assets/og/*.jpg`, the superseded `og.png` files and
   `og-home-v2.png`.
9. Rewrite `PUBLISHING.md` §OG images — its design table still specifies
   lime `#c8f060` and an "italic accent word in `#c8f060`", and its `[OP]`
   process still describes `og-<slug>.html` + `ensure_og_coverage.py`.
10. Update `docs/site/cta-system.md` §8, whose line "OG images: any new page
    still follows the AGENTS.md og-template pipeline — unaffected" becomes
    false.

---

## 6. Verification

| Check | Gate |
|---|---|
| Every page has an explicit record, no orphans | `check_og_coverage.py`, CI |
| Every advertised `og:image` has a reproducible source | `check_og_coverage.py`, CI |
| `lines` joins back to `headline` | `check_og_coverage.py`, CI |
| Voice rules, with escapes | `lint_og_voice.py`, CI |
| No source type below 30px | `render_og.py` tests |
| All outputs exactly 1200×630 | post-render assertion |
| Renderer versions match the pin | CI pre-render assertion |
| Palette contract intact | `sweep_accent_sage.py --check` |
| 360px legibility | manual QA, contact sheet at 1200/552/360 |
| Line endings / encoding | existing `check_line_endings.py`, `check_encoding.py` |

A regenerate-and-diff CI job catches cards drifting from their manifest
entry — the failure mode that produced the current 22 unreproducible PNGs.

---

## 7. Consequences

- Adding a page becomes **one manifest entry**, not an HTML file plus a
  `TEMPLATE_MAP` line plus a generator run.
- 280 template files, 2 scripts and 46 dead binaries leave the repo.
- 22 live cards stop being unreproducible; the homepage stops being a
  special case.
- Card copy becomes reviewable in one diff and checkable by CI for the first
  time.
- Editorial cards gain meaningful visual variety without per-card design
  work.
- Costs: a new manifest to keep honest (the coverage check is what keeps
  it honest), a one-time 322-page reference rewrite, and a pinned browser
  that must be bumped deliberately.
