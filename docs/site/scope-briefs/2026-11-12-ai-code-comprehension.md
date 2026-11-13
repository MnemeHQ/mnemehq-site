# Scope brief: Post- AI code comprehension

Status: **built, queued for 2026-11-16** (`ai-code-comprehension-gap`; article PR on its own `site/` branch)

| Field | Value |
|---|---|
| ChatGPT chat | `Post- AI code comprehension` |
| Created / last updated (UTC) | 2026-11-12 / 2026-11-12 |
| Shape | 2 user turns, 2 assistant turns; read in full, no "Show more" truncation remained. Turn 1 scopes the article; turn 2 asks whether a concept page is also needed and recommends one. |
| Repo check | Related pages exist: `gartner-architectural-technical-debt-ai-coding-agents`, `ai-native-engineering-intent-debt`, `ai-code-review-does-not-scale-linearly`, `ai-coding-agent-verification-tax`, `/concepts/intent-debt/`, `/concepts/engineering-coherence/`, `/concepts/agent-verification/`. No page uses "comprehension gap" or "comprehension debt". |

## Build card

| Field | Value |
|---|---|
| Kind | insight (concept page held, see Non-insight site edits) |
| Title | When AI Builds Faster Than Engineers Can Understand |
| Slug | `ai-code-comprehension-gap` |
| Report-anchored (ADR-015) | no |
| Topic hub | engineering-performance |
| Content type (`--type`) | Analysis |
| OG headline | AI Outpaces Engineering Comprehension (4 words) |
| Editorial gate | pass: distinct query (AI-generated code maintainability, AI technical debt) plus new evidence for the decision-governance thesis (separates implementation, verification and comprehension) |
| Five questions | changed: agents raise change volume faster than teams can explain it; matters: understanding of why a change exists does not scale with agent count; breaks: tests pass while architectural intent and decision authority are lost; teams should: track decision traceability, not only throughput; governance helps: persisted decisions, checks where a rule is checkable, inspectable evidence |
| Cannibalisation | `find_overlap.py` on title and keywords: `gartner-architectural-technical-debt-ai-coding-agents` 127.2, `ai-coding-agent-verification-tax` 63.9, `ai-native-engineering-intent-debt` 61.0, `ai-code-review-does-not-scale-linearly` 60.5. Verdict: **re-angle**. The article must not re-explain drift, intent debt or review load. Its own contribution is the three-way split (implementation, verification, comprehension) and the candidate decision-traceability measures. Body search for the figures found no existing use of the 2.09x, 11.8% or 278,790 figures. |
| Cross-links | `ai-coding-agent-verification-tax`, `ai-native-engineering-intent-debt`, `ai-code-review-does-not-scale-linearly`, `/concepts/engineering-decision-governance/` |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 38 |
| `lint_prose.py` | errors: 0 on the built page; 0 warnings |
| Cold read: thesis as restated | "AI doubled output but nobody checks the team still understands why the system looks as it does" (matches the brief) |
| Cold read: unclear terms, and how resolved | overlapping review shares explained; table wording and section heading corrected; 85% figure given its meaning; typed rule removed from the mid CTA |
| Pre-merge Opus claim audit | blockers and should-fix items applied; see the article PR |

## Agreed scope

Thesis: implementation velocity is exceeding human comprehension velocity. Audience: CTOs, VPs Engineering, platform leaders, architects. 1,500 to 2,000 words, evidence-led. Structure from the chat: (1) generation outran comprehension; (2) what comprehension means (reading code vs understanding why a boundary exists, what was rejected, who may change it); (3) why code review cannot close the gap alone; (4) from comprehension debt to drift, with one worked example (an agent reads a database directly, bypassing the service API; tests pass; later agents copy the pattern); (5) scale decision governance, not only review; (6) decision traceability as the next metric.

Chat's own qualification, to keep: the evidence shows rising throughput and review pressure, not a measured fall in comprehension. Present the gap as a reasoned hypothesis. The chat's formula G(t) = I(t) - C(t) is a conceptual model, not a validated metric; state that, and propose indicators (decision coverage, decision-to-change traceability, unresolved exceptions, architectural rework rate, decision recovery time) as candidate measures only.

Rule from the chat: three things before publication: the empirical evidence, one worked scenario, and a falsifiable framework.

