# Scope brief: Post-AI Silo Breakdown Content

Status: **merged** (decision 2026-10-12): folded into "The Return of the Silo Engineer" as one section; see [Cohesion brief](2026-10-04-cohesion-and-reddit-thread.md). Not built separately. Do not treat the chat as published until that article ships.

| Field | Value |
|---|---|
| ChatGPT chat | `Post-AI Silo Breakdown Content` |
| Created / last updated (UTC) | 2026-09-12 / 2026-09-13 (local timestamp in chat: Sat Sep 12, 3:24 PM) |
| Shape | One user prompt, one assistant reply. No later refinement. |
| Repo check | `site/insights` has no article on silos or decision silos (only unrelated mentions in `agent-formation-engineering-performance-metrics`). Not shipped. |

## Build card

Proposed values; confirm with the user before building.

| Field | Value |
|---|---|
| Kind | insight |
| Title | The Enterprise AI Problem Isn't Data Silos. It's Decision Silos. |
| Slug | `enterprise-ai-problem-is-decision-silos` |
| Report-anchored (ADR-015) | no (original POV piece) |
| Topic hub | architectural-governance (proposed; the related decision-layer pieces are on no hub) |
| Eyebrow / section | Analysis / Engineering |
| OG headline | Enterprise AI Has a Decision Silo (6 words) |
| Editorial gate | conditional pass: distinct query ("enterprise AI silos"); no new evidence, so it must earn its place by supporting the decision-layer cornerstone |
| Five questions | changed: agents act across systems; matters: each AI sees a partial company; breaks: agents violate decisions recorded elsewhere; do: make decisions machine-readable with scope and lifecycle; governance: a shared decision layer constrains specialised agents |
| Cannibalisation | `find_overlap.py`: no strong site hit (top 41.2 `enterprise-ai-guardrails-five-layers`, unrelated intent). **Batch overlap:** the 2026-10-04 "Post- Cohesion And Reddit Thread" chat scopes "The Return of the Silo Engineer"; merge the two into one silo piece |
| Overlap verdict | re-angle against `most-valuable-ai-dataset-decisions-already-made` and `agent-economy-needs-decision-infrastructure`, which argue the same layer; this piece's distinct angle is "silos" |
| Cross-links | the two pages above, `forward-deployed-architects-need-a-decision-layer`, `software-factory-governance-layer` |

"Decision layer" here is thesis vocabulary: use it only per the PUBLISHING.md 2026-09-11 amendment (never as something Mneme ships in full).

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

## Agreed scope

- **Working title (preferred by the chat):** The Enterprise AI Problem Isn't Data Silos. It's Decision Silos.
- **Alternate title:** AI Won't Transform the Enterprise Until It Can Cross the Silos.
- **Slug suggestion:** `enterprise-ai-problem-is-decision-silos`
- **Type:** thought-leadership pillar, explicitly "not another SEO article".
- **Audience:** enterprise / engineering leadership thinking about AI effectiveness across systems. (The chat does not name an audience; this is inferred from the framing, so confirm.)
- **Thesis:** enterprise AI cannot be effective while the decisions it needs are fragmented across code, tickets, documents, chat, architecture records, policies and people's heads. The silo that matters is decision context, not data. Formula in the chat: AI effectiveness = access + context + decisions + enforcement.
- **Chain to show:** conversation → decision → policy/rule → affected systems → implementation → evidence → outcome.
- **Do not argue** for one omniscient AI or for one giant vector database. Specialised agents stay specialised and share an authoritative decision layer.

### Proposed structure (from the chat)

1. AI adoption starts inside silos (IDE copilots, knowledge assistants, CRM AI, service AI, analytics AI).
2. Real work crosses them (one engineering decision may depend on an ADR, a security policy, an old incident, a customer promise, a Jira ticket and a Teams thread).
3. RAG only partly solves this. Knowing a document exists differs from knowing it was an approved decision, which component it applies to, what it supersedes, and whether violating it should stop the change.
4. The missing layer is decisions: no authoritative machine-readable system for what was decided, why, where it applies, whether it is active, and how it constrains future work.
5. Agents make it urgent: humans ask a colleague in another team, autonomous agents cannot reliably do that.
6. The future is not one omniscient AI: shared decision layer governing what specialised agents may do.
7. From knowledge management to decision infrastructure. Confluence, Slack, GitHub, Jira, EventCatalog, ServiceNow stay systems of record; the new layer connects the decisions between them.
8. Close on the Mneme connection late: an ADR can state a decision while a coding agent retrieves it and still violates it; knowing a decision differs from being governed by it.

### Diagram requested

Before: Slack, Jira, GitHub, Confluence, CI/CD, ServiceNow each feeding a separate AI with incomplete context.
After: sources feed a single DECISION LAYER (rules, scope, lifecycle, evidence) that feeds specialised agents.

### Closing line proposed

"The next phase of enterprise AI will not be won by the company that gives models access to the most data. It will be won by the company that can tell AI what the organisation has decided, and make those decisions survive across every system and agent."

## Key facts, figures, sources

None. This scope contains no statistics and no external citations. Every claim is argument or framing. If the build adds figures (for example enterprise data-silo surveys), they need primary sources found fresh; the chat provides none.

## Mneme positioning constraints

- Keep the Mneme connection subtle until near the end; "not a Mneme advert".
- Frames Mneme's decision index / decision layer as the long-term vision. The enterprise-wide connectors (Slack, Jira, ServiceNow) are **not** shipped; the chat refers to "integration strategy" and "longer-term Mneme vision". Treat every cross-system claim as PLANNED or CONCEPTUAL in the SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL audit, not as product capability.
- Software architecture (ADR vs agent behaviour) is the only grounded example.
- Overlap risk: FDE cluster, `most-valuable-ai-dataset-decisions-already-made`, `agent-economy-needs-decision-infrastructure` and the software-factory pillar already argue a decision-layer thesis. Cross-check for cannibalisation and re-angle rather than restate.

## Non-insight site edits requested

None.

## Open questions

- Which publication target: Mneme site only, or an external pitch? (The chat says "major thought-leadership pillar", nothing more.)
- Intended audience and word count are not stated.
- Whether a diagram asset is wanted, and in which style (see the OG and design standards in the repo).

## Unverified / needs checking

- No claim here is verified, because the chat cites nothing.
- "Enterprise tooling lists" (Confluence, Jira, EventCatalog, ServiceNow) are illustrative; only mention integrations that actually exist.
