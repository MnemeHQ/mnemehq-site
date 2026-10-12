# Scope brief: post-reverse engineer decisions

Status: **gathered, not built**

| Field | Value |
|---|---|
| ChatGPT chat | `post-reverse engineer decisions` (lowercase prefix) |
| Chat id | `6acd16bd-59a8-83e9-9a61-76438c12fd84` (project `g-p-69fb157536408191b03a29c6f51f7821`) |
| Created / last updated (UTC) | 2026-10-12 / 2026-10-12 |
| Shape | 2 user turns: a pasted research-topic proposal followed by "scope" (answered with a full research scope brief), then an arXiv paper to assess (architecture erosion mapping study). The second turn refines the scope. |
| Repo check | No page covers enterprise system reverse engineering, architecture recovery or erosion. "Erosion" appears only in passing on a few pages (e.g. `concepts/ai-native-sdlc`, `ai-coding-agent-guardrails`). |

## Build card

| Field | Value |
|---|---|
| Kind | **research scope, not an insight.** The chat asks for an internal research programme and a bounded first experiment. Website output comes after results, as a research page under the planned `/research/open-architecture/` (see the [Open Architecture brief](2026-10-09-open-architecture-page-assessment.md)) |
| Website working title (later) | Can AI Agents Understand an Enterprise System Before Acting on It? |
| Research title | Reverse-Engineering Enterprise Systems for AI Agents: From Architectural and Functional Blueprints to Decision Governance |
| Slug (later) | `research/open-architecture/enterprise-system-understanding` (proposed) |
| Editorial gate | not yet: nothing publishable until the first experiment has results. Publishing the scope alone would be a claim without evidence |
| Cannibalisation | `find_overlap.py`: `why-ai-coding-agents-copy-legacy-architecture` 49.6, `forward-deployed-engineers-enterprise-ai` 45.4, `demo/legacy-vs-target-architecture` 30.9. Verdict for the later research page: **re-angle**: system understanding before acting, not migration drift; link those pages |
| Possible insight spin-off | "architecture erosion vs architectural drift", grounded in the 2022 mapping study. `find_overlap.py`: the drift concept pages score 42.5. Verdict: **update instead**: add an erosion distinction to `concepts/architectural-drift`. "Erosion" is not in the terminology lock: needs a PUBLISHING.md amendment if used as a defined term |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

## Agreed scope

- **Origin:** a prospective enterprise user asked whether agents can work safely on systems nobody fully documented. The chat treats that as a candidate design-partner experiment.
- **Central question:** can we reconstruct an enterprise system's technical architecture, business functionality and governing decisions from existing evidence, so that AI agents can understand and operate within it more safely?
- **Hypothesis:** a structured, evidence-backed representation improves an agent's ability to reason about and modify the system compared with repository context or document retrieval alone.
- **Three layers:**
  1. Architectural blueprint: components, dependencies, interfaces, data stores, topology, ownership boundaries, communication paths, constraints. Distinguish observed facts, inferred relationships and human-confirmed architecture.
  2. Functional blueprint: capabilities, workflows, APIs, state transitions, events, business rules, data flows (e.g. "order submitted → payment authorised → inventory reserved → fulfilment initiated", not "service A calls service B").
  3. Decision layer: decisions with statement, scope, evidence, provenance, confidence, authority, lifecycle, relationships and linked system entities. This is the Mneme connection.
