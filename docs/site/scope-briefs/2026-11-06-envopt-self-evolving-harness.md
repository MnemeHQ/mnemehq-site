# Scope brief: Post-EnvOpt assessment

Status: **gathered, not built**

| Field | Value |
|---|---|
| ChatGPT chat | `Post-EnvOpt assessment` |
| Created / last updated (UTC) | 2026-11-06 / 2026-11-06 |
| Shape | 1 user turn, 1 assistant turn; read in full, no truncation. The turn asks whether to scope an article on self-evolving harnesses and answers with a brief. |
| Repo check | Harness pages exist: `what-is-harness-engineering`, `harness-engineering-still-needs-governance`, `harness-engineering-verification-layer`, `runtime-harnesses-for-ai-agents`, `prompt-engineering-vs-harness-engineering`, `deepseek-agent-model-harness-architectural-governance`, `anthropic-recursive-self-improvement-engineering-governance`, `recursive-self-improvement-orchestration-problem`. None covers authorization of a harness's own changes. |

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | Self-Evolving Agent Harnesses: Who Governs the Changes? |
| Slug | `self-evolving-agent-harness-governance` |
| Report-anchored (ADR-015) | no (Thoughtworks Radar is context, not the subject; revisit if the Radar entry becomes the lede) |
| Topic hub | agent-infrastructure |
| Content type (`--type`) | Analysis |
| OG headline | Who Governs Self-Evolving Harnesses? (4 words) |
| Editorial gate | pass: distinct query (self-evolving agent harness, harness evolution) plus a named-source entry point (Thoughtworks Technology Radar, Nov 2026) |
| Five questions | changed: harnesses now rewrite their own tools, instructions, memory and workflows from execution traces; matters: a better benchmark score does not show the old constraints still hold; breaks: the optimizer removes a validation step because that raises completion speed; teams should: treat harness changes as proposed until approved, and test against held-out regressions; governance helps: versioned decision authority decides which constraints an optimizer may not rewrite |
| Cannibalisation | `find_overlap.py`: `claude-code-self-hosted-environments-architectural-governance` 41.4 to 45.0, `recursive-self-improvement-orchestration-problem` 37.7, `deepseek-agent-model-harness-architectural-governance` 36.0, `runtime-harnesses-for-ai-agents` 36.0. Verdict: **clear**, with a hard rule: cover the lifecycle and authorization of harness modifications only; do not restate the general harness-governance case. Check the two recursive-self-improvement pages for shared claims before drafting. |
| Cross-links | `harness-engineering-still-needs-governance`, `what-is-harness-engineering`, `recursive-self-improvement-orchestration-problem` |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | errors: 0; warnings fixed or justified: |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

## Agreed scope

Thesis: optimizing an agent's capabilities is different from authorizing changes to its operating rules. The optimizer may propose; it must not decide that an approved constraint no longer applies. Audience: CTOs, platform engineers, AI infrastructure architects, framework developers. 1,400 to 1,800 words. Structure: (1) what a self-evolving harness is (execute, observe, propose, evaluate, promote, repeat; distinct from model training and environment optimization); (2) why now (Thoughtworks, Evo-Harness, Self-Harness, EnvOpt, multi-objective work); do not generalize benchmark gains to production; (3) risks: reward hacking, regression, forgotten constraints, altered tool permissions, instruction drift, contaminated knowledge; (4) governance architecture: independently governed decisions, versioned authority, proposed vs approved changes, held-out regression tests, enforcement checks, audit evidence; (5) how Mneme fits, without implying it governs every harness configuration or supports autonomous optimization today. Worked example: the optimizer proposes removing a validation step, scores higher, and violates an approved constraint. Include a control-flow example and an explicit split between current Mneme capability and proposed extension.

## Key facts, figures, sources

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| Thoughtworks Technology Radar, 4 Nov 2026, classes self-improving harnesses as Trial, advising bounded experiments and regression testing | unverified: find the Radar entry | unverified |
| EMNLP 2026 work on Evo-Harness / harness self-evolution | unverified: find the ACL Anthology entries | unverified |
| EnvOpt (5 Nov) on optimizing agents' information environments | unverified: find the paper | unverified |
| "Self-Harness" and multi-objective optimization work | unverified: chat gives no title or URL; cut if not found | unverified |

## Mneme claims and maturity

| Claim | SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL |
|---|---|
| Decision authority constrains a harness-modifying optimizer | CONCEPTUAL (no harness-optimizer integration shipped) |
| Versioned decisions, enforcement where supported, evidence | to classify at audit against current docs |

## Positioning constraints

Technical authority article, not a sales piece. No claim that Mneme supports autonomous harness optimization. The chat's SEO keywords are unvalidated; do not quote volumes.

## Non-insight site edits requested

None.

## Open questions

Chat suggests publishing the week of 2026-11-09 while the Thoughtworks entry is fresh; that date has passed, so queue it first after verification.
