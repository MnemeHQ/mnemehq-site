# Citation-worthiness evidence pass — design

Status: approved for implementation
Date: 2026-08-30

## Decision (ADR-003)

Public empirical claims must resolve to a verified public artifact and
carry an explicit claim boundary.

This is the whole architectural decision. It does not specify layout,
component structure, or page prose — those are implementation detail,
recorded below and subject to change without an ADR revision.

## Scope

Three existing pages get a citation-worthiness pass using first-party
evidence already public in `MnemeHQ/mneme`. No new pages.

- `/insights/how-ai-coding-agents-use-adrs/` — evidence unit **E1**
- `/insights/ai-native-sdlc-architecture-layer/` — evidence unit **E2**
- `/open-source-ai-coding-agent-governance/` — methodology unit **M1**, no
  empirical evidence block

## Evidence units

**E1** — canonical benchmark, already public before this work started.
- Source: `https://github.com/MnemeHQ/mneme/blob/main/examples/benchmarks/reports/RESULTS.md`
- Result: 7/7 governed violation scenarios produced the expected verdict.
- Also surfaced: the same report's retrieval precision@3 = 0.33 (n=5) —
  published alongside the flattering number, not omitted.
- Boundary: frozen benchmark scenarios, not production teams.
- Status: `verified`.

**E2** — enforcement-quality suite, merged to `main` this session via
`MnemeHQ/mneme#341` (squash-merged `7b062b4`).
- Source: `https://github.com/MnemeHQ/mneme/blob/main/examples/benchmarks-enforcement-quality/reports/RESULTS.md`
- Result: 3/3 violation scenarios caught, 0/4 benign controls blocked
  (false-positive rate 0%).
- If this suite's retrieval precision@3 = 1.00 is mentioned on-page, it
  must state explicitly that the figure belongs only to this suite's n=3
  violation scenarios and is not comparable to E1's 0.33 (different
  suite, different scenario count).
- Boundary: same frozen-suite / non-production boundary as E1.
- Status: `verified`.

**M1** — methodology unit for the OSS governance page. Not an evidence
unit under the registry/checker — no reproducible result, no claim
boundary needed. Four-layer definitions, inclusion/classification
criteria, a primary-source link per classification where supportable,
and one page-level "Last reviewed" date. No per-tool verification dates
(decays into a liability; rejected in brainstorming).

## Evidence registry

New file: `docs/site/evidence-contract.json`. One entry per unit:

```json
{
  "E1": {
    "source_artifact_url": "https://github.com/MnemeHQ/mneme/blob/main/examples/benchmarks/reports/RESULTS.md",
    "required_result_tokens": ["7/7", "0.33"],
    "forbidden_claims": ["guarantees", "eliminates", "always", "prevents", "in production"],
    "status": "verified"
  },
  "E2": {
    "source_artifact_url": "https://github.com/MnemeHQ/mneme/blob/main/examples/benchmarks-enforcement-quality/reports/RESULTS.md",
    "required_result_tokens": ["3/3", "0/4"],
    "forbidden_claims": ["guarantees", "eliminates", "always", "prevents", "in production"],
    "status": "verified"
  }
}
```

No `allowed_claims` verb whitelist (rejected — too easy to game with a
technically-permitted verb wrapping an overclaim; the forbidden list plus
required tokens plus mandatory limitation text is the actual contract).

## Markup convention

Reuses the existing `.callout` class already defined inline in each
article's `<style>` block — no new component. Adds a modifier and three
sub-elements a script can address without parsing prose:

```html
<div class="callout callout-evidence" data-evidence-id="E1">
  <p class="evidence-claim">...states the result, includes required tokens...</p>
  <p class="evidence-limitation">...states what this does not prove...</p>
  <a class="evidence-source" href="...">Method and artifacts &rarr;</a>
</div>
```

`.callout-evidence` gets a small inline style addition per article
(distinguishing background/border tint) — not a shared stylesheet
change, matching how `.callout` itself is already defined per-article.

## Checker: `scripts/check_evidence.py`

Scans an explicit list of governed pages (initially the two evidence
pages; extensible by adding a path to a constant, same pattern as
`check_concepts.py`'s `HUB`/`CONCEPTS_DIR` constants) for
`data-evidence-id="..."` blocks. Per block:

1. Evidence ID exists in the registry.
2. Registry `status` for that ID is `"verified"`.
3. `evidence-source` `href` equals the registry's `source_artifact_url`
   exactly.
4. Every string in `required_result_tokens` appears somewhere in the
   block's text (`evidence-claim` + `evidence-limitation` concatenated).
5. `evidence-limitation` element exists and is non-empty after stripping
   tags/whitespace.
6. No string from `forbidden_claims` appears anywhere in the block's
   text (case-insensitive substring match).

Exit codes match repo convention: 0 clean, 1 errors, 2 warnings-only.
No warnings are currently defined — checks 1–6 are all errors.

Tests: `tests/test_check_evidence.py` (or under `scripts/`, matching
`scripts/test_sync_insights_catalog.py`'s sibling-file convention) —
fixture HTML snippets covering: valid E1, valid E2, unknown evidence ID,
`status != verified`, mismatched source href, missing limitation,
missing a required result token, forbidden-claim string present.

## Page insertion locations

**ADR article** (`site/insights/how-ai-coding-agents-use-adrs/index.html`):
- Line 344 (the Redis/BullMQ paragraph under "Making ADRs Executable"):
  add one clause reframing it as a hypothetical — e.g. lead with "Here's
  a hypothetical:" — no other rewrite of that paragraph.
- Insert the E1 `.callout-evidence` block immediately after that
  paragraph (after current line 345), before the "ADRs in CI and at
  Edit Time" `<h2>`.

**AI-native SDLC article** (`site/insights/ai-native-sdlc-architecture-layer/index.html`):
- Insert the E2 block at the article's guidance-vs-deterministic-
  enforcement distinction (exact anchor confirmed by reading the
  article during implementation — its thesis section, not duplicated
  from the ADR article's placement logic).
- States 3/3 and 0/4 inline, states the fixed-suite/non-production
  boundary inline, links to the E2 artifact.
- Does not also carry an E1 block — one empirical unit per page per the
  approved mapping, not evidence-for-symmetry.

**OSS governance page** (`site/open-source-ai-coding-agent-governance/index.html`):
- No `.callout-evidence` block, no registry entry.
- Add: four-layer definitions (context/memory, architecture discovery,
  runtime governance, architectural governance — already named in the
  page's existing taxonomy per prior research), explicit
  inclusion/classification criteria, a primary-source link per
  classification where one exists, and a single page-level "Last
  reviewed: <date>" line.

## Out of scope

- Any page beyond these three.
- `validation/eventcatalog/` (PE1) — still unpublished in the product
  repo; not cited anywhere.
- Per-tool verification dates or a staleness-check script for the OSS
  page.
- A shared `.callout-evidence` CSS component in `base.css` — kept
  per-article inline, matching existing convention.
- `allowed_claims` verb whitelist.

## PR discipline

Branch `site/citation-worthiness-evidence` → PR → CI → squash merge, no
direct push to `main`. Provenance block filled with actual agent/session
info. Scope held to evidence/citation-worthiness only — no unrelated
cleanup.
