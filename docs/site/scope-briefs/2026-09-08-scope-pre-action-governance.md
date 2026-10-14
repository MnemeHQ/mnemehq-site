# Scope brief: Post-Scope pre action governance

Status: **built 2026-10-14** as `/insights/pre-action-enforcement-agent-governance/` (batch 1 PR; not yet merged or deployed). No `***` mark until deployed.

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Scope pre action governance` |
| Created / last updated (UTC) | 2026-09-08 / 2026-09-08 (local timestamp in chat: Mon Sep 7, 8:08 PM) |
| Shape | One short prompt ("Scope the ore-actiok category content") and one long reply. |
| Repo check | No pre-action pillar or cluster in `site/`. Only `package-hallucinations-pre-action-governance` (shipped #150) uses the term. Not shipped. |

## Build card

**Decision 2026-10-12:** "pre-action" is a mechanism word, not a category: no `/pre-action-governance/` pillar and no concept page. The definition article survives only as an insight about the mechanism, using "decision governance" (the locked concept term) for the category. Retitle before building, e.g. "Pre-Action Enforcement: Where Agent Governance Takes Effect".

| Field | Value |
|---|---|
| Kind | insight explaining the mechanism (no pillar, no concept page: decision 2026-10-12) |
| Title | Pre-Action Enforcement: Where Agent Governance Takes Effect |
| Slug | `pre-action-enforcement-agent-governance` |
| Report-anchored (ADR-015) | no |
| Topic hub | ai-coding-agents (where `package-hallucinations-pre-action-governance` sits) |
| Content type (`--type`) | Concept (explains a mechanism) |
| OG headline | Where Agent Governance Takes Effect (5 words) |
| Editorial gate | pass: distinct query (pre-action enforcement, the agent action boundary); introduces no new category term, uses "decision governance" for the category |
| Five questions | changed: agents act, not just generate; matters: review only sees results; breaks: consequential actions run before any control; do: put deterministic gates at the action boundary; governance: allow / warn / block before execution |
| Cannibalisation | `find_overlap.py` (retitled): `package-hallucinations-pre-action-governance` 68.0 (a news case vs this mechanism explainer), `integrations/github-actions` 39.6 (PR-level enforcement, a different boundary). Verdict: **re-angle**: explain where enforcement happens across boundaries (generation, tool call, write, PR); link the package piece as the worked case |
| Overlap verdict | link to `package-hallucinations-pre-action-governance` and `review-is-not-governance`; keep apart from the O'Reilly/TechTalks angles |
| Cross-links | the two pages above, `agentic-change-management-needs-a-decision-layer` |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 40 (8 on each dimension) |
| `lint_prose.py` | 0 errors, 0 warnings |
| Cold read: thesis as restated | "Agent governance only counts as enforcement if a control can refuse an action before it executes, but this works only on action paths the gate can fully see, so it must be paired with end-of-turn and CI backstops." Matches. |
| Cold read: unclear terms, and how resolved | "decisions", "gate" and "backstop" defined at first use; Mneme introduced before its integrations are cited; heredoc, MultiEdit, tree and the Audit tiers glossed. "The most common mistake" softened to "a common mistake". |

## Agreed scope

*As scoped in the chat, kept for reference. Superseded by the 2026-10-12 decision above: no pillar, no category term; only the mechanism article in the build card goes ahead, and any later piece uses "decision governance" for the category.*

The chat scoped a **category and cluster**: a pillar page plus six core articles and a second wave.

- **Category thesis:** pre-action governance is the enforcement of engineering constraints before an AI agent is allowed to carry out a consequential action. Boundary framing: Intent → context → generation → proposed action → governance decision → execute/block → verify.
- **Audience:** not stated. Inferred: engineering leaders and senior engineers adopting coding agents. Confirm.
- **Pillar:** `/pre-action-governance/`, H1 "Pre-Action Governance for AI Agents". Deck: "Control consequential agent actions before they are executed. Pre-action governance turns engineering decisions and constraints into deterministic allow, warn, or block decisions at the agent action boundary." It is a **page/concept contract**, not an insight, so it needs its own PR and validators (see `docs/site/concept-publication.md`).
- Pillar sections: agents as actors; what it is; why post-action verification is insufficient; the action boundary; different boundaries (pre-generation guidance, pre-tool, pre-write, pre-network/API, pre-delegation) which must **not** be claimed equivalent; what belongs in a policy; why prompts and context are not enough; pre-action plus post-action (Prevent → catch → verify); architectural governance as the concrete implementation (ADR → deterministic rule → applicable proposed change → verdict); Architecture Audit as the CTA.

### Six core articles

| Title | Role |
|---|---|
| What Is Pre-Action Governance? | Category definition / canonical explainer |
| The Agent Action Boundary: Where AI Governance Becomes Enforcement | Technical architecture |
| Pre-Action vs Post-Action Governance for AI Agents | Category comparison |
| Why Agent Permissions Need Policy Gates, Not Just Prompts | Broader agentic-AI hook |
| From Architecture Decisions to Pre-Action Controls | Mneme's strongest concrete use case |
| Prevent, Catch, Verify: A Control Model for AI Coding Agents | Full lifecycle model |

Second wave (selective): Why Human Approval Is Not a Governance Architecture; Why AI Agent Observability Cannot Prevent Bad Actions (adjacent to AgentInspect, without attacking the category); What Should an AI Coding Agent Be Allowed to Change?; Deterministic Policy Gates for AI Agents; Pre-Action Governance in Multi-Agent Systems; When Correct Code Should Still Be Blocked.

The chat suggested building the definition article, then the pillar, then the boundary and comparison pieces (superseded, see above). The chat does not rank priority beyond "six core, then selectively expand".

### Vocabulary to lock

agent action boundary; pre-action governance; proposed action; deterministic policy gate (non-LLM verdict mechanism); action authorization; post-action verification. For Mneme: architectural action boundary / architectural guardrail / architectural protection.

### Terminology correction (important)

Stop describing Mneme as "pre-generation enforcement". Use: **Guide before generation. Govern before action. Verify after action.** For supported native write paths Mneme can deterministically block the proposed mutation before it reaches disk: that is pre-write / pre-action enforcement, even though the model may already have generated the edit.

### Cannibalisation map

- O'Reilly article: architectural guardrails / drift / functionally correct code that violates architecture.
- TechTalks article: why prompts, instruction files and RAG do not reliably enforce architecture, with a blocking example.
- Pre-action pillar: the broader control architecture for agentic systems.
- Hierarchy: Pre-Action Governance → Architectural governance → Architectural drift prevention → Deterministic architectural guardrails → Mneme HQ.

### Audit tie-in

Audit output tiers (as shipped, ADR-026 and `/audit/`): **Protected** (an effective control exists), **Mneme-ready** (deterministic protection is possible but not yet active), **Requires modelling** (needs a structured rule before it can be protected), **Guidance** (context, not mechanically enforceable). CTA question: "Which decisions can your agents violate before any control intervenes?"

## Key facts, figures, sources

None cited. No statistics, no URLs. References are only to Mneme's own prior publications (O'Reilly, TechTalks).

## Mneme positioning constraints

- Mneme sits "principally at the proposed action → execute/block boundary today, with pre-generation guidance where an integration supports it". Keep that qualifier.
- Teach the category; do not open as a product pitch.
- Do not claim post-action controls (review, CI, observability, audit) disappear. The model is Prevent → catch → verify.
- Expansion beyond code writes (migrations, infrastructure, database/schema, API changes, agent delegation) is **future-looking**. Do not present it as shipped.
- Resolved 2026-10-12: "pre-action" names the mechanism, not the category, as the follow-on CodeRabbit chat argued.

## Non-insight site edits requested

- None for this article. (The chat's `/pre-action-governance/` pillar was dropped on 2026-10-12.)
- Possibly a canonical diagram reused on the site (see CodeRabbit brief).

## Open questions

- Existing positioning ADRs (ADR-001/013/014 in `MnemeHQ/mneme`) govern category and tagline changes. Any wording here that changes category or tagline copy needs those ADRs amended first.

## Unverified / needs checking

- Every statement about what Mneme enforces today (PreToolUse, native write paths, warn vs block) must be re-checked against the current release's documented behaviour (mneme-hq 0.10.0 release notes and docs) and classified SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL by the Opus audit.
- Mentions of the O'Reilly and TechTalks pieces are unlinked; find the live URLs before citing. **Not cited in the 2026-10-14 build.**
- AgentInspect is named without context; confirm what it is before referencing. **Not referenced in the 2026-10-14 build.**
- 2026-10-14 build: the article cites no external sources. Every Mneme claim is drawn from `/docs/how-enforcement-works/` and the Claude Code, Codex CLI, Kiro, Antigravity and Claude Agent SDK integration pages, and checked by the Opus audit.
