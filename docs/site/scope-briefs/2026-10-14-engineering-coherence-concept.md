# Scope brief: Engineering Coherence (concept page)

Status: **scoped, not built**; waits on the terminology amendment (see below)

| Field | Value |
|---|---|
| Source | Derived from the [Cohesion and Reddit thread brief](2026-10-04-cohesion-and-reddit-thread.md) (its concept scope and its foundational insight), per the owner's decision of 2026-10-14 |
| Kind | **concept page** under `/concepts/` (concept publication runbook, `docs/site/concept-publication.md`; separate PR from insights) |
| Repo check | No concept page defines coherence. The term is already used in shipped copy: `concepts/architectural-drift` defines drift as "the compound degradation in codebase coherence" (13 mentions); `concepts/architectural-governance` (6), `concepts/governance-infrastructure` (5), `concepts/decision-continuity` (3); insights `ai-makes-software-more-ambitious` (11) and `agent-governance-in-the-sdlc` (11). |

## Decision (2026-10-14, TheoV823)

"Coherence" and "decisions" are the two terms Mneme needs to own. Each gets **one canonical concept page** that defines it, and articles support and link to it rather than restating it.

This reverses the 2026-10-12 decision of "no Engineering Coherence concept page". "The Coherence Problem in Agentic Software Development" is not published as an article; its definitions become this page's body.

## Build card

| Field | Value |
|---|---|
| Title | Engineering Coherence (abstraction-first name, per PUBLISHING.md "Conceptual authority") |
| Slug | `concepts/engineering-coherence` |
| Schema | `DefinedTerm` JSON-LD; card and `hasPart` entry on `site/concepts/index.html` |
| Section on the concepts hub | the drift / architectural governance group, next to `architectural-drift` |
| OG headline | Correct Code, Incoherent System (4 words) |
| Length | 1,000 words or more (concept floor); consider flagship treatment later |
| Terminology lock | **Required first:** a PUBLISHING.md amendment admitting "engineering coherence" as a concept term (not category or tagline language, so no ADR-001/013/014 change), stating its relation to "drift" (drift = the degradation of coherence) |
| Cannibalisation | `find_overlap.py` "Engineering Coherence": top 20.9 (`prompt-engineering-vs-harness-engineering`, lexical noise). Body search: see Repo check. Verdict: **clear as the defining page**, provided it links to and is linked from the pages above |
| Contrast claim (required for concepts) | "Local correctness is not system coherence: a change can compile, pass its tests and satisfy its ticket while making the system less coherent." |

## Agreed scope

- **Definition:** engineering coherence is the extent to which independently executed software changes remain consistent with the technical decisions, boundaries, constraints and assumptions that govern a system. The key word is *independently*.
- **What must stay coherent:** service and module boundaries, dependency direction, ownership, interfaces and contracts, data access, security constraints, approved patterns and technologies, lifecycle state, exceptions. Not code style.
- **How it breaks:** shared intent → fragmented context → independent execution → divergent implementation. AI lowers the cost of independent execution, so this happens faster.
- **Five dimensions:** decision, context, structural, temporal and execution coherence.
- **Relationships (state each explicitly and link):**
  - **Architectural drift** is the degradation of coherence over time (consistent with `concepts/architectural-drift`).
  - **Architectural conformance** is one way to test coherence, not the whole of it.
  - **Shared mental models** are how human teams traditionally kept coherence; they do not scale to many independent agents.
  - **Decision governance** (its own concept page) is the mechanism that keeps independently executed changes on the same decisions.
- **What preserves it:** conversation → documentation → addressable decisions → contextual retrieval → deterministic enforcement → evidence.
- **Is not:** code consistency, architectural purity, identical choices, removing autonomy, broad organisational alignment, generic AI governance.
- **Mneme fit (restrained, end of page):** Mneme carries authoritative technical decisions into independent execution; it does not "create" coherence.

## Supporting pages

| Page | Action |
|---|---|
| `ai-makes-software-more-ambitious` (shipped) | light refresh: link to this page where it says changes must stay coherent; no rewrite |
| `agent-governance-in-the-sdlc` (shipped) | light refresh: link at first use of "coherence" |
| `concepts/architectural-drift` | link to this page from its definition of drift |
| The Return of the Silo Engineer (insight, Cohesion brief) | links here as the problem it illustrates |
| EY article | links here and to the decision-governance concept |

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Mneme retrieves applicable decisions and enforces encoded constraints on supported surfaces | SHIPPED |
| "Mneme preserves engineering coherence" as a positioning line | CONCEPTUAL; concept-page framing only, not category or tagline copy |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

## Open questions

- None beyond the terminology amendment.
