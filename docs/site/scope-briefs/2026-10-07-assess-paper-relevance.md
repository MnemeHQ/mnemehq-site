# Scope brief: Post-Assess paper relevance

Status: **built 2026-10-14** in the batch 2 PR (not yet merged or deployed) as `/insights/multi-agent-coding-shared-context/`

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Assess paper relevance` |
| Created / last updated (UTC) | 2026-10-07 / 2026-10-07 |
| Shape | 2 turns: paper assessment (AECP, arXiv 2610.06481), then "Scope article". The scope did not change between turns. |
| Repo check | No page mentions AECP or arXiv 2610.06481. Not shipped. |

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | Multi-Agent Coding Needs More Than Shared Context (chat's choice; see report-anchored row) |
| Slug | `multi-agent-coding-shared-context` (chat: `/insights/multi-agent-coding-shared-context`) |
| Report-anchored (ADR-015) | **no** (decided 2026-10-14): the paper is evidence for a broader argument, not the article's subject. Keep the evergreen title; name AECP and AWS AI Labs in the meta description and the first lines of the lede |
| Topic hub | agent-infrastructure (decided 2026-10-14; where `coordination-governance-multi-agent-systems` sits) |
| Content type (`--type`) | **Research** (changed at build, 2026-10-14: the meta description, lede and most sections are about the AECP preprint, so the paper is the primary object; the Opus audit flagged Analysis as indefensible under the contract). Also carded on `/insights/research/` |
| OG headline | Shared Context Won't Coordinate Agents (5 words) |
| Editorial gate | pass: named-paper entry point plus new evidence (controlled experiment on coordination protocols) |
| Five questions | changed: a controlled study shows structured, scoped artifacts beat free-form agent chat; matters: multi-agent coding is moving into production; breaks: agents miss, misread or outlive each other's findings and contracts; do: turn findings and interface agreements into scoped state the harness acts on; governance: runtime agreements still are not organisational decisions, which need authority, lifecycle and precedence |
| Cannibalisation | `find_overlap.py`: `concepts/multi-agent-architectural-drift` 62.8, `ai-agent-orchestration-is-not-governance` 49.0, `coordination-governance-multi-agent-systems` 48.2, `concepts/multi-agent-continuity` 45.8, `antigravity-solves-coordination-not-governance` 43.0. Verdict: **re-angle**: the new angle is "structured artifacts with applicability vs shared context", evidenced by AECP; link all five, and keep "coordination governance" claims to a link rather than restating them |
| Cross-links | the five pages above, `why-context-alone-doesnt-prevent-architectural-drift`, `software-factory-governance-layer` |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 38 (directness 8, rhythm 7, trust 8, authenticity 7, density 8) |
| `lint_prose.py` | 0 errors, 0 warnings |
| Cold read: thesis as restated | "Agent teams fail from coordination, not coding ability; structured, scoped, harness-verified artifacts beat shared context, but runtime agreements are not organisational architectural decisions." Matches. |
| Cold read: unclear terms, and how resolved | Execution harness and the three benchmarks glossed; the absolute shared-context claim softened; "AECP shows it holds for teams" reworded; the 18.6% given its absolute figures; supported agents named. |

## Agreed scope

- **Thesis:** as coding agents move from individual workers to teams, the problem shifts from giving agents more context to deciding which information must become structured, scoped, actionable state. Then one step beyond the paper: runtime coordination is still not organisational governance.
- **Progression to show:** context → structured artifacts → applicability → deterministic action → evidence.
- **Audience:** CTOs, platform engineers, software architects, AI engineering leads, people building agent harnesses.
- **SEO:** primary "multi-agent coding"; secondary: multi-agent coding agents, AI agent communication, agent coordination, coding agent orchestration, multi-agent software development, agent contracts, AI coding governance. Informational, emerging-category intent.
- **Structure (from the chat):**
  1. Open on the AECP result, not Mneme: more agents add capacity and more chances to disagree.
  2. Shared context is a weak coordination mechanism. Reusable diagram: information exists ≠ agent sees it ≠ understands it ≠ follows it ≠ system verifies it.
  3. AECP turns communication into artifacts: Knowledge Artifacts (scoped findings, optional executable witness) and Contract Artifacts (interface agreements checked by deterministic static analysis; dependants marked stale on change). The harness becomes an active participant, not a message bus.
  4. Applicability matters more than bigger context windows (component, file, operation, dependency, interface, task intent, lifecycle).
  5. Deterministic checks change the model's role: ask "does this implementation satisfy the agreement?", not "did the agent remember it?".
  6. Runtime agreements are not architectural decisions: example "CustomerService exposes method X" vs "services in domain Y communicate asynchronously except approved adapters". Durable decisions need authority, applicability, lifecycle, precedence, provenance, enforcement, exceptions, evidence.
  7. A layered architecture: organisational knowledge → durable decisions → applicable decisions → agents → runtime findings and agreements → deterministic enforcement → evidence. Rule: do not auto-promote agent agreements into organisational memory; promotion needs authority and provenance.
  8. Software factories make this a governance problem.
  9. Four conclusions; close with a restrained Mneme bridge. CTA: decision model docs; secondary: GitHub.
- **Later, separate:** a short research note targeting "AECP artifact-exclusive communication protocol" if search volume appears, linking here.

## Key facts, figures, sources

**Verified 2026-10-14** against arXiv 2610.06481 v1 (no v2): abstract page and full HTML. Title: "AECP: Artifact-Exclusive Communication Protocol for Multi-Agent Code Generation"; five models (Claude Opus 4.8, Opus 4.6, Sonnet 5, DeepSeek-V4-Flash, GLM-5.2); authors at AWS AI Labs, first author at the University of Central Florida during an AWS internship.

| Claim | Source | Verified? |
|---|---|---|
| AECP replaces free-form agent messages with Knowledge Artifacts and Contract Artifacts; harness injects artifacts on matching code access; checks fire on tool interactions | https://arxiv.org/html/2610.06481 | verified |
| 28.2% **relative** improvement in test-pass score and 16.5% lower wall-clock time vs free-form communication, across five models and three repo-generation benchmarks | same | verified |
| vs a centralised integration architecture: +8.5% score, -24.9% runtime | same | verified |
| ~46% more tokens than a single agent | same | verified |
| 26.8% of tokens on repeated exploration, 22.2% on rework from incompatible decisions at module boundaries | same | verified |
| 0/20 malicious-message propagation vs 19/20 reaching another worker and 8/20 adopted in free-form; authors attribute it to removing the free-form channel and did not test malicious artifacts | same | verified |
| Single agent faster and better on easy tasks; adaptive team sizing cut runtime 18.6% without lowering score; leader chose one worker for 39 of 104 tasks | same | verified |
| Authors are AWS AI Labs; arXiv v1 submitted 2026-10-05; not peer reviewed | same | verified |

Carry over the chat's cautions: report 28.2% as relative, not percentage points; the security result is about one removed attack surface, not general security; label it a preprint.

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Deterministic enforcement at tool/write seams for supported integrations | SHIPPED on supported native write paths (verify against the current release's documented behaviour (mneme-hq 0.10.0 release notes and docs)) |
| Applicability-scoped retrieval of decisions | SHIPPED for repository decisions (verify scope) |
| Decision Index with lifecycle, supersession and provenance | SHIPPED (OSS, mneme-hq 0.10.0: canonical Decision Index persistence; the Decision MCP reads it). Cross-system ingestion is PLANNED; ADR-031 governance semantics are accepted but unreleased |
| Runtime-artifact layer with promotion into governed decisions | CONCEPTUAL |
| Enterprise ingestion (Confluence, Jira) | Confluence ADR ingestion: PLANNED (site roadmap). Jira, Slack, Teams and telemetry connectors: CONCEPTUAL (the core roadmap plans a source-independent ingestion contract and warns against assuming such connectors) |

## Positioning constraints

- Treat AECP as validation, not a competitor: it is a coordination protocol inside one execution; Mneme targets decisions across executions.
- ADR numbers (ADR-023, ADR-024, ADR-029 and others) are public in MnemeHQ/mneme, but explain the idea in plain words rather than citing a bare number. O1 is internal shorthand; keep it out of copy.
- "Mneme is being built around that second layer" must stay PLANNED-voiced.
- Governance should work the same for human, single agent, agent team and software factory: do not position Mneme as an orchestrator.

## Non-insight site edits requested

None. (The chat suggests an entry in the internal research/competitive landscape; not site work.)

## Open questions

- None outstanding (title and hub decided 2026-10-14).
