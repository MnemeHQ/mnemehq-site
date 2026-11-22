# Scope brief: Post-Scope Atlassian AI SEO Response

Status: **gathered, not built** (draft written; cold read and claim audit pending)

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Scope Atlassian AI SEO Response` |
| Created / last updated (UTC) | 2026-11-18 (date not exposed by the UI; project list shows Nov 18, in-chat stamp Wednesday) / 2026-11-18 |
| Shape | 1 user turn, 1 assistant turn; read in full, truncation check passed (no "Show more" marker). Single scope, no later reversal. |
| Repo check | No page covers the Atlassian AI SDLC Index (body search for 69.7, 97.8, 340,000, "SDLC Index", "bot review", "survivorship" found nothing). Related: `atlassian-agentic-pivot-engineering-system-of-record` (Sep 2026, survey report), `why-code-review-cannot-scale-with-ai-output` and `ai-code-review-does-not-scale-linearly` (May 2026 review-capacity perspectives), `ai-code-comprehension-gap` (2026-11-16, review-load study plus candidate decision indicators), `ai-engineering-roi` (uses DX Q2 2026 data, five-stage scorecard). |

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | Atlassian AI SDLC Index: Review Is Measured, Architecture Is Not |
| Slug | `atlassian-ai-sdlc-index-code-governance` (the chat's recommended URL) |
| Report-anchored (ADR-015) | yes: entity = "Atlassian AI SDLC Index" (page title "The Atlassian AI SDLC Index"; the name carries no year, so none is added). Verbatim first in all six title fields; meta description leads with the entity and two figures that appear in the body (69.7%, 22.3). |
| Topic hub | engineering-performance |
| Content type (`--type`) | Report Response |
| OG headline | Atlassian AI SDLC Index: Architecture Unmeasured (6 words) |
| Editorial gate | pass: named-source entry point (a new Atlassian/DX report with no page on the site) plus new evidence for an existing thesis (measured review load and latency) |
| Five questions | changed: Atlassian published month-by-month DX data showing review load per reviewer up from 12.8 to 22.3 PRs a month and longer first-review times where AI share is higher; matters: every review figure measures speed or volume, none measures architectural conformance; breaks: locally correct changes that break a recorded decision pass every check a bot can run; teams should: add decision-side metrics (protection coverage, violations caught before merge, share of changes needing an owner's judgment) next to review metrics; governance helps: record decisions, make the checkable part an exact rule, check every change in CI or a pre-write hook, route the rest to owners |
| Cannibalisation | `find_overlap.py` on the chat's title and keywords: `stanford-ai-index-2026-engineering-governance` 119.3 (matches on "AI Index 2026"; different report, capability not review; no overlap of intent), `ai-code-review-does-not-scale-linearly` 85.9, `github-copilot-usage-based-billing-review-economics` 70.6, `why-code-review-cannot-scale-with-ai-output` 69.6, `cursor-developer-habits-report-governance-infrastructure` 67.3, `ai-coding-agent-verification-tax` 65.0, `what-is-the-ai-sdlc` 63.9, `atlassian-agentic-pivot-engineering-system-of-record` 57.4, `ai-coding-governance-should-be-reviewable` 46.5, `ai-native-sdlc-architecture-layer` 44.2; second query adds `concepts/ai-native-sdlc` 47.6, `how-ai-coding-agents-use-adrs` 42.6. All read. On the final title the top hit is Stanford at 67.3. **Verdict: re-angle.** The review-capacity thesis is owned by `why-code-review-cannot-scale-with-ai-output` and `ai-code-review-does-not-scale-linearly`, and `ai-code-comprehension-gap` already has "output doubled, review did not", a direct-database worked example and five decision indicators. The draft therefore does not re-argue review scaling (it links those pages in one paragraph). Its own contribution: (1) the Index's figures read with their samples and methods, (2) the point that every review metric in the Index counts speed or volume and none counts conformance, and survivorship is not a quality measure, (3) a pairing of the two Index-measured metrics with three proposed decision metrics. Decision protection coverage overlaps `ai-code-comprehension-gap`'s "decision coverage"; it is narrowed here to "recorded decisions with a machine check behind them", which is what the Audit reports. The worked example uses a domain/infrastructure import, not the comprehension-gap article's handler/database case. Agentic Pivot: linked and distinguished as a survey; the Index adds product data. No other brief in this batch was checked for overlap by this agent (orchestrator to compare). |
| Cross-links | out: `atlassian-agentic-pivot-engineering-system-of-record`, `why-code-review-cannot-scale-with-ai-output`, `ai-code-comprehension-gap`, `ai-engineering-roi`, `/audit/`, `/tools/adr-checker/`, `/integrations/`. Reciprocal in: Agentic Pivot, comprehension gap, why-code-review. `/concepts/governance-before-generation/` (chat's fourth link) not linked: the draft does not need it; add at the publisher's discretion. |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 39 after revision round 1 (directness 8, rhythm 8, trust 8, authenticity 7, density 8). First draft also 39; revised once before audit to remove an unsupported "most organizations" claim, a "not a flaw" contrast, an unsupported "improving fastest" claim and an over-quotable pull quote. |
| `lint_prose.py` | errors: 0; 3 warnings, justified: `SDLC` first appears inside the verbatim report name and is expanded in the same sentence (the built page's H1 will also precede it); `DX` is a company name; `CLI` is part of the product name "Codex CLI". Re-run on the built page. |
| Cold read: thesis as restated | "The Index measures review speed and volume, which show rising strain, but not whether changes respect architecture, so leaders should also track decision-protection metrics" (matches the brief) |
| Cold read: unclear terms, and how resolved | DX: described at first use (a platform organizations use to measure developer productivity and AI use). Typed rule and pre-write hook: defined in the worked example. Audit labels Protected / Mneme-ready / Requires modelling / Guidance: one short definition each. Mneme now introduced in plain words at the start of the worked example, so the closing section is not the first mention. Per-chart sample caveat moved from section 1 into the cautions paragraph as one sentence. |
| Pre-merge Opus claim audit | round 1: VERDICT FIX, 9 items; all 9 applied with the auditor's replacement text (Agentic Pivot described as a survey of 1,100+ professionals; "four figures bear on code review"; "between January and October" for the 74% rise, in body and reciprocal; reciprocal[0] no longer calls the Index a follow-up; Audit described as "the closest measure" with its actual formula, share of non-Guidance decisions that are Protected; protection coverage no longer called a count; "good first candidates"; "Automated review is growing too"). CTA tag `adr_check` confirmed valid (gtm-tagging-requirements.md). Re-audit pending. |

## Agreed scope

Thesis (from the chat): AI-generated code is growing faster than organizations can review, understand and govern it; more automated review helps, but keeping architectural intent needs authoritative decisions, enforcement and evidence during implementation. Do not compete with Atlassian on summarizing the report; explain what teams should do about it. Audience: engineering leaders. Chat outline: what the Index measures (and contrast with the Agentic Pivot); AI code volume vs review capacity (no causal claims); why automated review is not enough; from AI code review to AI code governance; five metrics (two DX-measured, three proposed, clearly separated); a worked example (domain layer must not import infrastructure adapters); close with the Architecture Protection Audit, secondary CTA the ADR checker. Target 1,500 to 1,900 words; the draft body is about 1,500 words including the FAQ, which is enough to answer the five questions without restating the linked review-capacity pieces.

SEO intent: primary evergreen topic "AI code governance"; Atlassian's name for topical and news relevance; secondary "AI SDLC", "AI code review", "why AI code needs human review" (FAQ). The chat's keyword volumes come from a tool the source step could not check; they were used only to choose target queries and appear nowhere in the copy.

Chat guardrails carried into the draft: metrics come from different cohorts and methods; the review-time link to AI share is observational; survivorship measures code remaining in commits, not safety or correctness.

## Key facts, figures, sources

All figures from one source: https://www.atlassian.com/blog/ai-sdlc-index ("The Atlassian AI SDLC Index", Inside Atlassian, data from DX; first published 2026-11-16, "Latest update 11.18.26", modified 2026-11-20; read 2026-11-22). Chart data is published as HTML tables, so no chart rendering was needed.

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| Sample: more than 340,000 engineers at 500+ engineering organizations that use DX; self-reported and telemetry data aggregated at company level | https://www.atlassian.com/blog/ai-sdlc-index | verified (Methodology) |
| Published Nov 16, updated Nov 18 | same | verified (JSON-LD datePublished 2026-11-16; lede "Latest update 11.18.26") |
| Chart samples range 180 to 630 companies | same | verified (AI use by task n=180; bot review n=630; others between) |
| 69.7% AI-authored code, Oct 2026, from 49% in Apr; self-reported; n=227 | same | verified ("How much code AI authors vs. how much survives") |
| 68.2% of AI-authored code survives (Oct); survivorship = share of AI-authored code that remains in commits, measured in product | same | verified (same chart and note) |
| PR reviews per active human reviewer per month 12.8 (Jan) to 22.3 (Oct); n=627 | same | verified ("Review load per developer over time": "Counts distinct PRs reviewed per active human reviewer"). "About three quarters" = 22.3/12.8 = 1.74, our arithmetic |
| Median minutes to first human review by AI share: 31.2 (20-40%), 66.6, 72.6, 97.8 (80%+); AI share self-reported, time from product data; n=441 | same | verified ("State of PR reviews") |
| 20% of work hours lost to friction, 409 hours a year; self-reported; n=475 | same | verified ("Friction"; table "Time lost to friction 20% 409 Hrs") |
| Review wait time 86.5 h/yr, tied with CI wait 86.5; code comprehension 71.5 | same | verified ("Hours lost per year, by source") |
| Bot review share 15.3% (Nov 2025) to 21.2% (Oct 2026), among companies using bot reviewers for >5% of PRs; n=630 | same | verified ("Share of PRs that get a bot review over time") |
| Architecture design and planning in 11.9% of AI sessions; shares exceed 100%; n=180 | same | verified ("AI use by task") |
| The Agentic Pivot was a survey of more than 1,100 software professionals, engineering leaders and individual contributors | https://mnemehq.com/insights/atlassian-agentic-pivot-engineering-system-of-record/ (cites https://www.atlassian.com/whitepapers/the-agentic-pivot) | verified against our own published, audited article (1,100+ professionals in Q2 2026: 364 leaders, 750 individual contributors, fielded by Prolific); wording supplied by the claim audit. Not on the Index page. |
| Semrush keyword volumes | none (authenticated tool) | not verified; used only to pick target queries, not in copy |

## Mneme claims and maturity

Checked against `/docs/how-enforcement-works/`, `/docs/how-to/adr-to-enforceable-decision/`, `/integrations/`, `/audit/methodology/`, `/tools/adr-checker/` and the audited wording in `ai-code-comprehension-gap`. Release in `scripts/core_version.json`: mneme-hq 0.11.0 minimum.

| Claim | SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL |
|---|---|
| Mneme is an open-source decision and control layer for agentic software development | SHIPPED (ADR-001 category statement; open source, MIT) |
| Mneme is an open-source tool that stores a team's architectural decisions in its repository and checks code changes against them (plain-words intro at the worked example) | SHIPPED (`/integrations/` lede uses the same description) |
| It does not replace code review and does not make judgment calls | SHIPPED (scope limit) |
| A decision is enforced when it carries an active typed rule: exact, case-sensitive text that must not appear in code, optionally limited to paths | SHIPPED (FORBID_LITERAL with include_paths) |
| A matching change returns a FAIL that names the decision behind it | SHIPPED (verdict records the matched rule and decision) |
| A decision without an active typed rule is not enforced | SHIPPED (limit) |
| Checks run in CI on pull requests | SHIPPED (GitHub Actions gate) |
| Checks run before a write in coding agents with a supported hook, such as Claude Code and Codex CLI | SHIPPED (Claude Code PreToolUse on Edit/Write/MultiEdit; Codex CLI on native apply_patch). Shell writes are not checked pre-write; the draft points to `/integrations/` for exact coverage |
| Worked example: FORBID_LITERAL `from app.infrastructure` scoped to `app/domain/`; FAIL in a pre-write hook stops the write, in CI fails the PR; an alias or relative import would not match | SHIPPED (illustrative configuration of shipped behaviour; the limit is true of literal matching) |
| The Architecture Protection Audit reads decisions recorded in a repository, sorts each as Protected, Mneme-ready, Requires modelling or Guidance (each defined in one clause), and reports the share of non-Guidance decisions already Protected; called "the closest measure" to decision protection coverage, not the same measure | SHIPPED (audit methodology: Current Protection = Protected / (Protected + Mneme-ready + Requires modelling)) |
| The free ADR checker sorts the statements in one pasted ADR into Mneme-ready, Requires modelling or Guidance | SHIPPED (`/tools/adr-checker/`) |
| Three proposed metrics (decision protection coverage, violations caught before merge, changes needing architectural judgment) | CONCEPTUAL (proposed, not validated, not measured by DX) |

Totals: 11 SHIPPED, 1 CONCEPTUAL, 0 VALIDATED EXPERIMENT, 0 PLANNED.

## Positioning constraints

Report response, not a summary of Atlassian's report and not a critique of it (the draft says the gap is in what any platform can count). No causal claim from the review-time chart. Survivorship never used as a quality or failure rate. Category stays ADR-001's; no new terminology. "Bottleneck" not used.

## Non-insight site edits requested

None. The chat recommends tracking Search Console and analytics at 30 and 60 days (AI code governance, AI SDLC, AI code review, Atlassian-branded queries; article-to-audit clicks and audit starts); other follow-ups are tracked privately.

## Open questions

- Owner: the chat's SEO title was "AI Code Governance: Atlassian AI SDLC Index 2026". ADR-015 requires the entity first, and the report name carries no year, so the draft uses "Atlassian AI SDLC Index: Review Is Measured, Architecture Is Not" and puts "AI code governance" in the description, body and FAQ. Confirm, or choose another hook after the entity.
- Publisher (optional, separate docs change): `adr_check` is valid per `docs/site/gtm-tagging-requirements.md` but missing from the stale list in `docs/site/cta-system.md` section 6.
