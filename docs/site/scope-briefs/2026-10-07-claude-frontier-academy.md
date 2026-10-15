# Scope brief: Post-claude frontier academy Assess program relevance

Status: news piece **published 2026-10-15 in [#221](https://github.com/MnemeHQ/mnemehq-site/pull/221), deployed at `88d8edd9`** as `/insights/claude-frontier-academy-frontier-deployed-engineers/`. Judged still newsworthy on 2026-10-14 (12 days after launch; cohorts running, first badges early 2027). The FDE pillar update shipped in the batch 3 PR, and every other cluster item was merged or dropped on 2026-10-15 (see the verdict table). The chat can be marked once batch 3 is deployed

| Field | Value |
|---|---|
| ChatGPT chat | `Post-claude frontier academy Assess program relevance` |
| Created / last updated (UTC) | 2026-10-07 / 2026-10-07 |
| Shape | 3 turns: programme assessment, "Scope articles" (a 10-article list), then "combine with the FDE cluster, plus one explicit article to target the keyword in the news" (12-article list). The last turn is final. |
| Repo check | No page mentions Claude Frontier Academy or "Frontier Deployed Engineer". The FDE cluster already shipped (#129, #132): `forward-deployed-engineers-enterprise-ai`, `forward-deployed-engineering-ai-sdlc`, `forward-deployed-engineering-architecture`, `fde-coding-agents`, `forward-deployed-architects-need-a-decision-layer`. |

## Build card (the news article; the rest of the list is below)

| Field | Value |
|---|---|
| Kind | insight (news) |
| Title | Claude Frontier Academy: What 10,000 Frontier Deployed Engineers Mean for Enterprise AI |
| Slug | `claude-frontier-academy-frontier-deployed-engineers` (the chat wrote `/articles/...`; insights live under `/insights/`) |
| Report-anchored (ADR-015) | yes: entity = "Claude Frontier Academy" |
| Topic hub | agent-infrastructure (decided 2026-10-14). The FDE cluster pages, which sit on no hub today, move onto it too (separate small site edit) |
| Content type (`--type`) | Analysis (news / launch response) |
| OG headline | Claude Frontier Academy and the Decision Layer (7 words) |
| Editorial gate | pass: named-vendor news entry point; "Claude Frontier Academy", "Frontier Deployed Engineers" and "Anthropic" in the first 150 words |
| Five questions | changed: Anthropic is funding 10,000 deployed engineers to take Claude to production; matters: deployment is industrialising inside consultancies and enterprises; breaks: the judgment that governed a deployment leaves with the engineer; do: make decisions, authority and exceptions survive handover; governance: an organisational decision layer under every agent, not only Claude |
| Cannibalisation | `find_overlap.py`: for "Claude Frontier Academy" alone, top hit `anthropic-claude-marketplace-ai-engineering-control-plane` 45.1 (different announcement). With the full title, `forward-deployed-engineers-enterprise-ai` 90.2 and `forward-deployed-engineering-ai-sdlc` 61.8, matching on "deployed engineer". Verdict: **clear** for the news entity, but keep FDE definitions out and link the FDE pillar instead |
| Cross-links | `forward-deployed-engineers-enterprise-ai`, `forward-deployed-architects-need-a-decision-layer`, `fde-coding-agents`, `anthropic-claude-marketplace-ai-engineering-control-plane` |

## Rest of the chat's cluster: verdicts

| Article (chat priority) | Verdict |
|---|---|
| What Is a Frontier Deployed Engineer? (P0, evergreen FDE pillar) | **done** in the batch 3 PR: `forward-deployed-engineers-enterprise-ai` gains a "From forward deployed to frontier deployed" section |
| The Missing Control Layer in Enterprise AI Deployment (P0) | **dropped** (decided 2026-10-15 (TheoV823)): overlaps `microsoft-agent-forge-enterprise-ai-infrastructure` 57.5 and `enterprise-ai-guardrails-five-layers` 56.8 |
| What Happens After the AI Engineer Leaves? (P0) | **merged** (decided 2026-10-15 (TheoV823)): covered by the FDE pillar's handoff-failure section and the Frontier Academy piece |
| From AI Deployment to AI Governance: What Has to Become Machine-Readable (P1) | **merged**: shipped as `from-decision-records-to-decision-governance` (#221) |
| Why Frontier Deployed Engineers Need a Decision Layer (P1) | **dropped** (decided 2026-10-15 (TheoV823)): same thesis as `forward-deployed-architects-need-a-decision-layer` |
| How to Hand Over an Agentic System Without Losing Its Engineering Intent (P1) | **merged** (decided 2026-10-15 (TheoV823)): with "After the AI Engineer Leaves", covered as above |
| Why AI Agents Need Institutional Memory, Not Just Context Windows (P1) | **dropped** (decided 2026-10-15 (TheoV823)): overlaps `memory-is-not-governance` and `long-context-windows-governance-infrastructure` |
| Why Guardrails Are Not the Same as Governance (P1) | **dropped** (decided 2026-10-15 (TheoV823)): overlaps `enterprise-ai-guardrails-five-layers` and `ai-coding-agent-guardrails` |
| The AI Deployment Stack Is Missing a Decision Plane (P2) | **dropped** (decided 2026-10-15 (TheoV823)): would introduce a new term ("decision plane") under the terminology lock |
| Who Owns a Decision When an AI Agent Writes the Code? (P2) | **dropped** (decided 2026-10-15 (TheoV823)): overlaps `architecture/decision-memory-vs-documentation` 47.1; authority is covered on the decision-governance concept page |
| Why Software Factories Need a Decision Index (P2) | **merged**: the batch 3 PR adds a decision-governance section to `software-factory-governance-layer` |

The chat also proposed a content architecture (pillar "Decision Governance for Agentic Software" with discover / understand / enforce / operate clusters; FDE content in "operate"). That depends on the decision-governance terminology decision.

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 38 (directness 8, rhythm 7, trust 8, authenticity 7, density 8) |
| `lint_prose.py` | 0 errors, 0 warnings |
| Cold read: thesis as restated | "Anthropic's plan scales deployments faster than it scales the way their decisions are recorded, so enterprises need a vendor-independent decision layer that outlives each engineer." Matches. |
| Cold read: unclear terms, and how resolved | The "industrial process" leap and "most live in the engineer's head" rewritten; Anthropic's rationale now quoted; "five of the eight named" made precise; silo glossed. |

## Agreed scope (news article)

1. What is Claude Frontier Academy? (factual)
2. What is a Frontier Deployed Engineer? (short; link the FDE pillar for depth)
3. Why Anthropic is investing in deployed engineers: access to models is no longer the constraint; getting AI into real enterprises is.
4. The governance problem appears after deployment begins: security, architecture, policy, authority, exceptions, handover.
5. What happens when thousands of FDEs deploy agents?
6. The missing layer: organisational decisions (scope, authority, applicability, lifecycle, enforcement).
7. Why this matters beyond Claude (OpenAI, coding agents, software factories, internal agents). Keep Mneme tool-independent.

Publish quickly; news value decays. The chat orders it first, with the FDE pillar update close behind.

## Key facts, figures, sources

**Verified 2026-10-14** against the live Anthropic announcement (headline: "Anthropic invests $100 million to train 10,000 engineers and tackle the enterprise AI talent gap", 2 October 2026). Corrections to the rows below: the programme is a multi-day in-person programme with a simulated deployment "from the right use case through security review to handover" and a graded practical (Claude Resident Engineer badge), then a 12-week residency leading a real Claude use case at the engineer's own organisation, reassessed for the Claude Frontier Deployed Engineer badge (first expected early 2027). The Partner Network and startup-programme rows are not used.

| Claim | Source | Verified? |
|---|---|---|
| Launched 2 October 2026; $100M to train 10,000 Frontier Deployed Engineers by end of 2027 | https://www.anthropic.com/news/claude-frontier-academy | verified |
| First cohorts include Accenture, Bain, Capgemini, Deloitte, McKinsey, Morgan Stanley, Commonwealth Bank, Novo Nordisk | same | verified (see the corrections above) |
| In-person enterprise deployment simulation, then 12 weeks on a real production Claude project; curriculum runs from use-case selection through security review, deployment and handover | same | verified (see the corrections above) |
| Participants return with a named project and lead it to production ("from an idea to a system in production") | same | verified (see the corrections above) |
| Nomination-based; via Anthropic account team or Partner Account Manager; cohorts in San Francisco, New York, London | same | verified (see the corrections above) |
| Claude Partner Network: 40,000+ firms applied; service-partner tiers based on certified engineers and production deployments | https://www.anthropic.com/news/services-track-partner-hub | not used |
| Startup programme open to bootstrapped, pre-seed and venture-backed startups | https://claude.com/programs/startups | not used |

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Deterministic enforcement of repository decisions | SHIPPED on supported native write paths and in CI |
| Decision Index | SHIPPED (OSS, mneme-hq 0.10.0: canonical Decision Index persistence; the Decision MCP reads it). Cross-system ingestion is PLANNED; ADR-031 governance semantics are accepted but unreleased |
| Vendor-independent decision layer across organisations' systems | CONCEPTUAL (thesis framing only) |

## Positioning constraints

- Do not title around Anthropic beyond the news piece; do not let Anthropic define the category.
- Do not reposition Mneme as a "Claude company"; Claude is one governed environment among Claude Code, Codex, Kiro and others.

## Non-insight site edits requested

- Add the FDE cluster pages (`forward-deployed-engineers-enterprise-ai`, `forward-deployed-engineering-ai-sdlc`, `forward-deployed-engineering-architecture`, `fde-coding-agents`, `forward-deployed-architects-need-a-decision-layer`) to the agent-infrastructure topic hub (decision 2026-10-14).

(Go-to-market follow-ups from the chat are tracked outside this public repository.)

## Open questions

- Resolved 2026-10-14: the news piece and the FDE cluster go on the agent-infrastructure hub.
- Which "After the AI engineer leaves" angle survives against `forward-deployed-architects-need-a-decision-layer`?
