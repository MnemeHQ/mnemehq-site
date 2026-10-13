# Scope brief: Post-claude frontier academy Assess program relevance

Status: **gathered, not built**

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
| Topic hub | agent-infrastructure (proposed; the FDE pages sit on no hub) |
| Eyebrow / section | Analysis / Engineering |
| OG headline | Claude Frontier Academy and the Decision Layer (7 words) |
| Editorial gate | pass: named-vendor news entry point; "Claude Frontier Academy", "Frontier Deployed Engineers" and "Anthropic" in the first 150 words |
| Five questions | changed: Anthropic is funding 10,000 deployed engineers to take Claude to production; matters: deployment is industrialising inside consultancies and enterprises; breaks: the judgment that governed a deployment leaves with the engineer; do: make decisions, authority and exceptions survive handover; governance: an organisational decision layer under every agent, not only Claude |
| Cannibalisation | `find_overlap.py`: for "Claude Frontier Academy" alone, top hit `anthropic-claude-marketplace-ai-engineering-control-plane` 45.1 (different announcement). With the full title, `forward-deployed-engineers-enterprise-ai` 90.2 and `forward-deployed-engineering-ai-sdlc` 61.8, matching on "deployed engineer". Verdict: **clear** for the news entity, but keep FDE definitions out and link the FDE pillar instead |
| Cross-links | `forward-deployed-engineers-enterprise-ai`, `forward-deployed-architects-need-a-decision-layer`, `fde-coding-agents`, `anthropic-claude-marketplace-ai-engineering-control-plane` |

## Rest of the chat's cluster: verdicts

| Article (chat priority) | Verdict |
|---|---|
| What Is a Frontier Deployed Engineer? (P0, evergreen FDE pillar) | **update instead**: extend `forward-deployed-engineers-enterprise-ai` to cover "frontier deployed engineer" and the solutions → forward → frontier evolution |
| The Missing Control Layer in Enterprise AI Deployment (P0) | not scoped for this build; run `find_overlap.py` (likely overlaps `enterprise-ai-guardrails-five-layers`, `coordination-governance-multi-agent-systems`) |
| What Happens After the AI Engineer Leaves? (P0) | candidate; close to `forward-deployed-architects-need-a-decision-layer` ("the architect becomes another silo"). Re-angle on handover or merge |
| From AI Deployment to AI Governance: What Has to Become Machine-Readable (P1) | overlaps the Business Type chat's "From Decision Records to Decision Governance"; merge |
| Why Frontier Deployed Engineers Need a Decision Layer (P1) | **drop**: same thesis as `forward-deployed-architects-need-a-decision-layer` |
| How to Hand Over an Agentic System Without Losing Its Engineering Intent (P1) | merge with "After the AI Engineer Leaves" |
| Why AI Agents Need Institutional Memory, Not Just Context Windows (P1) | likely overlaps `memory-is-not-governance`, `long-context-windows-governance-infrastructure`; check |
| Why Guardrails Are Not the Same as Governance (P1) | likely overlaps `ai-coding-agent-guardrails`, `enterprise-ai-guardrails-five-layers`; check |
| The AI Deployment Stack Is Missing a Decision Plane (P2) | new term "decision plane": terminology lock |
| Who Owns a Decision When an AI Agent Writes the Code? (P2) | check |
| Why Software Factories Need a Decision Index (P2) | overlaps `software-factory-governance-layer`; merge or drop |

The chat also proposed a content architecture (pillar "Decision Governance for Agentic Software" with discover / understand / enforce / operate clusters; FDE content in "operate"). That depends on the decision-governance terminology decision.

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

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

**None verified.**

| Claim | Source | Verified? |
|---|---|---|
| Launched 2 October 2026; $100M to train 10,000 Frontier Deployed Engineers by end of 2027 | https://www.anthropic.com/news/claude-frontier-academy | no |
| First cohorts include Accenture, Bain, Capgemini, Deloitte, McKinsey, Morgan Stanley, Commonwealth Bank, Novo Nordisk | same | no |
| In-person enterprise deployment simulation, then 12 weeks on a real production Claude project; curriculum runs from use-case selection through security review, deployment and handover | same | no |
| Participants return with a named project and lead it to production ("from an idea to a system in production") | same | no |
| Nomination-based; via Anthropic account team or Partner Account Manager; cohorts in San Francisco, New York, London | same | no |
| Claude Partner Network: 40,000+ firms applied; service-partner tiers based on certified engineers and production deployments | https://www.anthropic.com/news/services-track-partner-hub | no |
| Startup programme open to bootstrapped, pre-seed and venture-backed startups | https://claude.com/programs/startups | no |

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Vendor-independent decision layer across Claude, OpenAI, internal agents, repositories, CI/CD | CONCEPTUAL (thesis framing only) |
| Deterministic enforcement of repository decisions | SHIPPED on supported native write paths and in CI |
| Decision Index | SHIPPED (OSS, mneme-hq 0.10.0: canonical Decision Index persistence; the Decision MCP reads it). Cross-system ingestion is PLANNED; ADR-031 governance semantics are accepted but unreleased |
| Vendor-independent decision layer across organisations' systems | CONCEPTUAL (thesis framing only) |

## Positioning constraints

- Do not title around Anthropic beyond the news piece; do not let Anthropic define the category.
- Do not reposition Mneme as a "Claude company"; Claude is one governed environment among Claude Code, Codex, Kiro and others.

## Non-insight site edits requested

None. (Go-to-market follow-ups from the chat are tracked outside this public repository.)

## Open questions

- Hub for the news piece and for the FDE cluster generally (none of the FDE pages sits on a hub).
- Which "After the AI engineer leaves" angle survives against `forward-deployed-architects-need-a-decision-layer`?
