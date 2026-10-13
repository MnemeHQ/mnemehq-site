# Scope brief: Post-Writing ROI Content (unpublished backlog)

Status: **gathered, not built.** This chat must stay without `***` until the backlog ships or is dropped. **Never rename it.**

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Writing ROI Content` |
| Created / last updated (UTC) | 2026-09-08 / 2026-09-10 (local timestamps in chat: Tue Sep 8 8:04 AM; Thu Sep 10 2:37 PM) |
| Shape | Four user turns: ROI for senior leaders; pillar page scope (with a LeadDev link); supporting articles; "Include stats" (a screenshot-driven turn, FT/NBER). |
| Already shipped from this chat | `ai-engineering-roi` (pillar) and `ai-throughput-is-not-engineering-throughput`, PR #135. The pillar already uses the LeadDev 28x spend / 58% feature-work stats. |

## Build card

One row per buildable article. All go on the **engineering-performance** hub (where the pillar and its shipped spokes sit), eyebrow Analysis, and must link up to `ai-engineering-roi`. Proposed values; confirm before building.

| Article | Slug | Report-anchored | OG headline | Gate |
|---|---|---|---|---|
| AI Can Raise Coding Activity 240%. Why Do Releases Rise Only 30%? | n/a | n/a | n/a | **already shipped**: `ai-throughput-is-not-engineering-throughput` (#135) is this article (NBER 240% → 30% in its description, lede and image alt); do not build |
| How to Measure AI Coding ROI Without Counting Lines of Code | `measure-ai-coding-roi-without-lines-of-code` | no | Measure AI ROI Without LOC | pass: distinct query |
| The Hidden Cost of AI-Generated Rework | `hidden-cost-ai-generated-rework` | no | The Hidden Cost of AI Rework | re-angle vs `ai-coding-productivity-gains-rework` |
| When AI Saves Developer Time but Creates More Work for Senior Engineers | `ai-saves-developer-time-senior-engineer-work` | no | AI's Hidden Senior-Engineer Tax | pass: distinct query |
| 28x More AI Spend. Where Is the Engineering ROI? | `28x-ai-spend-engineering-roi` | yes: entity = LeadDev/DX report (verify name) | 28x AI Spend, Flat Features | check overlap: the pillar already leads with these stats |
| Architectural Drift Is an AI ROI Leak | `architectural-drift-ai-roi-leak` | no | Architectural Drift Leaks AI ROI | pass: cornerstone support (drift prevention) |
| What CTOs Should Measure Before Renewing Their AI Coding Tools | `what-ctos-measure-before-renewing-ai-coding-tools` | no | Before You Renew AI Tools | re-angle vs `github-copilot-usage-based-billing-review-economics` |
| You Bought the AI Agents. What Should You Measure Now? | `bought-ai-agents-what-to-measure` | no | You Bought Agents. Now Measure | likely merge into the CTO-renewal article (same intent) |
| The Economics of Preventing an Incompatible Change | `economics-preventing-incompatible-change` | no | Prevention Beats Rework Economics | hold until pilot data exists |
| From AI Adoption to AI Value: A Maturity Model | `ai-adoption-to-ai-value-maturity-model` | no | From AI Adoption to Value | likely drop: overlaps `ai-adoption-maturity-model-engineering-analysis` |
| AI Can Write 3x More Code. Why Isn't 3x More Software Shipping? | n/a | n/a | n/a | drop: same finding as the shipped `ai-throughput-is-not-engineering-throughput` |

**Cannibalisation (`find_overlap.py`, 2026-10-12), overriding the Gate column where they differ:**

| Article | Top hit (score) | Verdict |
|---|---|---|
| 240% / 30% (NBER) | `ai-throughput-is-not-engineering-throughput` 76.1 (after the 2026-10-12 scoring fix; it was missed at 30.6 before) | **already shipped: drop** |
| Measure AI Coding ROI Without LOC | `ai-engineering-roi` 80.7 (the pillar is already "How to Measure the Real Return") | **merge or drop**: fold the scorecard into the pillar |
| Hidden Cost of AI-Generated Rework | `ai-coding-productivity-gains-rework` 72.1, `use-cases/ci-governance-for-ai-generated-code` 72.6 | **re-angle or drop**: only the "unattributed downstream hour" accounting angle is new |
| Senior Engineers | `ai-coding-agent-verification-tax` 54.3 | re-angle: redistribution of work to Staff/Principal only, not review volume |
| Drift Is an ROI Leak | `ai-roi-problem-is-about-systems-not-models` 57.9 | re-angle: drift as one named leak, link the systems essay |
| CTO renewal | `ai-coding-governance-should-be-reviewable` 56.0, `ai-engineering-roi` 47.9 | clear if it stays a buying-decision checklist |

Five questions are shared across the cluster: changed: AI spend and coding activity rose sharply; matters: delivered value did not rise in step; breaks: gains are absorbed by review, rework and reconciliation; do: measure generation, delivery and governance layers separately; governance: prevent incompatible changes before they cost review time (kept to 10-20% of each piece).

## Backlog status against the repo (checked 2026-10-12)

| Article | Priority in chat | Repo status |
|---|---|---|
| How to Measure AI Coding ROI Without Counting Lines of Code | P0 | Not in `site/insights`. Unbuilt. |
| The Hidden Cost of AI-Generated Rework | P0 | Not built. Adjacent: `ai-coding-productivity-gains-rework`. Differentiate. |
| When AI Saves Developer Time but Creates More Work for Senior Engineers | P0 (P1 in the stats table) | Unbuilt. |
| Architectural Drift Is an AI ROI Leak | P1 | Unbuilt. |
| What CTOs Should Measure Before Renewing Their AI Coding Tools | P1 | Unbuilt. Adjacent: `github-copilot-usage-based-billing-review-economics`. |
| The Economics of Preventing an Incompatible Change Before It Is Written | P2 | Unbuilt. Retitled in the stats table as "The Economics of Preventing a Bad Architectural Change Before It Is Written". |
| From AI Adoption to AI Value: A Maturity Model for Engineering Organizations | P2 | Unbuilt, but **`ai-adoption-maturity-model-engineering-analysis` already exists**. Check overlap before building. |

**New articles scoped in the Sep 10 "Include stats" turn that are NOT in the ledger's list** (confirmed absent from `site/insights`):

| Article | Priority | Statistical hook |
|---|---|---|
| AI Can Raise Coding Activity 240%. Why Do Releases Rise Only 30%? | P0, "first article after the pillar" | **already shipped** as `ai-throughput-is-not-engineering-throughput` (#135) |
| 28× More AI Spend. Where Is the Engineering ROI? | P0 | LeadDev/DX: median quarterly AI spend ~$1,500 → $44,000, feature work ~58% |
| You Bought the AI Agents. What Should You Measure Now? | P1 | LeadDev: 90% of organisations pay for AI models; about two-thirds pay for both autonomous agents and completion |
| AI Can Write 3× More Code. Why Isn't 3× More Software Shipping? | suggested in the turn-3 reply | drop: same finding as the shipped `ai-throughput-is-not-engineering-throughput` |

Already shipped, so **drop from the backlog**: "The Verification Tax of AI Coding Agents" (`ai-coding-agent-verification-tax`) and DORA metrics (`dora-metrics-insufficient-for-agentic-development`). The chat listed both as supporting articles; they already exist.

## Agreed scope

- **Editorial guardrail (verbatim intent):** keep the cluster ~60-70% neutral executive/engineering economics, ~20-30% governance-specific, only ~10-20% explicitly Mneme/audit. Write standalone economics pieces, not governance pitches. Otherwise readers and editors read the cluster as product marketing.
- **Audience for the whole cluster:** CTOs, VPEs, Heads of Engineering, platform leaders, technically literate CIOs. Pages must be intelligible without knowing ADRs, RAG or Mneme.
- **Core claims the cluster owns:** "AI throughput is not engineering throughput"; the unit of AI coding ROI is "production-ready change", not code generated; "developer acceleration is an input, engineering ROI is an outcome".
- **Do not attack developer-productivity metrics**; they are useful leading indicators, not sufficient ROI metrics.
- **Do not claim architectural drift explains the whole generation-to-release gap.** The narrower claim: architectural reconciliation is one downstream cost that standard AI productivity measures fail to expose, and one that systems can prevent.
- One memorable number in each article's opening.

### Per-article notes from the chat

- **How to Measure AI Coding ROI Without Counting Lines of Code** (P0, search workhorse). Scorecard: generation → delivery → rework/quality → governance → business outcome. Candidate metrics: accepted/generated change, first-pass PR acceptance, rework rate, review time, CI retry rate, architectural-policy violation rate, lead time to production, incidents attributable to AI-generated changes, senior-engineer time spent correcting AI work. Hook: only 6% of executives in the cited Atlassian research say they can identify organisation-wide AI ROI. Net-value model: gross AI productivity gain − review overhead − rework − CI/remediation − architecture correction − operational consequences = net AI engineering ROI.
- **The Hidden Cost of AI-Generated Rework** (P0, "may be the commercially strongest"). Premise: a coding assistant can save 30 minutes during implementation while creating an hour of work somewhere nobody attributes to the AI tool. Break into review → clarification → architecture correction → CI → rewrite → re-review. CTA: Run the Architecture Audit. Pair LeadDev's absorption of gains at review/approvals/CI/rework with the NBER attenuation.
- **When AI Saves Developer Time but Creates More Work for Senior Engineers** (P0/P1). Attack the measurement blind spot, not AI itself. Illustration in the chat: a developer reports being 40% faster while staff-engineer review time rises, architecture debates move into PRs, more incompatible work reaches CI, more work is abandoned or rewritten. **That illustration is hypothetical; do not present it as data.** Stats hook: NBER's estimated elasticity of substitution of 0.23 between AI and human effort (read as strong complementarity).
- **Architectural Drift Is an AI ROI Leak** (P1). Start with the macro gap, then state the qualification.
- **What CTOs Should Measure Before Renewing Their AI Coding Tools** (P1). Seven diagnostic questions listed in the chat's pillar section (generation throughput; production throughput; review time; rework; defects/change failures; senior time correcting AI-generated decisions; can architectural decisions be checked automatically before entering review).
- **The Economics of Preventing an Incompatible Change** (P2). Reactive flow (agent → incompatible implementation → tests → PR → senior reviewer finds it → rewrite) vs preventive flow (decision → machine-evaluable constraint → block → compatible implementation). "Can contain an actual cost model later once we have pilot data" so no invented numbers.
- **From AI Adoption to AI Value: A Maturity Model** (P2). Six levels: 0 Spend, 1 Adoption, 2 Productivity, 3 Delivery, 4 Quality, 5 Governed ROI. "Most AI dashboards stop between Levels 1 and 2."
- **Pilot data:** none exists yet, so no article in this cluster may state Mneme ROI figures; the prevention-economics piece waits for real data.

## Key facts, figures, sources

URLs verbatim from the chat with `?utm_source=chatgpt.com` stripped. **All unverified** until re-read.

| Fact | Source |
|---|---|
| Median quarterly AI spend ~$1,500 → ~$44,000 (~28×); feature work ~58% unchanged; 6% of executives (via Atlassian) confident of org-wide AI ROI; 90% pay for AI models, ~two-thirds pay for both autonomous agents and completion | https://leaddev.com/ai/28x-more-ai-spend-zero-new-innovation (the chat's rendered citations also show https://zephrcf.leaddev.com/ai/28x-more-ai-spend-zero-new-innovation, which looks like a CDN mirror; use the first) |
| NBER working paper, revised Sept 2026, 500,000+ GitHub developers: cumulative coding-activity gain +30% autocomplete, +180% interactive agents, +240% autonomous agents; attenuating to +80% at project level and +30% at release level; elasticity of substitution 0.23 | https://www.nber.org/papers/w35275 |
| Earlier FT reporting: ~+300% files created/edited, +150% work submitted for review, ~+30% releases; steam-to-electricity factory-redesign analogy | https://www.ft.com/content/734d7178-94a7-4139-918d-7df9f4df4b65 |
| Microsoft EngThrive treats productivity as multidimensional (speed, ease, quality, developer experience) | https://commandline.microsoft.com/engineering-thrive-engthrive-productivity-measurement-framework-agentic-ai-era/ |
| Competing pages already targeting "AI engineering ROI" / "AI coding ROI" | https://snowmanlabs.com/insights/how-to-measure-ai-engineering-roi |
| Mneme internal links the chat used | https://mnemehq.com/insights/ai-roi-problem-is-about-systems-not-models/ ; https://mnemehq.com/concepts/architectural-drift-prevention/ ; https://mnemehq.com/audit/ |

**Chat's own warnings to carry over:** the NBER paper is "actively being revised": cite the current version and do not build marketing around a single number; use 240% → 80% → 30% as canonical, not the FT's ~300% / ~150% / ~30%. The stats come from different studies, so never present them as one causal funnel; label as "signals from recent AI engineering research".

## Mneme positioning constraints

- Governance/Mneme share capped at ~10-20% of the cluster; neutral economics first.
- Mneme legitimately says only: AI raised the rate of code production; the next challenge is raising the rate of trustworthy, architecture-compatible code moving through delivery. Mneme addresses one slice (architectural review, rework and governance), not the whole generation-to-release gap.
- No ROI claims about Mneme ("reduced rework by X%") until pilot data exists.
- Governance-layer metrics (e.g. "percentage of decisions mechanically protected") should be tied to what the Architecture Audit actually outputs: Protected / Mneme-ready / Requires modelling / Guidance (the shipped tiers, ADR-026 and `/audit/`).

## Non-insight site edits requested

None in this chat beyond the pillar, which is shipped.

## Open questions

- Build order: the NBER article the chat wanted first already shipped as `ai-throughput-is-not-engineering-throughput`. Does the ledger's P0 order (measurement, rework, senior-engineer) still hold?
- The pillar `ai-engineering-roi` already cites the NBER figures (240% coding activity, 30% releases); no update needed for them.
- Which articles to explicitly drop (the maturity model overlaps an existing page).

## Unverified / needs checking

- Every figure in the sources table, especially the NBER numbers and the 0.23 elasticity (re-read the revised PDF), and the FT URL (the ledger already records an earlier FT citation that could not be located; check this one resolves).
- Atlassian "6%" is quoted second-hand through LeadDev; trace to Atlassian's own report or attribute it only to LeadDev.
- DX as the source of the spend data is attributed via LeadDev only.
