# Scope brief: Post-Business Type Comparison and decision governance

Status: concept published in #214; insight 3 (`/insights/from-decision-records-to-decision-governance/`) **published 2026-10-15 in [#221](https://github.com/MnemeHQ/mnemehq-site/pull/221), deployed at `88d8edd9`**, typed **Perspective** under the 2026-10-14 type rule (no external anchor; the concept page owns the definition). Insight 2 (software factories) is merged into `software-factory-governance-layer` in the batch 3 PR, as a "Six ways factory output loses engineering intent" section. Every item is then shipped, so the chat can be marked once batch 3 is deployed

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Business Type Comparison and decision governance` |
| Created / last updated (UTC) | 2026-10-07 / 2026-10-07 |
| Shape | 3 turns: "Are we [this] type of business" (an image of an Entrepreneur/HBR post about AI-native startups), "Decision governance: a concept we need to write about?", then "Scope them" (concept page plus two insights). |
| Repo check | No concept page or insight on decision governance. The phrase already appears in product copy: `compare/sourcegraph-cody` ("Codebase Context vs Decision Governance") and `integrations/kiro`. |

## Build card

**Decision 2026-10-12:** "engineering decision governance" is the one new concept term. Before the concept page ships: a PUBLISHING.md terminology amendment and an ADR-001/013/014 check in `MnemeHQ/mneme`. Only "decision governance" is adopted; the rest of the chat's vocabulary (Decision Engineering, Decision Infrastructure, Decision Enforcement, Decision Evidence) is not locked.

**Product meaning comes from ADR-031** ("Decision Governance Semantics (DG1)", MnemeHQ/mneme, accepted 2026-10-08). The concept page and both insights must use its definition, not the chat's: decision governance answers three deterministic questions, (1) *effective resolution*: given the authoritative state and a governance context, which decisions govern it, which do not, and why; (2) *governance change*: between two snapshots, what effective governance changed, why, and which scope and rules are affected; (3) *evidence identity*: which canonical decision version and rule produced a given outcome. Maturity: ADR-031 is accepted and partly implemented on core `main`, **not released** (core CHANGELOG "Unreleased"); describe it as in progress until a release ships it. The terminology amendment should cite ADR-031.

| Piece | Kind | Slug | Hub | OG headline | Cannibalisation (`find_overlap.py`) | Verdict |
|---|---|---|---|---|---|---|
| Engineering Decision Governance | **concept page** (concept-publication contract, separate PR) | `concepts/engineering-decision-governance` | n/a | n/a | `docs/decision-model` 19.6, `stanford-ai-index-2026-engineering-governance` 18.1, `concepts/autonomous-software-engineering-governance` 17.0 | clear lexically; check intent against `concepts/autonomous-software-engineering-governance` and `docs/decision-model` |
| Why AI Software Factories Need Decision Governance | insight | `ai-software-factories-need-decision-governance` | ai-coding-agents | Software Factories Need Decision Governance | `software-factory-governance-layer` 83.2 (same thesis) | **merge or drop**: extend the software-factory pillar instead |
| From Decision Records to Decision Governance | insight (technical) | `from-decision-records-to-decision-governance` | architectural-governance | From Decision Record to Governed Decision | `how-ai-coding-agents-use-adrs` 39.3, `docs/how-to/adr-to-enforceable-decision` 30.1 | **re-angle**: stay conceptual (the nine stages); link the how-to for the hands-on version. **Batch overlap:** absorbs the Frontier Academy chat's "What Has to Become Machine-Readable" |

Report-anchored: no for all three. Eyebrows: Concept / Analysis.

Five questions (technical insight): changed: agents now execute decisions that were written for humans; matters: an ADR states a decision but does not say whether it is current, applies here or wins a conflict; breaks: agents act on superseded, misapplied or conflicting decisions; do: add lifecycle, scope, applicability, authority, relationships, retrieval, enforcement and evidence in stages; governance: the decision gains force only when the system can resolve and apply it.

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 39 (directness 8, rhythm 8, trust 8, authenticity 7, density 8) |
| `lint_prose.py` | 0 errors, 0 warnings |
| Cold read: thesis as restated | "An ADR is only text to a coding agent; it becomes an enforceable governed decision only after it gains lifecycle, scope, authority, precedence, retrieval, enforcement and evidence, and each missing stage causes a specific agent failure." Matches. |
| Cold read: unclear terms, and how resolved | Decision Index, hooks, typed rules, provenance and the snapshot jargon glossed; unsupported generalisations ("most teams stop at stage 0 or 1", "a few dozen decisions") rewritten; the authority stage reconciled with the index storing no approver name. |

## Agreed scope

### 1. Concept: Engineering Decision Governance (P0)

- **Definition:** use ADR-031's three questions (effective resolution, governance change, evidence identity; see the build card). The chat's own wording ("the system for determining which engineering decisions have authority, where and when they apply, how conflicts are resolved, how decisions may change, and how their application is enforced and evidenced") is background only; where it differs from ADR-031, ADR-031 wins. Governance is about force, not storage.
- **Audience:** Staff+ engineers, architects, platform engineering, enterprise architecture, CTOs, engineering governance teams.
- **Sections:** definition; why decision records are insufficient; properties of a governed decision (identity, statement, scope, applicability, authority, provenance, lifecycle, precedence, exceptions, enforcement potential, evidence); the six governance questions; vs adjacent concepts (ADR management, architecture governance, AI governance, policy-as-code, decision intelligence); documentation → operational governance chain; same model for humans, agents, CI and software factories; restrained Mneme fit.
- **Key graphic:** "Anatomy of a governed engineering decision", reusable.
- **Section added 2026-10-14: why decisions become the scarce asset.** The thesis of the Cohesion chat's dropped insight 3 (as implementation gets cheaper, the durable asset is the decision context needed to produce the right implementation) lives here as one section, linking the shipped articles that already argue it (`ai-makes-software-more-ambitious`, `ai-roi-problem-is-about-systems-not-models`) rather than restating them.
- **Relationships to existing concepts (state and link):** ADR-031's *effective resolution* includes precedence, so this page is the umbrella over `concepts/precedence-semantics` and `concepts/decision-continuity`, and over the Engineering Coherence concept as the outcome decision governance protects. The `find_overlap.py` screen puts `precedence-semantics` at 30.4; link down to it rather than redefine it.
- **Avoid:** implying Mneme invented the term; product pitch. CTA: how Mneme models decisions (docs).

### 2. Insight: Why AI Software Factories Need Decision Governance (P0 in chat)

Thesis: when production speeds up, human review cannot remain the mechanism by which engineering intent keeps force. Opens on the Entrepreneur/HBR claim that products taking years now take weeks. Failure modes: locally correct changes violating system intent; decisions applied outside scope; obsolete decisions still applied; conflicting instructions; decisions lost between systems; controls disconnected from their decision. Close: "Software factories scale code generation. Decision governance ensures engineering intent still has force." CTA: Architecture Audit or design-partner conversation. **See verdict: merge into `software-factory-governance-layer`.**

### 3. Technical insight: From Decision Records to Decision Governance (P1)

One ADR ("ADR-042: Use PostgreSQL for transactional persistence") gains semantics stage by stage: record → lifecycle (status, supersedes) → scope (repository, paths) → applicability (operation) → authority and provenance → relationships and precedence → retrieval for a task → enforcement (decision ≠ rule; one decision may yield several rules, some none) → evidence. Key graphic: one ADR gaining operational semantics. CTA: docs / GitHub.

### Vocabulary the chat wants locked

Decision Engineering (discipline), Decision Governance (what has force), Decision Index (resolves and relates), Decision Enforcement, Decision Evidence, Decision Infrastructure (systems that carry it). Each is a terminology-lock decision.

## Key facts, figures, sources

| Claim | Source | Verified? |
|---|---|---|
| IBM wrote about decision governance years ago (enterprise decision management) | https://www.redbooks.ibm.com/redbooks/pdfs/sg248127.pdf | not used (the insight cites no external sources) |
| AsDecided article "Decision Governance for Coding Agents" defines it around authority, applicability, delivery and deterministic checks | https://asdecided.com/articles/decision-governance-for-coding-agents | not used |
| Gartner includes decision governance within Decision Intelligence platforms | **no URL in chat** | not used |
| SAS argues in 2026 that decisions should be first-class governed assets | **no URL in chat** | not used |
| Other new projects use "decision governance for code and the agents editing it" | **no URL in chat** | not used |
| Entrepreneur/HBR post on AI-native startups shipping in weeks | image only, **no URL** | not used |

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Decision model with scope and lifecycle, deterministic enforcement | SHIPPED (verify fields: authority, precedence) |
| Decision Index | SHIPPED (OSS, mneme-hq 0.10.0: canonical Decision Index persistence; the Decision MCP reads it). Cross-system ingestion is PLANNED; ADR-031 governance semantics are accepted but unreleased |
| Decision discovery and cross-system ingestion | Discovery: Research harness SHIPPED as research-only (`mneme research open-architecture`, O1A benchmark harness in 0.10.0); results not validated, experiment in progress. Confluence ADR ingestion: PLANNED (site roadmap). Jira, Slack, Teams and telemetry connectors: CONCEPTUAL (the core roadmap plans a source-independent ingestion contract and warns against assuming such connectors) |
| "Mneme is building the decision and control infrastructure" | CONCEPTUAL/PLANNED voice; keep it that way |

## Positioning constraints

- Category ambition in the chat ("Decision Governance as the missing name for the layer"; architecture as one class of decisions, not the ceiling) is a positioning change: ADR route before copy.
- Don't publish a generic "What is Decision Governance?" (large fuzzy space); stay on engineering decisions.
- ADR-017 and other ADR numbers are public in MnemeHQ/mneme; explain the idea rather than citing a bare number. O1 is internal shorthand; keep it out of copy.

## Non-insight site edits requested

- Add Decision Governance as a named concept in the site taxonomy (concept contract).

## Open questions

- Adopted 2026-10-12: "engineering decision governance" (meaning from ADR-031). Still to settle in the PUBLISHING.md amendment: how it sits beside the locked "decision layer" and "decision corpus" (the corpus is what is governed; decision governance is how the effective subset is resolved).
- Is merging the software-factory insight into the existing pillar acceptable?
