# Scope brief: Post-Agent orchestrators and factories

Status: **gathered, not built** (site edit, not an insight; separate PR and contract)

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Agent orchestrators and factories` |
| Created / last updated (UTC) | 2026-10-20 / 2026-10-20 |
| Shape | 1 user turn (agent orchestrators need their own integrations section, a stronger link to software factories, "start small" advice, how-to guides); 1 answer. The answer opened site issue [#231](https://github.com/MnemeHQ/mnemehq-site/issues/231). Read in full 2026-10-20; no collapsed turns. |
| Repo check | `site/integrations/` lists coding agents, orchestrators and runtimes in one flat directory (claude-code, codex-cli, kiro, antigravity, langchain-langgraph, paperclip, hermes, microsoft-agent-forge, mcp, github-actions, gitlab and others). `software-factory-governance-layer` is the strategy pillar (`find_overlap.py` 88.3 for a software-factory title). `/docs/how-to/` has five task guides, all single-operation. |

## Build card

| Field | Value |
|---|---|
| Kind | site edit (not an insight; follows the integrations and docs contracts, own PR) |
| Title | n/a |
| Editorial gate | n/a for an insight. No new software-factory concept page or insight: that would make three pages on the same ground (the chat says so) |
| Cannibalisation | the use-case page must not restate `software-factory-governance-layer`; it explains how a team starts, and links to the pillar for why |

## Agreed scope

**Architecture to show:** software factory (work queue, coordination, review, delivery) → agent orchestrator (dispatch, state, retries, handoffs) → coding agents → execution systems (files, shell, CI, deploy), with Mneme applying approved decisions at supported execution boundaries (guidance, pre-write, CI, evidence). Orchestrators control how work happens; Mneme controls which architectural constraints that work must respect. Mneme stays independent of orchestrator, model and host.

**1. Restructure Integrations by function** (keep the directory and URLs):

| Section | Members |
|---|---|
| Coding agents and harnesses | Claude Code, Codex, Kiro, Antigravity |
| Agent orchestrators | LangGraph, Paperclip, OpenAI Symphony, Hugging Face Agent Manager, custom orchestrators |
| Software factories | workflow patterns, factory platforms, reference implementations |
| Decision interoperability | MCP, CLI, Python API |
| CI and enforcement | GitHub Actions, GitLab, downstream policy engines |
| Infrastructure and runtime | OpenShell and other runtime environments |

Keep explicit statuses on every entry: shipped, validated, experimental, planned, research. A conceptual connection is not interoperability. Orchestrator pages use one format: what it does → where Mneme fits → supported enforcement boundary → evidence → setup → limitations. Do not assume middleware or local hooks intercept every mutation.

**2. Use-case page:** `/use-cases/software-factory-governance/`, "Software Factory Governance: Start Small, Scale with Evidence". The starter pattern is a one-issue software factory: one repository, one coding agent, two reviewed decisions, human-approved merge. Steps: pick one bounded issue → resolve applicable decisions → run the agent in an isolated workspace → check supported mutations and collect evidence → run tests and Mneme CI → open a draft PR for review. Label it a proposed reference workflow, not a validated six-stage flow. Message: you don't need ten agents to start a software factory; start with one repeatable, verifiable workflow and give it the decisions it must respect.

Sources for "start small" (verify): Matt Pocock's tiny-factory suggestion (one bounded issue per day) and Addy Osmani's post that teams may not need a full factory until they need repeatable, event-driven work.

**3. How-to backlog** (order from the chat):

| Priority | Guide | Gate |
|---|---|---|
| P0 | Build your first decision-governed software factory | after the small-factory experiment produces reproducible evidence |
| P0 | Add architectural checks to LangGraph | supported middleware path, allowed and forbidden change |
| P1 | Connect Mneme to a custom orchestrator (MCP, mandatory interception, CI fallback, coverage gaps) | verified integration boundary |
| P1 | Carry decisions across multiple agents | verified integration boundary |
| P1 | Measure whether your software factory is safe to scale | evidence |

Each hands-on guide needs real commands, a sample repo, expected output, a failure example, a decision-linked evidence record, and a statement of which paths are not protected. The first guide must not require LangGraph or an orchestration platform.

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Integrations and support levels | per each integration page's current status; re-verify before restructuring copy |
| The six-step one-issue factory as a validated flow | not validated; describe as a proposed reference workflow |
| Mneme orchestrating agents | not claimed; Mneme is not an orchestrator or a factory platform |

## Positioning constraints

- Position Mneme as part of building a software factory, not as a competing factory platform.
- Leave out the integration runtime partner the chat names; it is tracked privately.

## Non-insight site edits requested

All of the above. Tracked in [#231](https://github.com/MnemeHQ/mnemehq-site/issues/231).

## Open questions

- Sequencing: the integrations restructure can go ahead on verified statuses; the first runnable guide waits for the experiment's evidence.
