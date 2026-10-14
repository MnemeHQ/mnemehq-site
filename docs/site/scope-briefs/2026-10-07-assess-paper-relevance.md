# Scope brief: Post-Assess paper relevance

Status: **gathered, not built**; build card decided 2026-10-14, ready to build

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
| Eyebrow / section | Analysis / Engineering |
| OG headline | Shared Context Won't Coordinate Agents (5 words) |
| Editorial gate | pass: named-paper entry point plus new evidence (controlled experiment on coordination protocols) |
| Five questions | changed: a controlled study shows structured, scoped artifacts beat free-form agent chat; matters: multi-agent coding is moving into production; breaks: agents miss, misread or outlive each other's findings and contracts; do: turn findings and interface agreements into scoped state the harness acts on; governance: runtime agreements still are not organisational decisions, which need authority, lifecycle and precedence |
| Cannibalisation | `find_overlap.py`: `concepts/multi-agent-architectural-drift` 62.8, `ai-agent-orchestration-is-not-governance` 49.0, `coordination-governance-multi-agent-systems` 48.2, `concepts/multi-agent-continuity` 45.8, `antigravity-solves-coordination-not-governance` 43.0. Verdict: **re-angle**: the new angle is "structured artifacts with applicability vs shared context", evidenced by AECP; link all five, and keep "coordination governance" claims to a link rather than restating them |
| Cross-links | the five pages above, `why-context-alone-doesnt-prevent-architectural-drift`, `software-factory-governance-layer` |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

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

All from one source; **none verified yet**. Re-read the paper (and check for a v2) before use.

| Claim | Source | Verified? |
|---|---|---|
| AECP replaces free-form agent messages with Knowledge Artifacts and Contract Artifacts; harness injects artifacts on matching code access; checks fire on tool interactions | https://arxiv.org/html/2610.06481 | no |
| 28.2% **relative** improvement in test-pass score and 16.5% lower wall-clock time vs free-form communication, across five models and three repo-generation benchmarks | same | no |
| vs a centralised integration architecture: +8.5% score, -24.9% runtime | same | no |
| ~46% more tokens than a single agent | same | no |
| 26.8% of tokens on repeated exploration, 22.2% on rework from incompatible decisions at module boundaries | same | no |
| 0/20 malicious-message propagation vs 19/20 reaching another worker and 8/20 adopted in free-form; authors attribute it to removing the free-form channel and did not test malicious artifacts | same | no |
| Single agent faster and better on easy tasks; adaptive team sizing cut runtime 18.6% without lowering score; leader chose one worker for 39 of 104 tasks | same | no |
| Authors are AWS AI Labs; arXiv v1 submitted 2026-10-05; not peer reviewed | same | no |

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