- **Research questions:** RQ1 architecture recovery; RQ2 functional recovery; RQ3 decision recovery; RQ4 agent usefulness, comparing (A) repository context only, (B) RAG, (C) architectural + functional blueprint, (D) blueprint + governing decisions, on realistic tasks.
- **First experiment:** one bounded real system with several components, one meaningful workflow, history and identifiable decisions. Stages: evidence ingestion (Git, ADRs/Markdown, static analysis, issue history, selected architecture docs; Slack, Confluence, cloud and telemetry later) → architecture reconstruction → functional reconstruction → decision reconstruction → agent evaluation with and without the Mneme-derived representation.
- **Evaluation:** reconstruction quality (entity and relationship precision/recall, workflow accuracy, decision discovery precision/recall, evidence correctness, provenance completeness); agent performance (task completion, impact identification, architectural and decision compliance, unsafe-change rate, unnecessary escalation, uncertainty recognition); human usefulness (does it cut time to understand the system; would an engineer trust an agent more with it).
- **Success criterion:** for one bounded real system, Mneme reconstructs a useful architectural view, recovers at least one meaningful workflow, connects both to evidence-backed decisions, and measurably improves an agent's reasoning about a change.
- **Out of scope:** reconstructing a whole enterprise, guaranteed recovery of every decision, replacing architects, a universal enterprise knowledge graph, autonomous enforcement of inferred decisions, exhaustive ingestion. Inferred knowledge stays distinguishable from authoritative knowledge; an inferred decision becomes governable only after validation or authority.
- **Refinement from the paper (turn 2):** separate three questions: architecture recovery (what exists), conformance/drift (does it depart from the approved architecture), erosion (is it deteriorating over time). A single violation is not erosion; an approved migration is not damage, so lifecycle, supersession and authority semantics matter. Build one common model of observed state, intended state, applicable decisions and evidence, then separate analyses, rather than two drift engines. Test the case where the intended architecture is undocumented, contradictory or outdated.
- **Proposed work packages:** observed architecture reconstruction and provenance (P0); intended architecture and decision authority representation (P0); structural conformance and longitudinal erosion metrics (P1); functional workflows and operational-agent evaluation (P1).
- **Positioning line from the chat:** first understand the system, then determine which decisions govern it, then verify that agent actions respect those decisions.

## Key facts, figures, sources

**None verified.**

| Claim | Source | Verified? |
|---|---|---|
| Li, Liang, Soliman & Avgeriou (2022), "Understanding Software Architecture Erosion: A Systematic Mapping Study", Journal of Software: Evolution and Process; reviews 73 studies (literature up to May 2019) | https://arxiv.org/abs/2112.10934 (PDF: https://arxiv.org/pdf/2112.10934) | no |
| Distinguishes implemented vs currently intended architecture; erosion as structural degradation or growing resistance to change | same | no |
| Knowledge vaporization is the most-mentioned nontechnical cause (11 of 73 studies) | same | no |
| Recommends recording and tracing architectural knowledge (decisions, assumptions) to code and changes | same | no |
| Reviews tools including ARCADE, Lattix, Structure101, Axivion, Sonargraph | same | no |
| A September 2026 study on recovering architectural decisions from commits finds LLMs often miss the rationale | https://arxiv.org/abs/2609.03721 | no |
| A 2025 systematic mapping study on mining repositories to recover software architecture | ScienceDirect, **URL not captured** | no |
| Research on deriving business-process event logs from legacy code and database activity | Springer, **URL not captured** | no |

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Data engine ingesting repositories, docs, ADRs, static analysis | VALIDATED EXPERIMENT at most; confirm |
| Jira, Confluence, Slack/Teams, cloud, telemetry ingestion | PLANNED |
| O1 evaluating entity discovery, relationships, decision recovery | VALIDATED EXPERIMENT / in progress |
| Decision Index with authority, lifecycle, provenance | PLANNED |
| Mneme Core retrieves and deterministically enforces reviewed constraints | SHIPPED |
| Architecture, functional and decision reconstruction for enterprise systems | CONCEPTUAL (this is the research question) |

## Positioning constraints

- Do not present dependency analysis, architecture recovery or conformance checking as Mneme inventions; they are established fields (ARCADE, Lattix, Structure101 and others).
- The 2022 paper predates LLM agents; it supports the problem framing, not the proposed capability.
- Keep enterprise-level drift distinct from the current architectural-drift concept rather than stretching that concept; any new term goes through the terminology lock.
- Do not name the prospective user or their organisation in public pages.

## Non-insight site edits requested

None now. Later: a research page and case study under `/research/open-architecture/` once the first experiment has results (same sequencing as the Open Architecture brief).

## Open questions

- Which bounded real system for the first experiment, and does its owner agree to publication of results?
- Where does the research plan itself live (internal research repo or `MnemeHQ/mneme`), given this repository is public?
