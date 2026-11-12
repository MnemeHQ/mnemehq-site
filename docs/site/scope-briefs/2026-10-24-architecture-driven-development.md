# Scope brief: Post-Architecture Driven Development Positioning

Status: **dropped as scoped** (flagship merges into existing spec-driven pages; concept page and cluster held for an owner decision)

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Architecture Driven Development Positioning` |
| Created / last updated (UTC) | 2026-10-24 / 2026-10-24 |
| Shape | 1 user turn ("Scope content"), 2 assistant turns; read in full. The second turn expands the first into a six-asset cluster. |
| Repo check | Spec-driven coverage already exists: `spec-driven-development-still-needs-governance`, `google-spec-driven-development-not-enough`, `/concepts/spec-driven-development/`, `/concepts/objective-driven-development/`. No page uses "architecture-driven development". |

## Build card

| Field | Value |
|---|---|
| Kind | strategy only, plus a possible update to an existing insight |
| Title | none (flagship proposed: From Spec-Driven to Architecture-Driven Development: Why AI Agents Need Enforceable Decisions) |
| Slug | none; candidate target for an update: `spec-driven-development-still-needs-governance` |
| Report-anchored (ADR-015) | no |
| Topic hub | n/a |
| Content type (`--type`) | n/a |
| OG headline | n/a |
| Editorial gate | **fail** for a new flagship: same query as two shipped pages. The concept page, comparison and experiment are separate asks (below) |
| Five questions | not applicable until a verdict changes |
| Cannibalisation | `find_overlap.py`: `spec-driven-development-still-needs-governance` 135.0, `google-spec-driven-development-not-enough` 133.0, `/concepts/spec-driven-development/` 125.6. Verdict: **update instead / merge**. At most, add a short prior-art section to `spec-driven-development-still-needs-governance` naming the existing "architecture-driven development" usage and stating what enforceable decisions add. |
| Cross-links | `spec-driven-development-still-needs-governance`, `google-spec-driven-development-not-enough`, `/concepts/spec-driven-development/` |

## Draft quality gate (filled at build time)

Not applicable: nothing is built from this brief unless the owner picks the update.

## Agreed scope

The chat's first turn found that "Architecture-Driven Development" is already in use (a May 2026 ArDD white paper, an October 2026 ArchitectCoder launch, older literature) and that "ADD" collides with Carnegie Mellon's Attribute-Driven Design. It advises not claiming the term and instead showing what makes it operational and verifiable. The second turn proposes six assets: the flagship insight, a concept page, a technical guide, an SDD comparison, a perspective piece and an experiment, with Spec Kit and C4 integration guides later.

## Key facts, figures, sources

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| May 2026 ArDD white paper (Guillermo Quiros) | unverified: architecturedrivendevelopment.com | unverified |
| October 2026 ArchitectCoder launch | unverified: dev.to post | unverified |
| Decision-Driven Development used by the DDSE Foundation | unverified: ddse-foundation.github.io | unverified |
| GitHub Spec Kit includes architecture planning, constitutions and analysis gates | unverified: Spec Kit docs | unverified |
| ADD = Attribute-Driven Design (CMU SEI) | unverified | unverified |

## Mneme claims and maturity

| Claim | SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL |
|---|---|
| "Decision Execution Layer" as Mneme's role and "AI writes the code. Architecture decides what ships." as a core message | CONCEPTUAL positioning; a category or tagline change needs ADR-001/013/014 amendments in `MnemeHQ/mneme` first, so do not use it on the site |
| Context vs decision governance experiment (variants A, B, C) | PLANNED; no results, so no comparative claim |

## Positioning constraints

Do not claim ownership of ArDD. Do not set it against spec-driven development. Do not imply universal deterministic enforcement. Do not propose a new methodology name.

## Non-insight site edits requested

A concept page `/concepts/architecture-driven-development/`, an SDD comparison page and an experiment. **All held**: the concept needs the same terminology decision and amendment as any new concept term, and the experiment is evidence-gated.

## Open questions

Owner: add the prior-art section to `spec-driven-development-still-needs-governance`, or drop the chat? Is ArDD ever to become a concept term?
