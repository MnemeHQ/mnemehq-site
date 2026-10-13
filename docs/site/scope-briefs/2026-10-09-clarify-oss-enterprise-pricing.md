# Scope brief: Post-Clarify OSS Enterprise Pricing

Status: **gathered, not built**

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Clarify OSS Enterprise Pricing` |
| Created / last updated (UTC) | 2026-10-09 / 2026-10-09 |
| Shape | 1 turn: "Do we need to write about enterprise vs OSS on the pricing page? More prominent?" |
| Repo check | Not done. `site/pricing/index.html` still says "Enterprise — later" and "No commercial enterprise tier exists yet"; the homepage has no `/pricing/` link. |

## Build card

| Field | Value |
|---|---|
| Kind | **site edit** (pricing, Enterprise Trust, homepage, nav/footer); not an insight |
| Target pages | `/pricing/` (P0), Enterprise Security & Trust page (P0), homepage (P1), nav/footer (P1), For Teams (P1), new Enterprise page (P2) |
| Cannibalisation | `find_overlap.py`: `/pricing/` 84.8 (the target itself), `open-source-ai-coding-agent-governance` 67.6. Verdict: **update instead**: edit `/pricing/`; check the OSS governance page for consistent wording |
| Validators | `check_nav_footer.py` (nav/footer links), `check_sticky_nav.py`, encoding; the shared nav and footer are canonical across all pages |

## Agreed scope

- **Positioning line:** "OSS executes engineering decisions. Enterprise operates decision governance at organizational scale."
- **Problems with the current page:** Enterprise reads as an upgraded enforcement engine; OSS reads as limited to individuals and small repositories (multi-repo CI/CD gating shown as Enterprise-only); Enterprise is presented mainly as unavailable.
- **P0, pricing page, above the cards:** headline "One open decision engine. Two ways to govern engineering decisions." Supporting copy: OSS provides the decision model, applicability and authority semantics, agent integrations and deterministic enforcement; Enterprise is being developed for discovering decisions across systems, reconciling authority, maintaining them over time and managing governance across teams and software factories. Cards: Open Source (free forever, run independently); Guided Pilot (complimentary, validate on real workflows); Enterprise (design partners, shape organisational decision governance).
- **P0, comparison table:** replace the misleading feature boundaries. Proposed boundary (intended, not shipped):

| Dimension | OSS | Enterprise (planned) |
|---|---|---|
| Purpose | execute known decisions | discover, reconcile, govern across the organisation |
| Decision Index | open core | built on open core |
| Authority, applicability, precedence | open core | governed organisational workflows |
| Deterministic enforcement | open core | managed across teams and environments |
| Agent integrations | open core | centralised management |
| Decision discovery | repository/local | cross-system |
| Confluence, Jira, Slack | not supported (no import or ingestion path exists in OSS) | connected ingestion and sync (planned) |
| Evidence | local, inspectable | aggregated history and reporting |
| Administration | local | RBAC, approvals, lifecycle |
| Pricing | free, MIT | set with design partners |

- **P0, Enterprise Trust page:** align its OSS/Enterprise split with the same boundary.
- **P1:** homepage OSS/Enterprise note near the team section; Pricing (or "OSS & Enterprise") in nav/footer; For Teams page explains when an organisation needs Enterprise. **P2:** dedicated Enterprise page.
- **Labels everywhere:** "Available today", "In development / validation", "Enterprise direction".
- **CTO test:** the distinction should be clear within 30 seconds on the pricing page.

## Key facts, figures, sources

All claims are about the live site; re-read `/pricing/` and the Enterprise Trust page before editing.

## Mneme claims and maturity

| Claim | Class |
|---|---|
| OSS: decision model, applicability semantics, agent integrations, deterministic enforcement, MIT | SHIPPED (verify "authority and precedence" are actually in OSS before saying so) |
| Decision Index as open core | SHIPPED (OSS, mneme-hq 0.10.0: canonical Decision Index persistence; the Decision MCP reads it). Cross-system ingestion is PLANNED; ADR-031 governance semantics are accepted but unreleased |
| Every Enterprise row | PLANNED ("Enterprise direction") |

## Positioning constraints

- PUBLISHING.md: "decision layer" thesis framing does not belong on pricing; the product-level "decision layer" (the shipped rule-evaluation component) is allowed. The pricing page title already reads "Open-Source Decision and Control Layer".
- Don't make Enterprise more prominent than the evidence: decision discovery and measured outcomes are still being validated.
- The trust page's current "OSS is local/project-scoped" may reflect what actually shipped. Verify before rewriting it.
- A pricing headline change may touch tagline/category copy: check ADR-001/013/014.

## Non-insight site edits requested

All of the above. Separate PRs from any insights batch.

## Open questions

- Is "Decision Index" part of OSS today?
- Nav label: "Pricing" or "OSS & Enterprise"?