## Key facts, figures, sources

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| 802 developers, 196,212 PRs (Jan 2024 to Apr 2026); per-engineer PR throughput 2.09x baseline; reviewer workload about doubled; automated review overtook human review in coverage | https://arxiv.org/abs/2607.01904 | verified (abstract; Sec. IV-A RQ1, IV-C RQ3, Fig. 6). Differs on nuance: 2.09x is mean authored PRs per *active* developer, 21.2 (Jan-Apr 2025 baseline) to 44.3 (Apr 2026), on a 564-developer subsample with 3+ active months; the company's own metric (merged PRs per engineer) gives 2.31x. Reviewer load "roughly doubled (2.0x)" is a derived ratio: PR volume 3.1x over baseline divided by reviewer pool 1.5x. Review coverage: PRs with a human review fell 89% to 68%; PRs with an automated AI review rose about 19% to about 84%. Single AI-forward company, not randomised; authors call the estimates an upper bound, not an industry average. Preprint, no venue or peer-review status listed. |
| Paper identity: "AI Writes Faster Than Humans Can Review: A Longitudinal Study of an Enterprise 2x Mandate", Hao He, Shyam Agarwal, Yegor Denisov-Blanch, Pavel Azaletskiy, Sanmi Koyejo, Bogdan Vasilescu; arXiv 2607.01904 (cs.SE, CC BY 4.0), v1 2 Jul 2026, v3 10 Nov 2026 | https://arxiv.org/abs/2607.01904 | verified (arXiv listing). Cite as an arXiv preprint; figures checked against v3 text and v1 abstract summary |
| Google DORA 2025: 90% of surveyed professionals use AI at work; AI now improves delivery throughput but still increases delivery instability | https://dora.dev/research/2025/dora-report/ (report PDF: https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf) | verified (report PDF Executive summary, p. 4: "The majority of survey respondents (90%) use AI as part of their work"; "AI adoption now improves software delivery throughput ... However, it still increases delivery instability"). Survey of "nearly 5,000 technology professionals", fielded 13 Jun to 21 Jul 2025. Report title "State of AI-assisted Software Development 2025", DORA (Google Cloud), PDF dated Oct 2025 (v. 2025.2); Google announcement 23 Sep 2025. Also reports 30% with little to no trust in AI-generated code |
| DORA: time saved on generation moves to auditing and verification | https://dora.dev/insights/balancing-ai-tensions/ | differs: the 2025 report does not say "time saved is reallocated to auditing". Report PDF p. 40 (Friction): friction "shifts from manual grind to deciding and verifying", and more change volume "could increase verification and coordination costs"; it says this "could net out to roughly no change in total friction". The "time saved ... re-allocated to verification overhead" wording is in the DORA insight article "Balancing AI tensions" (Jessica Baolin, Nathen Harvey, 10 Mar 2026), which cites the 2025 report. Cite each for what it says |
| 278,790 review conversations; human reviewers ran 11.8% more rounds on AI-generated code | https://arxiv.org/abs/2603.15911 | verified (abstract; Sec. III-B RQ2). Nuance: sample is inline review conversations from 300 mature open-source GitHub projects (54,330 closed PRs, 2022 to Nov 2025), not enterprise code. 11.8% compares human reviews of AI-generated code (HRA) with human reviews of human code (HRH, average 1.76 rounds); HRA is only 6,519 of the 278,790 conversations. Paper words it as "rounds" in abstract and "comments" in one body sentence. No statistical test reported for the 11.8%. Preprint, comments field "13 pages, 6 figures, 14 tables", no journal reference |
| Paper identity: "Human-AI Synergy in Agentic Code Review", Suzhen Zhong, Shayan Noei, Ying Zou, Bram Adams; arXiv 2603.15911 (cs.SE), v1 16 Mar 2026, v3 30 Oct 2026 | https://arxiv.org/abs/2603.15911 | verified (arXiv listing) |
| Same paper: 85-87% of AI-initiated reviews end after the first comment with no follow-up (precisely 85.2 to 86.7%) | https://arxiv.org/abs/2603.15911 | verified (Sec. I RQ2 and Sec. III-B); optional extra fact, no statistical test reported |

## Mneme claims and maturity

| Claim | SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL |
|---|---|
| Decision Index persists decisions across sessions | to classify at audit against current docs |
| Enforcement before a write, where an integration supports it, plus a CI backstop | to classify at audit; keep literal about supported paths |
| Evidence distinguishing declared intent from verified compliance | to classify at audit |
| The comprehension-gap model and the five indicators | CONCEPTUAL (not Mneme-validated metrics) |

## Positioning constraints

Governance preserves understanding and decision authority; it does not remove the need for human comprehension. Ambiguous, conflicting or non-checkable decisions still need human judgment. Not a product pitch. Keep the O'Reilly ADR study separate.

## Non-insight site edits requested

A concept page, "Implementation-Comprehension Gap" at `/concepts/implementation-comprehension-gap/` (700 to 1,000 words), was recommended in turn 2. **Held**: a new concept term needs an owner decision and a PUBLISHING.md terminology amendment first (the 2026-10-12 and 10-14 decisions allow only "engineering decision governance" and "engineering coherence" as concept terms). Use "comprehension gap" descriptively in the article. Do not add "comprehension debt" as a term (the chat itself advises against it).

## Open questions

Owner: confirm the concept page stays held. Build: find and verify the three studies before any figure is written.
