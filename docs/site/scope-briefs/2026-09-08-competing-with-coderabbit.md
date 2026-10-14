# Scope brief: Post-Competing with CodeRabbit

Status: **gathered, not built.** Do not treat as published; no `***` mark.

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Competing with CodeRabbit` |
| Created / last updated (UTC) | 2026-09-08 / 2026-09-08 (local timestamps in chat: Mon Sep 7, 7:42 PM onward) |
| Shape | Strategy conversation, 4 user turns. It is **not a clean article scope**. It is competitive strategy with several content and site actions at the end. |
| Repo check | `site/compare/coderabbit/` exists (added 2026-05-07, has no agentic-change-management content). `site/insights/review-is-not-governance/` (2026-05-07) and `site/insights/agentic-change-management-needs-a-decision-layer/` (#136, 2026-09-17, covers CodeRabbit's Triage and its agentic change management framing) already cover adjacent ground. The comparison piece below is not shipped. |

## Build card

| Field | Value |
|---|---|
| Kind | **site edit (recommended)**: refresh `/compare/coderabbit/` (compare-page contract, `scripts/check_compare.py`) rather than a new insight |
| Title | n/a for the refresh; if built as an insight instead: "CodeRabbit Agentic Change Management: Review Is Not Pre-Action Enforcement" |
| Slug | refresh `compare/coderabbit/`; insight fallback `coderabbit-agentic-change-management-pre-action-enforcement` |
| Report-anchored (ADR-015) | yes if an insight: entity = "CodeRabbit" (named vendor is the spine) |
| Topic hub | architectural-governance (insight fallback only) |
| Content type (`--type`) | n/a for the compare-page refresh; Analysis if built as an insight |
| OG headline | Review Is Not Pre-Action Enforcement (5 words) |
| Editorial gate | **fails as a new insight**: `agentic-change-management-needs-a-decision-layer` (#136) already takes the CodeRabbit "agentic change management" entry point. The compare-page refresh passes as cornerstone support |
| Five questions | changed: CodeRabbit repositioned as a change-control layer; matters: buyers will treat the two as substitutes; breaks: architectural violations caught only at PR time cost a regenerate loop; do: govern the action boundary, review the result; governance: different boundaries, complementary |
| Overlap verdict | update `compare/coderabbit/` instead; link `agentic-change-management-needs-a-decision-layer` and `review-is-not-governance` |
| Cross-links | the two pages above |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

## Agreed scope (what the chat actually concludes)

### Content item (the only article-shaped ask)

- **Piece:** a comparison/education page on **pre-action enforcement vs post-generation review**, "without making it an attack page on CodeRabbit". Explain why they solve different boundaries.
- **Slug suggestion:** `pre-action-enforcement-vs-post-generation-review`. It may be better built as an **update to `site/compare/coderabbit/`** (stale against CodeRabbit's August 2026 positioning) than as a new insight. Decide with the user.
- **Audience:** engineering leaders, principal and staff engineers evaluating AI code-review and governance tools. The chat says not to narrow to Principal Architects only. Buyers: CTO, VP Engineering, Platform/DevEx leadership, Principal/Staff and architecture leadership.
- **Thesis lines the chat endorses:**
  - "CodeRabbit reviews software changes. Mneme governs architectural change."
  - "Code review evaluates a change. Mneme constrains the actions that can create the change."
  - "Don't review architectural drift after the agent creates it. Prevent the agent from creating it."
  - Possible complementarity: Mneme asks whether the architectural decision was obeyed; CodeRabbit asks whether the implementation is correct, secure and worth merging.
- **Worked example:** ADR says SQLite (the chat's third turn uses "ADR-014 says PostgreSQL" and "SQLite, not PostgreSQL" inconsistently); agent attempts the opposite; CodeRabbit would flag it at PR time; on supported native write paths, Mneme blocks the write before it lands. Normalise the example before using it.
- **Comparison table the chat endorsed:** primary object (change/PR vs architectural decision); moment (review/pre-merge vs before and during agent action); policy representation (instructions and AI checks vs typed executable rules); evaluation (agentic/semantic vs deterministic where protectable); control surface (PR/review system vs agent/harness/tool boundary).
- **Cost argument (from the user's pasted third message):** late PR-level rejection wastes tokens, compute and context for a regenerate loop. Treat as an argument, not a measured figure. No numbers given.

### Non-article actions the chat also proposes (not in scope for an insight build)

1. **Roadmap page update** (`/roadmap/`): hero "Building the Governance Layer for the Agentic AI SDLC"; Phase 1 add Audit → Mneme-ready → activated Protection; Phase 3 rename "Agent Platform Integrations" → "Agentic Workflow Governance"; Phase 4 make the destination an architectural control plane; replace the thesis section with "Why architecture becomes infrastructure when agents can act". Progression: Audit → Protect → Team Governance → Agentic Governance → Architectural Control Plane. **Note:** `site: refresh roadmap around the decision and control layer (#179)` already merged after this chat; re-check what remains.
2. Homepage: say "before the change is written" near the top.
3. Architecture page: visual execution boundary (Architectural decision → Mneme policy → agent/tool request → allow/block → filesystem → PR/review). (#193 and #183 touched this page since.)
4. Architecture Audit page: commercial story "find the decisions your agents can currently violate, then protect them before execution".
5. Proof demo: show the expensive failure loop vs immediate block.
6. A single canonical Mneme diagram: Architecture → decisions → executable constraints → Mneme pre-action control → agents/harnesses → permitted code → review/CI.

## Key facts, figures, sources

All unverified at the time of the chat; verify each against the live source before use. The chat's links (query strings stripped):

| Claim in chat | Source URL | Verified? |
|---|---|---|
| CodeRabbit raised $143M at a $1.5B valuation; 17,000+ customers; 2M+ code reviews/week; ~$15M ARR and 8,000 customers in 2025; 5x YoY revenue growth by Aug 2026 | https://www.reuters.com/technology/ai-code-review-platform-coderabbit-valued-15-billion-latest-funding-round-2026-08-12/ | no |
| CodeRabbit positions as "Agentic Change Management" / "the control layer for software change" | https://www.coderabbit.ai/newsroom/coderabbit-series-c-agentic-change-management | no |
| Same positioning, product announcement | https://www.coderabbit.ai/blog/introducing-agentic-change-management | no |
| Earlier custom-policy / quality-gates positioning (2025) | https://www.coderabbit.ai/blog/coderabbit-series-b-60-million-quality-gates-for-code-reviews | no |
| Custom architectural checks run against the PR read-only; blocking is a pre-merge check; checks are mostly AI/natural-language, AST rules available | https://docs.coderabbit.ai/pr-reviews/pre-merge-checks | no |
| CodeRabbit May 2026 article: waiting until PR review is "the wrong intervention"; agents should understand rules before writing code | https://www.coderabbit.ai/blog/policy-as-code-the-missing-layer-in-ai-assisted-development | no |
| Mneme pages the chat inspected (live-site claims: roadmap hero said "Governance Layer for AI-Assisted Development") | https://mnemehq.com/ and https://mnemehq.com/roadmap/ | no |


## Mneme positioning constraints

- Do not write a CodeRabbit attack page. Frame as different boundaries, with a possible complementary integration.
- Do **not** assert CodeRabbit "will not" move into this space. The chat explicitly reverses an earlier assumption: CodeRabbit already talks about architectural drift, policy-as-code and agent governance. Pitch differences by mechanism (typed deterministic rules at the agent/tool boundary vs PR-time AI checks), not by "they can't".
- The chat's internal strategic assessments (opportunity, threat level, market size) are not copy; keep them, and any valuation or market-size claim about Mneme, out of public pages.
- Avoid positioning as "AI governance for software engineering" generally. Stay at "architectural drift prevention, powered by pre-action architectural enforcement, evolving toward an architectural control plane" (the chat's final phrasing).
- **Conflict with the pre-action chat:** this chat's last turn says pre-action is the mechanism, not the category name. Align the two before building.
- Anything about enforcement at the agent/tool boundary, cross-harness adapters, exceptions and evidence history must be classified SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL in the audit.

## Open questions

- New insight, or refresh of `/compare/coderabbit/`? The existing compare page predates CodeRabbit's August 2026 repositioning.
- Is the roadmap page work already complete after #179?
- Which of the six non-article actions go to separate PRs (different contracts and validators)?

## Unverified / needs checking

- Every CodeRabbit figure and quote above. In particular the funding/valuation/customer numbers rest on one Reuters link; confirm against the live article. Note the Reuters URL slug contains "2026-08-12".
- The characterisation of CodeRabbit's check mechanics comes from reading the docs page through the chat; re-read it live before describing it.
- "Three weeks ago" funding timing is relative to the chat date (Sep 7), not publication date.
