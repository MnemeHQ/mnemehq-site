# Scope brief: Post-Open Architecture Page Assessment

Status: **parked** (owner decision 2026-10-25, TheoV823): no spec or site work until the O1 validation produces results. Revisit then; the open question of where the spec lives (an ADR in `MnemeHQ/mneme` or this repo) is deferred with it.

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Open Architecture Page Assessment` |
| Created / last updated (UTC) | 2026-10-09 / 2026-10-09 |
| Shape | 4 turns: "Do we need an open architecture page?", URL structure for per-repo scorecards and a leaderboard, three options with scores (Observatory preferred), then the user's pushback, which ChatGPT accepted. **The final turn reverses the Observatory proposal.** |
| Repo check | No `site/research/` or `site/repositories/`. Not started. |

## Build card

| Field | Value |
|---|---|
| Kind | **spec / ADR now; site page later** (not an insight) |
| Now | an internal identity and permalink specification, an assessment reproducibility contract, a public/private publication policy, maintainer notification, correction and opt-out rules. Recorded as a small architecture decision, not a website workstream |
| Later (after O1 validation) | `/research/open-architecture/` page and a few case studies at `/research/open-architecture/case-studies/{slug}/` |
| Conditional | `/repositories/github/{owner}/{repo}/` (+ `assessments/{id}/`, `decisions/{id}/`), `/repositories/leaderboard/`, `/repositories/compare/`, only with enough validated findings and real external interest |
| Cannibalisation | `find_overlap.py` for the research page: top 37.5 `agentic-resource-discovery-agent-governance`, 30.4 `open-knowledge-format-vs-governance`. Clear |
| Editorial gate | n/a now (nothing to publish) |

## Agreed scope (final turn)

- Separate *how we know* (research) from *what we publish* (findings).
- Rejected: the label "Observatory" (a coined term nobody searches; same trap as premature category labels), the option scores (false precision; URLs can be 301'd cheaply, the data model is what is expensive), and the timing (zero scorecards published, O1 not validated, too early commercially).
- Adopted conventions:

| Decision | Convention |
|---|---|
| Repository identity | provider + immutable provider repository ID (GitHub numeric ID), not owner/name |
| Display URL | human-readable provider/owner/repo; renames redirect to the same identity |
| Assessment identity | stable opaque ID, independent of URL |
| Reproducibility | commit SHA, methodology version, evaluator version, evidence references |
| Decision identity | stable ID, not a regenerated title or position; candidates distinct from validated decisions |
| Publication state | draft, reviewed, published, withdrawn |
| Evidence | explicit provenance and verification status |
| Private audits | private by default; never auto-promoted from `/audit/` |
| Corrections | recorded, reviewable, attributable |

- Maintainer protections are a prerequisite: notify before publishing an evaluative scorecard; correction and dispute process; opt-out; distinguish missing evidence from demonstrated failure; publish methodology versions and limitations; no overall architecture score; no rankings without validation and a fair participation policy. Prefer repositories whose maintainers took part in validation.
- Keep `/benchmark/` (Mneme's governance effectiveness), `/audit/` (user-driven), `/architecture/` (Mneme's own architecture) separate from public repository assessments.
- The wedge stays enforcement at the agent boundary; O1/DG support it upstream ("how do we know which decisions exist and should apply?").

## Key facts, figures, sources

| Claim | Source | Verified? |
|---|---|---|
| Google Open Source Insights uses per-project URLs such as `/project/github/...` | deps.dev (exact URL not captured) | no |
| OpenSSF Scorecard gives independently addressable project assessments | not captured | no |
| Live Mneme pages reviewed: Architecture, Benchmark, Roadmap, Audit | mnemehq.com pages; re-check current wording | no |

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Decision discovery research (O1) and evidence relationships | Research harness SHIPPED as research-only (`mneme research open-architecture`, O1A benchmark harness in 0.10.0); results not validated, experiment in progress. Note: DG1 is decision governance semantics (ADR-031), not an evidence graph |
| Public scorecards, leaderboard | CONCEPTUAL |

## Positioning constraints

- Do not present experimental capabilities as shipped.
- Publish the scientific problem, methods and verified results (including failures); keep proprietary pipelines, reconciliation internals and enterprise acquisition workflows private.

## Non-insight site edits requested

Everything here is non-insight: the spec now; research page and case studies later. The chat's first answer also wanted a small Research section linked from Architecture, Roadmap and About (not primary nav). That is superseded by the "later" timing.

## Open questions

- Where does the spec live: an ADR in `MnemeHQ/mneme` (it concerns data model and identity), or this repo?
- First case study: only a repository whose maintainer has agreed to publication.
