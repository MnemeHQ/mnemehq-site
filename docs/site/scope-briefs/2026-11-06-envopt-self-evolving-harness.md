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
| Thoughtworks Technology Radar, 4 Nov 2026, classes self-improving harnesses as Trial, advising bounded experiments and regression testing | https://www.thoughtworks.com/radar/techniques/self-improving-harness (fetched via the /en-ca/ path; page says Published Nov 04, 2026) | verified (blip page): blip is named "Self-improving harness", quadrant Techniques, ring Trial, no authors listed, new/moved status not shown. Volume 35 is inferred from the PDF filename, not stated on the page. Advice (paraphrased): bounded experiments with regression testing; humans set objectives and modification boundaries and judge whether improvements generalize to new tasks. Chat was right |
| Radar blip content: what the entry covers | same URL | verified (blip page): agents analyze execution traces and evaluation feedback, then propose or make changes to prompts, context strategies, workflows, skills, tools, memory and middleware. Builds on "Feedback flywheel" (also Trial, Techniques, Nov 2026), which still relies on humans to interpret feedback. Cites Meta-Harness and VERSE as newer research toward self-directed improvement (VERSE also evolves the optimizer's own tools). Examples named: Pi's extensions, Claude Code Mods, DeepSeek Harness (DSH). Quote only short phrases; paraphrase the rest |
| Related Radar blips, same edition | https://www.thoughtworks.com/radar/techniques/feedback-flywheel ; DSH and Pi on the Tools quadrant | partly verified: the self-improving-harness page lists Feedback flywheel = Trial/Techniques, DeepSeek Harness (DSH) = Assess/Tools, Pi = Trial/Tools, all Nov 2026. Feedback-flywheel and DSH pages themselves not opened |
| EMNLP 2026 work on Evo-Harness / harness self-evolution | https://aclanthology.org/2026.emnlp-main.969/ | verified (ACL Anthology page): "Evo-Harness: Context-to-Harness Skill Compilation for Self-Evolving Agents", Tianxin Wei et al. (17 authors, Hanqing Lu last), EMNLP 2026 main (Budapest), Oct 2026, pp. 22343-22358, DOI 10.18653/2026.emnlp-main.969. Frozen agent updates a structured harness over sequential tasks ("online harness learning"); compiles noisy single-shot runs into reusable skill harnesses. Evaluated on TerminalBench2, SWE-bench, CL-Bench, tau-bench, WebArena-Infinity. Abstract on the page reports no headline numbers. Preprint: https://arxiv.org/abs/2608.15071 (not opened; ID from search only) |
| Second EMNLP 2026 paper, relevant counterpoint | https://aclanthology.org/2026.emnlp-main.2326/ | verified (ACL Anthology page): "Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents", Minhua Lin et al., EMNLP 2026 main, Oct 2026, pp. 52829-52852. Finding: producing harness updates (roughly flat across model tiers) is separate from benefiting from them (non-monotonic: weak models gain little, mid-tier most, strong less than mid-tier). Chat did not mention this paper |
| EnvOpt (5 Nov) on optimizing agents' information environments | https://arxiv.org/abs/2611.07372 | verified (arXiv abs, v1): "EnvOpt: Automated Optimization for Agent Environments", Mingxuan Li, Huanzhi Mao, Qiuyang Mang, Hanchen Li, Joseph E. Gonzalez, Alex Dimakis; submitted 5 Nov 2026 03:16 UTC; cs.AI/cs.CL. Preprint, no venue, not peer reviewed. Affiliations not on the abstract page (acknowledgements name U Chicago, UC Berkeley Sky Computing Lab, Bespoke Labs) |
| EnvOpt idea | https://arxiv.org/html/2611.07372 | verified (abstract, intro): optimizes "stationary environments" (shared workspaces and data sources agents operate in) as a third lever alongside model parameters and harness design; end-to-end, on real or synthetic tasks, no graders or reference answers. Note: environment optimization, not harness self-modification; keep it distinct as the brief already says |
| EnvOpt headline numbers | https://arxiv.org/html/2611.07372 | verified (abstract, Sec. 3), with caveats: Claude Haiku 4.5 on AutomationBench, cost -72.7%, pass rate +14.34% (Sec. 3 says 14.3%); same environment on Opus 5, cost -68.1%, +1.34%; Haiku 4.5 with Meta-Harness's harness, further -83.4% cost, +11.17% accuracy over Meta-Harness alone. Source does not say whether pass-rate gains are relative or absolute points; do not state which. Intro cites 16% for the Meta-Harness combination, conflicting with the abstract's 11.17%. Intro average cost reduction 48% across benchmarks on unseen test sets. Author-reported only; use sparingly or omit (article is about governance, not these gains) |
| "Self-Harness" | https://arxiv.org/abs/2606.09498 | verified (arXiv abs): "Self-Harness: Harnesses That Improve Themselves", Hangfan Zhang, Shao Zhang, Kangcong Li, Chen Zhang, Yang Chen, Yiqun Zhang, Lei Bai, Shuyue Hu. v1 8 Jun 2026, v3 20 Aug 2026. Preprint, no venue named. Loop: mine failure patterns from execution traces, propose minimal harness edits, accept edits only after regression testing. Models MiniMax M2.5, Qwen3.5-35B-A3B, GLM-5; benchmarks Terminal-Bench-2.0, SWE-bench Verified, AppWorld; every final harness improved held-in and held-out pass rates, relative gains up to 132%. Useful for the article: the accept-only-after-regression-testing gate is part of the method itself. Full text not opened |
| Multi-objective harness optimization work | https://arxiv.org/abs/2610.15150 ; https://arxiv.org/abs/2611.02079 | differs: chat named no paper, but two exist. (1) "Harmony Harness: Multi-Objective Self-Evolution of Agent Harnesses", Weichen Yu et al., 10 Oct 2026, no venue; decomposition-based evolutionary search over the Pareto frontier; "gains exceeding 10%" on SecRepoBench and BaxBench; abstract does not name the objectives. (2) "ParetoSaddler: Pareto-Guided Optimization of Agent Harnesses for Quality and Cost", Xingzhi Qian et al. (Microsoft-linked project site aka.ms/ParetoSaddler-website; affiliation not on abstract page), 1 Nov 2026, no venue; ClawMark quality 70.86% to 81.35%, cost $1.17 to $1.01 per task; GAIA2 quality 56.22% to 62.89%, cost $0.78 to $0.45 per task. Both abstract pages only; cite as preprints |

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
