# Insights scope ledger

Tracks ChatGPT scope chats (project: "Mneme Growth and GTM") against what actually
shipped, so we stop re-crawling the whole chat list on every "draft insights" run.
See [[draft-insights-workflow]] memory for the pipeline this supports.

**How to update:** after a scope chat's article ships and the chat is renamed with
the `***` prefix in ChatGPT, add/update its row here with the PR # and merged date.
Only chats that produced (or were meant to produce) a published insight belong here —
not every chat in the project.

## Published

| Scope chat (ChatGPT title) | Scoped | Shipped as | PR | Merged |
|---|---|---|---|---|
| ***Post-MCP Agentic SDLC Scope | 2026-09-17 | `agentic-change-management-needs-a-decision-layer` | [#136](https://github.com/MnemeHQ/mnemehq-site/pull/136) | 2026-09-17 |
| ***Post-FDE Decision Layer Article | 2026-09-15 | `forward-deployed-architects-need-a-decision-layer` + FDE supporting cluster (4 pages) | [#132](https://github.com/MnemeHQ/mnemehq-site/pull/132) | 2026-09-15 |
| ***Post-FDE ICP Content Cluster | 2026-09-15 | `most-valuable-ai-dataset-decisions-already-made`, `agent-economy-needs-decision-infrastructure`, + FDE cluster pages | [#129](https://github.com/MnemeHQ/mnemehq-site/pull/129) | 2026-09-15 |
| ***Post-Mneme Decision Data | 2026-09-15 | folded into #129 (decision-dataset article) — **not independently verified, confirm before trusting** | [#129](https://github.com/MnemeHQ/mnemehq-site/pull/129)? | 2026-09-15 |
| ***Post-Positioning strategy analysis | 2026-09-15 | not independently verified — likely folded into #129's "decision-layer thesis" | unknown | unknown |
| (unmarked chat, not yet located) | — | `ai-engineering-roi`, `ai-throughput-is-not-engineering-throughput` | [#135](https://github.com/MnemeHQ/mnemehq-site/pull/135) | 2026-09-15 |

## In review (drafted, not merged, not yet marked `***`)

Drafted 2026-09-19 on branch `site/software-factories-conway-brooks-private-ai`. Rename the chats with `***` once the PR merges:

| Scope chat(s) | Scoped | Published slug | Notes |
|---|---|---|---|
| Post-software factories + Post-Scope software factories | 2026-09-19 | `software-factory-governance-layer` | One article, refined across two chats (2nd adds the Bob Bemer/1968 historical framing). Pillar for a planned 5-article cluster — only the pillar is scoped so far. |
| Post-Conway's Law Relevance | 2026-09-18 | `conways-law-ai-coding-agents` | Scoped to run first in the Conway→Brooks pair. |
| Post-Brooks Law Relevance | 2026-09-18 | `brooks-law-ai-coding-agents` | Scoped to run second, immediately after Conway. |
| Post-Strategic Signal local infra | 2026-09-16 | `private-ai-infrastructure-governance` | Latham facts verified against Bloomberg Law and Legal IT Insider. The FT citation named in the scope chat could not be located and was dropped. Scoped to publish near the FDE article as an enterprise-governance pairing. |

**Last insight-article PR before this ledger was created:** [#136](https://github.com/MnemeHQ/mnemehq-site/pull/136),
merged 2026-09-17T13:37:05Z — "Position Mneme's Decision Index against post-MCP
agentic change management."
