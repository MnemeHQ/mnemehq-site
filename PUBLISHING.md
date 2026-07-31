# Publishing governance for mnemehq.com

**This repository, [MnemeHQ/mnemehq-site](https://github.com/MnemeHQ/mnemehq-site), is the
canonical source and the deployment owner for [mnemehq.com](https://mnemehq.com).** The site
content under `site/`, the validation and asset tooling under `scripts/`, and the deploy workflow
under `.github/workflows/` all live here, and production is deployed from here (see
[Deployment ownership](#deployment-ownership)).

This document is the **current, canonical source of publishing governance** for the website. It
is the rulebook to follow when adding or changing pages.

## Historical decision records

The normative rules below originated as Architecture Decision Records in the product repository,
[MnemeHQ/mneme](https://github.com/MnemeHQ/mneme), while the site still lived there. Those ADRs
(ADR-003, ADR-006, ADR-007, ADR-008, ADR-011, ADR-012, ADR-015) **remain in that repository as the
immutable historical record** of why these decisions were made. This document supersedes them as
the source of *current* governance for the website: where an ADR describes the site as living in
the core repository or names the core repository as the deploy owner, that framing is historical.
The [Provenance](#provenance) section maps every source ADR to the section here that carries its
rules forward. No rule from those seven ADRs was dropped, and none was weakened.

---

## How these rules are enforced

Rules fall into three kinds. Each rule below is tagged with one:

- **[CI]** Mandatory, enforced automatically. A path-filtered PR workflow runs a validator and a
  failing check blocks the PR. See [Validators](#validators).
- **[OP]** Mandatory operator procedure. Not machine-checkable end to end; it is a required manual
  step at publish or deploy time. Skipping it produces a broken or unpublished page.
- **[ED]** Editorial guidance. Enforced by human review at PR time. These protect positioning and
  conversion quality; reviewers revert changes that break them.

---

## Repository layout and current paths

```
site/                     the static site exactly as deployed to mnemehq.com
  _snippets/              shared nav/footer/head sources (inlined into pages by scripts/sync_shared.py)
  assets/                 css, js, self-hosted fonts (+ fonts/licenses/), OG sources
  insights/               insight articles, the archive (all/), and topic hubs (topics/)
  concepts/               concept pages and the /concepts/ hub
  for/                    persona / buyer landing pages
  sitemap.xml             canonical URL list
scripts/                  deploy, validation and asset tooling
.github/workflows/        PR validators + the manual/scheduled deploy workflow
docs/site/                operational runbooks (see Related runbooks)
PUBLISHING.md             this document
```

All rules below reference these current paths. Site assets that belong on mnemehq.com live **only**
under `site/`, and `scripts/deploy_site.py` uploads from `site/`: a full deployment walks `site/`
and uploads the files present there, and a delta deployment uploads the added, copied, or modified
`site/` paths since the `site-deployed` tag (`git diff --diff-filter=ACM site-deployed..HEAD`).
Assets placed anywhere other than `site/` are not deployed.

---

## Deployment ownership

Production deployment of mnemehq.com is owned by **this repository** and is defined entirely by
[`.github/workflows/deploy-site.yml`](.github/workflows/deploy-site.yml):

- **Triggers:** push to `main` touching `site/**` or `scripts/deploy_site.py`; manual
  `workflow_dispatch`; and a daily `schedule` at 06:00 UTC. There is **no** `pull_request` trigger,
  so untrusted PR code never runs on the deploy runner.
- **Runner:** a dedicated, repository-scoped self-hosted runner labelled `mnemehq-site-deploy`
  (`runs-on: [self-hosted, mnemehq-site-deploy]`). It leaves egress from a static, cPanel-whitelisted
  IP. This is a separate runner registration from the core repository's runner; the two are not
  shared.
- **Mechanism:** `scripts/deploy_site.py` computes the changed-file delta since the `site-deployed`
  tag (or does a full upload when no tag exists), uploads via the cPanel Fileman API, purges the
  Cloudflare cache, runs post-deploy verification, then advances the `site-deployed` tag only after
  verification passes. IndexNow notifies search engines of updated URLs.
- **Credentials** are supplied at run time from repository secrets and variables (`CPANEL_API_TOKEN`,
  `CF_API_TOKEN`, `CF_ZONE_ID`, and the `CPANEL_HOST` / `CPANEL_PORT` variables). Their **values are
  never committed** to this repository and are not reproduced in any documentation.

**[OP]** Deploy behaviour changes (triggers, runner, upload/verify/purge logic) are owned by this
repository and are made only by editing the workflow and `scripts/deploy_site.py` here.

---

## Deploy and asset conventions

*Source: ADR-003. Historical rationale in the core ADR record.*

- **[OP] Canonical deploy path.** All site assets that belong on mnemehq.com live under `site/`.
  Do not place site assets in the repository root or other directories and expect them to deploy.
- **[OP] Working files stay out of `site/`.** Pages downloaded for editing, half-finished drafts,
  and scratch copies live in the repository root or a `scratch/` directory (gitignored), never under
  `site/`, and are never deployed.
- **[OP] Asset versioning for cache-busting.** cPanel shared hosting does not reliably overwrite
  files in place, and there is no CDN purge-by-hash. When a static asset (image, font) changes, ship
  it under a **new versioned filename** (`logo.png` -> `logo-v2.png` -> `logo-v3.png`;
  `og.png` -> `og-v2.png`) and update every HTML reference in the same change. Do **not** rely on
  query-string cache-busting (`?v=2`); it does not change the server-side file. (Current live assets
  include `logo-v3.png` and `favicon-v2.png`.)
- **[ED] Logo and image formats.** The site uses a dark background (`#0c0c0d`). The nav logo is a
  transparent PNG with light-coloured marks; the favicon is a square PNG; OG images are opaque PNG
  at exactly 1200x630 (see [OG images](#og-images)). The dark-navy 2000x2000 logo variant is not
  used on the dark site (it creates a visible box in the nav).
- **[CI] Nav and page structure.** All pages share the canonical nav and footer, with the correct
  `.active` state per section and homepage anchor links (`/#how-it-works`, `/#benchmarks`). Nav and
  footer consistency is enforced by `scripts/check_nav_footer.py`; the mobile sticky/hamburger nav
  is enforced by `scripts/check_sticky_nav.py`.
- **[ED] Typography.** Body / nav / UI text is **Inter**; the hero `h1` **only** uses **Instrument
  Serif**; code, terminal, and labels use **DM Mono**. Instrument Serif must not appear on `h2`,
  `h3`, or any sub-heading.
- **[CI] Hub-page completeness for every URL segment.** Every directory referenced from the nav,
  footer, or `site/sitemap.xml` must have an `index.html` at that directory. A subpage must never be
  reachable under a parent that returns 404 (add `/for/index.html` before shipping `/for/cto/`). The
  per-cohort hubs are checked by `scripts/check_for.py`, `scripts/check_compare.py`,
  `scripts/check_concepts_schema.py`, and `scripts/check_supported_languages.py`.
- **[CI] Breadcrumb depth mirrors URL depth.** Both the JSON-LD `BreadcrumbList` and the visible
  breadcrumb nav carry one `ListItem` per URL segment, in order (a page at `/for/cto/` has
  `Home -> For -> For CTOs`). When a hub page is added, every subpage's breadcrumb is updated to
  route through it in the same change.
- **[OP/ED] CSS class hygiene.** Every `class="..."` on an element inside `<body>` must resolve to a
  CSS rule on the same page (inline `<style>`) or an allowlisted state class (`active`, `open`,
  `hidden`, `selected`, `current`, `sr-only`). Typos in `class=` produce silent layout failures. The
  `style.classes` rule in `scripts/seo_check.py` surfaces violations, but `seo_check.py` runs
  **warn-only** inside `scripts/deploy_site.py` and does not block the PR or the deploy. Treat class
  hygiene as a mandatory review item at publish time.
- **[OP] Delta-deploy and file renames.** `scripts/deploy_site.py` computes its upload delta with
  `git diff --name-only --diff-filter=ACM site-deployed..HEAD`. Git-detected renames (`R`) are
  excluded by that filter and will not upload. When a rename is part of a deploy (for example
  `site/demo.html -> site/demo/index.html`), include the new path as a modified file (a
  trailing-newline edit on the post-rename path is the standing workaround) and remove the old path
  on the host so existing `.htaccess` rewrites do not redirect into a newly-empty directory.
- **Boundary note.** `theovalmis.com` pages are a separate personal site, never part of the Mneme
  deploy, and never live under `site/`.

---

## Insights articles

*Source: ADR-006 (SEO and schema) and ADR-015 (report-anchored titles). Historical rationale in the
core ADR record. The step-by-step registration procedure lives in
[`docs/site/insight-publishing-contract.md`](docs/site/insight-publishing-contract.md).*

**[CI]** `scripts/check_insights.py` (workflow
[`check-insights.yml`](.github/workflows/check-insights.yml)) is the publishing gate. For every
`site/insights/<slug>/index.html` it requires all of:

1. A sitemap entry in `site/sitemap.xml`.
2. An index card on at least one approved surface (the archive `site/insights/all/index.html` or a
   topic hub under `site/insights/topics/<hub>/index.html`).
3. A co-located `og.png` and `og:image` / `twitter:image` tags that resolve to a file under `site/`.
4. At least one incoming internal link.
5. A visible `<nav class="breadcrumb-nav">` breadcrumb with the three-item `Home -> Insights ->
   article` path.
6. A `BreadcrumbList` JSON-LD entry mirroring the visible breadcrumb.
7. A `TechArticle`/`Article` JSON-LD entry with matching `url` and non-empty `headline`.
8. A `CollectionPage` `hasPart` entry in the archive (or homepage) hub.

**[OP]** Required `<head>` scaffolding for every article (not all fully machine-checked): canonical
meta tags (`<title>` ending ` — Mneme HQ`, a 150-160 char `description`, `robots`, `canonical`,
`author`), `og:type=article` with the `article:*` properties (`published_time`, `author` -> the
`/founder/` URL, `section`), and Twitter card tags. Registration is a manual step: the pipeline does
**not** auto-discover articles, auto-insert sitemap or hub entries, or auto-create OG templates.

**[ED] Report-anchored titles (ADR-015).** When an article's spine is a named, searchable external
artifact (a report, study, survey, framework, playbook, or named system):

- Lead the `<title>` and `<h1>` with the **verbatim** searchable entity name (plus year if the name
  carries one), before any editorial angle, so it survives ~60-char title truncation and matches the
  query. Pair the entity with a hook (`<entity>: <angle>`); do not ship a bare keyword.
- Keep that entity string **identical** across all six title-bearing fields: `<title>`, `<h1>`,
  `og:title`/`twitter:title`, the JSON-LD `headline`, the `BreadcrumbList` final item `name`, and
  the inbound internal anchor text (index card + any cross-links).
- Lead the meta description (unified across `description`/`og:description`/`twitter:description`)
  with the source and a concrete figure **verified against the article body**, then pivot to the
  governance angle.
- The OG card headline leads with the same entity (see [OG images](#og-images)).
- **Do not retrofit** this onto original-concept or POV pieces; a report cited only as a supporting
  stat does not make an article report-anchored. Leaving a concept-first title on an original piece
  is correct.

**[ED] Editorial standards.** Publish an article only when it targets a distinct query, adds new
evidence to a thesis, creates an entry point from a named report/vendor/paper, or supports a
cornerstone through internal linking. Lead with the recognizable entity for SEO, then pivot to the
governance interpretation (News -> Problem -> Governance). Target engineering leaders, not individual
developers. Do not publish merely because a company announcement can be reframed as "this also needs
governance." House voice: concrete and declarative; never the word "bottleneck"; no em dashes as
connective tissue; the domain is always `mnemehq.com`.

## Video structured data

**[CI] VideoObject scope.** `VideoObject` JSON-LD is reserved for dedicated, video-first demo pages
under `/demo/` where a visible player or click-to-load video facade is part of the page experience.
Concept and insight pages may embed a supporting video, but they must not advertise that video as the
page's primary structured result. Do not create video-first pages solely for Google Video unless
Google Video is an approved acquisition channel. The validator is
[`scripts/check_video_markup.py`](scripts/check_video_markup.py).

---

## OG images

*Source: ADR-007. Historical rationale in the core ADR record.*

**[OP]** Every page gets its own OG image at `<page-path>/og.png`, rendered at exactly **1200x630px**
from an HTML source template `site/og-<slug>.html`. Regenerate with
`scripts/generate_og_images.py` (requires the `playwright` package and a local HTTP server, which the
script can start). OG source templates are committed alongside the PNGs they generate;
`scripts/deploy_site.py` walks `site/` and uploads the PNGs automatically, so no manifest update is
needed. For insights, add the template and mapping via `scripts/ensure_og_coverage.py` before
running the generator (see the insight publishing contract).

**[OP]** Every page carries both:

```html
<meta property="og:image"  content="https://mnemehq.com/<path>/og.png" />
<meta name="twitter:image" content="https://mnemehq.com/<path>/og.png" />
```

Pages without a page-specific image fall back to `https://mnemehq.com/og.png`.

**[ED] OG design system** (every OG image follows the site design language):

| Property | Value |
|---|---|
| Dimensions | 1200 x 630 px, exact (no skew, no letterbox) |
| Background | `#0c0c0d` |
| Accent | `#c8f060` |
| Text / muted | `#e8e8ec` / `#88889a` |
| Heading font | Instrument Serif (italic accent word in `#c8f060`) |
| Body font | DM Mono |
| Logo text | **"Mneme HQ"**, never "Mneme"; top-left, always visible |

LinkedIn caches OG images aggressively; use the LinkedIn Post Inspector to force a refresh after a
change.

---

## Persona / buyer pages (`/for/<role>/`)

*Source: ADR-008. Historical rationale in the core ADR record.*

**[ED] Audience-appropriate primitives.**

- **CTO / VP Engineering (`/for/cto/`):** no code blocks, YAML, command-line invocations, or
  per-tool config filenames. Frame in review capacity, architectural debt, headcount efficiency,
  vendor consolidation, audit posture, decision continuity. A "Business Outcomes" ROI section is
  required.
- **Platform / DevEx (`/for/platform/`):** may include configuration patterns and one or two short
  YAML/rules snippets. Frame in tool consolidation, multi-agent coverage, governance-as-code, rollout
  staging, override governance.
- **Staff / Principal (`/for/principal-engineer/`):** may include code-level primitives (hook
  intercept points, decision-record schema, CI gate behaviour). Frame in decision-once-enforced,
  repeated-review elimination, override observability, structural integrity across sessions.

**[ED] CTA discipline.** CTAs route to the next sensible step per audience. **Hard rule:** the CTO
page uses no "View on GitHub" CTA in the body (its primary CTA is `Talk to the founder` ->
`/contact/`); universal footer nav-links to `/github` are chrome, not CTAs. Persona pages over ~1,000
words carry a single mid-document Roadmap CTA panel (`.mid-cta-wrap` / `.mid-cta`) pointing to
`/roadmap/`, between the body and the footer CTA.

**[CI/ED] Structure.** Every `/for/<role>/` subpage and the `/for/` hub render a visible breadcrumb
above the hero (in addition to the JSON-LD `BreadcrumbList`); the `/for/` cohort schema is checked by
`scripts/check_for.py` (CI), while layout-class hygiene is a warn-only `scripts/seo_check.py` finding
reviewed at publish time. The `/for/cto/` page must
contain, in order: Hero, The Problem (review capacity vs AI throughput), Why Existing Approaches Do
Not Scale (comparison table), How It Works (high-level, no engineering primitives), Business Outcomes
(ROI cards), mid-document Roadmap CTA, Proof, CTA footer. Content review for persona pages is a
manual gate; edits that reintroduce engineering primitives on the CTO page are reverted on review.

---

## Concepts and the knowledge graph

*Source: ADR-011. Historical rationale in the core ADR record. Step-by-step in
[`docs/site/concept-publication.md`](docs/site/concept-publication.md).*

**[ED] Namespace boundary.** `/concepts/<slug>/` is the canonical-definitions namespace
(abstraction-first, stable references, tier-tagged); `/insights/<slug>/` is the applied-arguments
namespace. Insights point back to concepts; they do not redefine them. Content that blurs the
boundary (an opinion essay posing as a concept, or a definitional stub posing as an insight) is
recategorized.

**[ED] Asymmetric cross-references.** Cross-links use the shared `.related-panel` component (rich
card list: title plus a required one-line description, never a bare `<a>` list). The direction is
asymmetric by design: a concept page's panel is **Related operational essays** (points only to
`/insights/*`); an insight page's panel is **Related governance concepts** (points only to
`/concepts/*`).

**[ED] Concept tiers.** Concepts are organized as primitives -> properties -> outcomes, plus a
failure rail and an adjacent context set. Every concept declares its tier in the concept-graph
adjacency table, which is a **private** (ADR-002, Category 3) artifact held in the internal ops
store, not in this repository. The `/concepts/` hub diagram renders the tiers explicitly.

**[OP/private] Authority telemetry.** `scripts/graph_metrics.py` emits a weighted inbound-authority
score per concept (source weights: benchmark 5; demo / use-case / integration 3; compare / concept /
works-with 2; insight 1). The scores are **internal telemetry** and are never displayed on public
pages; the adjacency table, coverage matrix, and graph-health baselines live in the private ops
store. Only the analyzer script and the rendered HTML are public.

**[ED] SVG knowledge graph.** The `/concepts/` hub SVG is editorial; not every concept belongs in
it. A concept that occupies a structural position gets a node (following the `cmap-card-*` tier
conventions); a contextual or adjacent concept is instead listed, one slug per line, in
[`docs/site/svg-omitted.txt`](docs/site/svg-omitted.txt) so the local `scripts/check_concepts.py`
validator treats the omission as intentional.

---

## Conceptual authority and editorial discipline

*Source: ADR-012. Historical rationale in the core ADR record.*

**[ED] No glossary behaviour in `/concepts/`.** Every concept page must clear all of: body content
>= 1000 words; abstraction-first naming (no page titled after a feature, tool, or product surface,
such as "MnemeCheck CLI" or "Cursor Rules Format"); argument density (at least one explicit contrast
claim, "X is not Y, because ..."); and no SEO-stub pages. A page that fails any test is rejected,
deepened, or merged. `scripts/seo_check.py` surfaces sub-1000-word concept pages as warnings; the
rest is review.

**[ED] Diagrams are infrastructure evidence, not decoration.** Four diagrams are canonical
(governance propagation, enforcement checkpoints, provenance chain, architectural drift cascade) and
are **reused, not redrawn**; new pages embed the existing primitive. Shared visual conventions:
colour tokens (`--accent` active, `--teal` secondary, `--border2` neutral), glyph ordering (outcomes
top, primitives bottom), and label typography (DM Mono for metadata, Inter for nodes). Diagrams must
parse as valid SVG and be mobile-readable. No ornamental illustrations: if a claim reads better in
prose, the prose wins and the diagram is removed. (Which canonical primitive lives on which page is
defined in the private knowledge-graph roadmap.)

**[ED] Flagship concept pages.** The four highest-authority concepts (Governance Infrastructure,
Verification Contracts, Governance Before Generation, Architectural Governance) are flagship
canonical references and carry stricter minimums: >= 1500 words; >= 4 links to other concepts; >= 3
to insights; >= 2 to demos; >= 1 to a benchmark (or a benchmark-scenario citation); >= 2 diagrams
(at least one canonical primitive); full `TechArticle` + `DefinedTerm` JSON-LD. Flagships are
maintained continuously, not snapshotted.

**[ED] Concept-to-benchmark reinforcement.** Every concept that can be empirically measured cites the
benchmark assertion that grounds it; where the data has not published yet, it cites the benchmark
scenario that would produce it, so the citation slot is visible.

**[ED] Recurring frames and terminology lock.** The "X is not governance" series (memory, prompts,
review, observability, ...) uses the full insights template and cross-links every existing entry so
it compounds; new entries ship only when the conflation is real and structural. Terminology is
stable across `/concepts/`, `/insights/`, and `/architecture/`: use "decision corpus" (not "memory
store" / "rules file"), "verification contract" (not "test case" / "assertion"), "governance
propagation" (not "rule sync" / "config distribution"), "drift" (not "regression" / "tech debt" in
the AI-coding sense), and "enforcement" (not "validation" / "checking" for the governance layer).
New terminology requires explicit consideration and a documented amendment to this file.

---

## Validators

Path-filtered PR workflows under `.github/workflows/` run these on every relevant PR; a failing check
blocks the PR. All are standard-library-only Python.

| Validator | Workflow | Enforces |
|---|---|---|
| `scripts/check_encoding.py site scripts` | `encoding-check.yml` | UTF-8, no mojibake or BOM in `site/` and `scripts/` |
| `scripts/check_nav_footer.py` | `nav-footer-check.yml` | shared nav/footer consistency |
| `scripts/check_sticky_nav.py` | `sticky-nav-check.yml` | mobile sticky/hamburger nav |
| `scripts/check_insights.py` | `check-insights.yml` | insight registration (sitemap, cards, OG, breadcrumb, schema, hub) |
| `scripts/check_compare.py` | `check-compare.yml` | `/compare/` hub invariants |
| `scripts/check_concepts_schema.py` | `check-concepts-schema.yml` | `/concepts/` schema graph |
| `scripts/check_for.py` | `check-for.yml` | `/for/` persona-cohort schema |
| `scripts/check_supported_languages.py` | `check-supported-languages.yml` | supported-languages schema |
| `scripts/test_deploy_verify.py` | `test-deploy-verify.yml` | deploy-verification helpers |

Two more validators run **outside** the PR-check workflows:

- `scripts/seo_check.py` runs inside `scripts/deploy_site.py` as a warn-only pre-flight (CSS class
  hygiene, word-count floors); it never blocks a deploy but its findings are the CSS-hygiene and
  concept-length gates referenced above.
- `scripts/check_concepts.py` is a **local** concept-hub validator (run it before opening a concept
  PR); it is not wired to a CI workflow. It reads `docs/site/svg-omitted.txt`.

---

## Provenance

Every source ADR (retained historically in [MnemeHQ/mneme](https://github.com/MnemeHQ/mneme)) maps to
the section here that carries its current rules forward:

| Source ADR (core) | Scope | Carried forward in |
|---|---|---|
| **ADR-003** Site Publishing Guidelines | `site.publishing` | [Deploy and asset conventions](#deploy-and-asset-conventions); nav/typography/hub/breadcrumb/CSS rules; [Deployment ownership](#deployment-ownership) |
| **ADR-006** Insights Article SEO and Schema Requirements | `site.insights_seo` | [Insights articles](#insights-articles) + [`docs/site/insight-publishing-contract.md`](docs/site/insight-publishing-contract.md) |
| **ADR-007** OG Image Generation | `site.og_images` | [OG images](#og-images) |
| **ADR-008** Persona / Buyer-Page Content Standards | `site.persona_pages` | [Persona / buyer pages](#persona--buyer-pages-forrole) |
| **ADR-011** Knowledge-graph content architecture | `site.knowledge_graph` | [Concepts and the knowledge graph](#concepts-and-the-knowledge-graph) + [`docs/site/concept-publication.md`](docs/site/concept-publication.md) |
| **ADR-012** Conceptual-authority discipline | `site.conceptual_authority` | [Conceptual authority and editorial discipline](#conceptual-authority-and-editorial-discipline) |
| **ADR-015** Report-Anchored Insight Titles | `site.insights_seo.report_titles` | [Insights articles -> Report-anchored titles](#insights-articles) |

The historical `scripts/deploy.py` name used in ADR-003 is now `scripts/deploy_site.py`. References in
the source ADRs to the site or deploy tooling living in the core repository are historical; both live
here now.

---

## Related runbooks

- [`docs/site/insight-publishing-contract.md`](docs/site/insight-publishing-contract.md) — the full
  step-by-step contract for registering a new insight article.
- [`docs/site/concept-publication.md`](docs/site/concept-publication.md) — the checklist for
  publishing a new `/concepts/` page.
- [`docs/site/svg-omitted.txt`](docs/site/svg-omitted.txt) — the intentional-omission allowlist read
  by `scripts/check_concepts.py`.
