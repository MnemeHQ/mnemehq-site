# Scope brief: Post- AI code comprehension

Status: **gathered, not built**

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
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | errors: 0; warnings fixed or justified: |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

## Agreed scope

Thesis: implementation velocity is exceeding human comprehension velocity. Audience: CTOs, VPs Engineering, platform leaders, architects. 1,500 to 2,000 words, evidence-led. Structure from the chat: (1) generation outran comprehension; (2) what comprehension means (reading code vs understanding why a boundary exists, what was rejected, who may change it); (3) why code review cannot close the gap alone; (4) from comprehension debt to drift, with one worked example (an agent reads a database directly, bypassing the service API; tests pass; later agents copy the pattern); (5) scale decision governance, not only review; (6) decision traceability as the next metric.

Chat's own qualification, to keep: the evidence shows rising throughput and review pressure, not a measured fall in comprehension. Present the gap as a reasoned hypothesis. The chat's formula G(t) = I(t) - C(t) is a conceptual model, not a validated metric; state that, and propose indicators (decision coverage, decision-to-change traceability, unresolved exceptions, architectural rework rate, decision recovery time) as candidate measures only.

Rule from the chat: three things before publication: the empirical evidence, one worked scenario, and a falsifiable framework.

## Key facts, figures, sources

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| 802 developers, 196,212 PRs, per-engineer PR throughput 2.09x baseline, reviewer workload about doubled (July 2026 enterprise adoption study) | unverified: chat names no URL; find the arXiv paper | unverified |
| Google DORA 2025: 90% of surveyed professionals use AI; time saved moves to auditing and verification | unverified: find the DORA 2025 report page | unverified |
| 278,790 review conversations; human reviewers ran 11.8% more rounds on AI-generated code (March 2026, "Human-AI Synergy in Agentic Code Review") | unverified: find the arXiv paper | unverified |

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
