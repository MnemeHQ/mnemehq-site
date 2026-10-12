# Scope brief: Post-Business Type Comparison and decision governance

Status: **gathered, not built**

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Business Type Comparison and decision governance` |
| Chat id | `6ac593b1-c42c-83ea-bf1c-ee498ee4393c` (project `g-p-69fb157536408191b03a29c6f51f7821`) |
| Created / last updated (UTC) | 2026-10-07 / 2026-10-07 |
| Shape | 3 turns: "Are we [this] type of business" (an image of an Entrepreneur/HBR post about AI-native startups), "Decision governance: a concept we need to write about?", then "Scope them" (concept page plus two insights). |
| Repo check | No concept page or insight on decision governance. The phrase already appears in product copy: `compare/sourcegraph-cody` ("Codebase Context vs Decision Governance") and `integrations/kiro`. |

## Build card

**Decision 2026-10-12:** "engineering decision governance" is the one new concept term. Before the concept page ships: a PUBLISHING.md terminology amendment and an ADR-001/013/014 check in `MnemeHQ/mneme`. Only "decision governance" is adopted; the rest of the chat's vocabulary (Decision Engineering, Decision Infrastructure, Decision Enforcement, Decision Evidence) is not locked.

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
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

## Agreed scope

### 1. Concept: Engineering Decision Governance (P0)

- **Definition (chat):** "Engineering decision governance is the system for determining which engineering decisions have authority, where and when they apply, how conflicts are resolved, how decisions may change, and how their application is enforced and evidenced." Governance is about force, not storage.
- **Audience:** Staff+ engineers, architects, platform engineering, enterprise architecture, CTOs, engineering governance teams.
- **Sections:** definition; why decision records are insufficient; properties of a governed decision (identity, statement, scope, applicability, authority, provenance, lifecycle, precedence, exceptions, enforcement potential, evidence); the six governance questions; vs adjacent concepts (ADR management, architecture governance, AI governance, policy-as-code, decision intelligence); documentation → operational governance chain; same model for humans, agents, CI and software factories; restrained Mneme fit.
- **Key graphic:** "Anatomy of a governed engineering decision", reusable.
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
| IBM wrote about decision governance years ago (enterprise decision management) | https://www.redbooks.ibm.com/redbooks/pdfs/sg248127.pdf | no |
| AsDecided article "Decision Governance for Coding Agents" defines it around authority, applicability, delivery and deterministic checks | https://asdecided.com/articles/decision-governance-for-coding-agents | no |
| Gartner includes decision governance within Decision Intelligence platforms | **no URL in chat** | no |
| SAS argues in 2026 that decisions should be first-class governed assets | **no URL in chat** | no |
| Other new projects use "decision governance for code and the agents editing it" | **no URL in chat** | no |
| Entrepreneur/HBR post on AI-native startups shipping in weeks | image only, **no URL** | no |

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Decision model with scope and lifecycle, deterministic enforcement | SHIPPED (verify fields: authority, precedence) |
| Decision Index, discovery/ingestion (O1, data engine, Confluence/Jira/Slack) | PLANNED / VALIDATED EXPERIMENT |
| "Mneme is building the decision and control infrastructure" | CONCEPTUAL/PLANNED voice; keep it that way |

## Positioning constraints

- Category ambition in the chat ("Decision Governance as the missing name for the layer"; architecture as one class of decisions, not the ceiling) is a positioning change: ADR route before copy.
- Don't publish a generic "What is Decision Governance?" (large fuzzy space); stay on engineering decisions.
- Do not cite internal ADR-017 or O1 in public copy.

## Non-insight site edits requested

- Add Decision Governance as a named concept in the site taxonomy (concept contract).

## Open questions

- Terminology: adopt "engineering decision governance" alongside or instead of "decision layer" / "decision corpus" (current lock)? It competes with "engineering coherence" (Cohesion chat) and "pre-action governance" (09-08 brief).
- Is merging the software-factory insight into the existing pillar acceptable?
