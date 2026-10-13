# Scope brief: Post- Cohesion And Reddit Thread

Status: **gathered, not built**; insight 1 ready, insights 2 and 3 blocked on overlap (owner decision)

| Field | Value |
|---|---|
| ChatGPT chat | `Post- Cohesion And Reddit Thread` |
| Created / last updated (UTC) | 2026-10-04 / 2026-10-04 |
| Shape | 7 turns: Reddit thread assessment, a draft Reddit comment, "write about silos?" plus emerging themes, "Scope coherent", "topic or concept?", "Scope the concept", "Scope the 3 insights". The first two turns do not render in the ChatGPT page; read via the API. |
| Repo check | Body search (2026-10-12, after the #209 audit): **coherence is already argued** by `ai-makes-software-more-ambitious` (published 2026-07-27; 11 mentions; "keeping hundreds of agent-made changes coherent becomes the harder problem"; "Writing code becomes cheaper. Maintaining architectural coherence does not.") and `agent-governance-in-the-sdlc` (11 mentions). The "code is cheap, X is scarce" line appears in 10+ shipped articles (e.g. `ai-roi-problem-is-about-systems-not-models`, `ai-coding-agent-verification-tax`). Silos: only `agent-formation-engineering-performance-metrics` mentions them (a study finding); no "silo engineer" piece exists. |

## Build card

**Decisions 2026-10-12:** no Engineering Coherence concept page; "coherence" stays a problem framing inside insights. Insight 1 absorbs the 09-12 decision-silos brief as one section. Insight 3 was to own the "cheap code, scarce decisions" thesis (EY linking to it).

**Overlap found after those decisions (#209 audit, confirmed by body search):** insights 2 and 3 would largely duplicate shipped articles. Both are **blocked** until the owner decides, for each: drop, re-angle to a claim the shipped pages do not make, or update `ai-makes-software-more-ambitious` instead. Insight 1 is unaffected.

| Piece | Kind | Slug | Hub | OG headline | Cannibalisation (`find_overlap.py`) | Verdict |
|---|---|---|---|---|---|---|
| Engineering Coherence | ~~concept page~~ | n/a | n/a | n/a | top 24.4 | **dropped** (decision 2026-10-12) |
| The Return of the Silo Engineer | insight | `return-of-the-silo-engineer` | engineering-performance | The Return of the Silo Engineer (5) | title screen: top 40.7 `ai-engineering-roi` (noise on "engineer"); body search: no silo-engineer piece | clear; **absorbs the 2026-09-12 decision-silos brief as one section**; link `ai-makes-software-more-ambitious` |
| The Coherence Problem in Agentic Software Development | insight (foundational) | `coherence-problem-agentic-software-development` | architectural-governance | Correct Code, Incoherent System (4) | title screen: `concepts/agentic-development` 40.6; **body search: `ai-makes-software-more-ambitious`, `agent-governance-in-the-sdlc`** | **blocked: owner decision** (drop / re-angle / update the shipped page) |
| When Code Becomes Cheap, Decisions Become the Scarce Asset | insight (strategic) | `when-code-is-cheap-decisions-are-scarce` | architectural-intent | Cheap Code, Scarce Decisions (4) | title screen: top 19.3; **body search: thesis in 10+ shipped articles** | **blocked: owner decision** (drop / re-angle) |

Report-anchored: no. Eyebrows: Concept / Analysis.

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

## Agreed scope

### Concept: Engineering Coherence

- **Definition (chat):** "Engineering coherence is the extent to which independently executed software changes remain consistent with the technical decisions, boundaries, constraints, and assumptions that govern a system." The key word is *independently*.
- **What must stay coherent:** service and module boundaries, dependency direction, ownership, interfaces and contracts, data access, security constraints, approved patterns and technologies, lifecycle state, exceptions. Not code style.
- **What breaks it:** divergence between actors: shared intent → fragmented context → independent execution → divergent implementation. AI lowers the cost of independent execution.
- **Central principle:** local correctness does not imply system coherence (a change can compile, pass tests and satisfy the ticket while reducing coherence).
- **What preserves it:** conversation → documentation → addressable decisions → contextual retrieval → deterministic enforcement → evidence.
- **Is not:** code consistency, architectural purity, identical choices, eliminating autonomy, broad organisational alignment, generic AI governance, mere conformance. Conformance is one mechanism; drift is one failure mode; shared mental models are one traditional mechanism.
- **Five dimensions:** decision, context, structural, temporal, execution coherence. The chat maps Mneme onto each but says to keep that mapping out of the definition.
- **Scope v1:** technical decisions governing software systems only.

### Insight 1: The Return of the Silo Engineer (symptom)

AI makes independent execution so cheap that teams recreate the silo problem at higher speed: a developer-agent unit produces substantial changes before the team shares an understanding of them. Sequence: more individual capacity → fewer coordination points → less architectural knowledge exchanged → local context dominates → divergence found late. Examples: two engineers solving one problem two ways; an agent adding a dependency without knowing why it was rejected. Not "developers are antisocial" or remote-work commentary. Ending: keep what old coordination transmitted, not its cost. Best for LinkedIn and Reddit distribution.

### Insight 2: The Coherence Problem in Agentic Software Development (foundational)

As changes become independent and autonomous, producing correct changes and keeping a coherent system become separate problems. Introduces the concept; explains why bounded-context agents amplify it; mechanisms: shared intent → explicit decisions → applicability → authority → lifecycle → enforcement where appropriate → evidence; distinguishes drift, conformance, shared mental models and agent guardrails. Mneme only near the end.

### Insight 3: When Code Becomes Cheap, Decisions Become the Scarce Asset (strategic)

Implementation cost falls; the value of knowing what to build, which constraints hold and why rises. Code is not worthless; relative value moves upward. Decisions sit badly across ADRs, Slack, tickets, PRs, docs and memory. "If implementation becomes reproducible, the durable asset becomes the decision context needed to reproduce the right implementation." Closes on software factories.

Order: silo → coherence → scarce decisions (symptom → problem → consequence), as a mini-series.

### Other themes the chat listed (not scoped)

Implementation abundance / coordination scarcity; verification moving earlier; shared mental models don't scale to agents; decision authority rises with autonomy; AI reviewing AI is not independent verification; comprehension debt; intent has to travel; software factories need a constitution, not just a harness. Umbrella proposed: keeping an autonomous engineering organisation coherent.

## Key facts, figures, sources

| Claim | Source | Verified? |
|---|---|---|
| r/ExperiencedDevs thread: developers overwhelmed by generated code and reduced collaboration; commenters ask for decisions before agents execute, call out architecture drift, siloing, an explicit owner for architectural decisions, and agent-approves-agent PRs | https://www.reddit.com/r/ExperiencedDevs/s/1DwHX4SXAW (share link; resolve to the canonical thread URL) | no |
| Individual comment citations | ChatGPT internal references only, **no URLs** | no |

Reddit is anecdotal (it shows the pain in practitioners' own words; it is not market validation). Quote paraphrased, not verbatim, unless the comment is re-read and attributed.

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Decision model, applicability/retrieval, typed rules and enforcement via agent hooks and CI | SHIPPED on supported surfaces (verify each). The Decision MCP proposes and reads decisions; it does not enforce |
| Lifecycle/precedence, evidence | verify; parts PLANNED |
| "Mneme helps organisations preserve engineering coherence as execution becomes autonomous" | positioning statement: CONCEPTUAL until adopted |

## Positioning constraints

- Agree with the thread's pro-collaboration commenters; do not position Mneme as a replacement for collaboration. The chat's line: "Collaboration is how teams create and change architectural intent. Mneme is how that intent continues to govern work when implementation scales beyond the conversations that created it." It reads as a pull-quote, which stop-slop flags; paraphrase it in the article.
- Out of scope: AI safety, agent permissions/sandboxing, whether AI code is good, generic collaboration advice, management silos.
- "Coherence" as broader positioning than drift prevention is a positioning change: ADR route.

## Non-insight site edits requested

- None for the site (the Engineering Coherence concept page was dropped on 2026-10-12).
- Social, not site: the drafted Reddit comment (do not post from this workflow).

## Open questions

- **Open (owner):** insights 2 and 3 overlap shipped articles (see the build card). Drop, re-angle, or update `ai-makes-software-more-ambitious` instead?
- Resolved 2026-10-12: "engineering coherence" is a framing used in these insights, not a concept page; the 2026-09-12 silo scope folds into insight 1 as one section.
