# Scope brief: Post-Databricks AI Assessment

Status: **gathered, drafted, not built** (draft `databricks-ai-index-architectural-conformance`; revision round 1 applied after cold read and claim audit)

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Databricks AI Assessment` |
| Created / last updated (UTC) | 2026-11-16 / 2026-11-16 (creation date inferred from the project list and the in-chat "Monday" stamp; not exposed directly) |
| Shape | 8 turns (4 user, 4 assistant); truncation check passed, no "Show more" marker. Turn 1 assesses the Index for Mneme; turns 2 and 3 are social and roadmap follow-ups (not site work); turn 4 scopes one P1 article. The scope is expanded in site issue #316 (internal tracking, not a source). |
| Repo check | No page mentions the Databricks AI Index or Unity Gateway. Same-thesis pages exist: `smart-routing-ai-coding-agents` (routing does not solve architectural consistency), `/concepts/model-independent-governance/`, `models-are-temporary-architectural-intent-is-not`, `stanford-ai-index-2026-engineering-governance` (benchmark-correct is not architecturally correct), `databricks-omnigent-agent-infrastructure-governance` (Databricks orchestration), `what-ctos-measure-before-renewing-ai-coding-tools` (total cost per merged change). |

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | Databricks AI Index: A Completed Task Is Not a Compliant One |
| Slug | `databricks-ai-index-architectural-conformance` |
| Report-anchored (ADR-015) | yes: entity = "Databricks AI Index" (launched 16 Nov 2026); verbatim first in all six title fields; meta description leads with source and the 64% to 28% figure, which the body states |
| Topic hub | architectural-governance |
| Content type (`--type`) | Report Response (primary object is a named industry index and its benchmark) |
| OG headline | Databricks AI Index: Completed Is Not Compliant (7 words) |
| Editorial gate | pass: named-source entry point (Databricks AI Index, not covered on the site) plus new evidence for the thesis (the Index's own metric, cost per completed task, makes the definition of "completed" an economic question) |
| Five questions | changed: single-provider use among Unity Gateway companies fell from about 64% to 28% and teams now compare models by cost per completed task; matters: model choice is revisited often and ranked on that metric; breaks: a task that passes hidden tests can still cross an architectural boundary and counts as success; teams should: fix repository, tasks and decisions, score conformance independently in CI, and compare cost per compliant completed task; governance helps: a deterministic check against recorded decisions gives a yardstick that does not change with the model |
| Cannibalisation | See below. Verdict: **re-angle**. The chat's title ("The Multi-Model Enterprise Has a Governance Problem That Model Routing Cannot Solve") is **merge or drop** against `smart-routing-ai-coding-agents` (85.7, same thesis). Built instead as a report response on the Index's measurement gap, linking rather than restating smart routing, model-independent governance and the Stanford piece. |
| Cross-links | out: `smart-routing-ai-coding-agents`, `stanford-ai-index-2026-engineering-governance`, `what-ctos-measure-before-renewing-ai-coding-tools`, `/concepts/model-independent-governance/`, `/demo/governed-python-agent/`, `/integrations/`, `/audit/`; reciprocal hosts: the first three |

### Cannibalisation detail

`find_overlap.py` on the chat's title (keywords: multi-model AI coding governance, model routing, Databricks AI Index, architectural conformance, cost per completed task): `stanford-ai-index-2026-engineering-governance` 93.8, `smart-routing-ai-coding-agents` 85.7, `databricks-omnigent-agent-infrastructure-governance` 56.0, `mistral-vibe-ai-coding-enterprise-infrastructure` 53.9, `barbara-liskov-python-encapsulation-ai-governance` 52.1, `bcg-ai-era-operating-models-governance` 46.6, `ai-coding-governance-should-be-reviewable` 46.5, `ai-coding-agent-architecture` 44.4, `ai-coding-agents-financial-services-audit-trail` 43.9, `cursor-developer-habits-report-governance-infrastructure` 41.3.

On the final title (keywords: Databricks AI Index, cost per completed task, architectural conformance, multi-model AI coding governance, open-weight models): Stanford 93.8, Omnigent 69.6, `/open-source-ai-coding-agent-governance/` 54.4, reviewable 46.5, `architectural-governance-across-heterogeneous-ai-coding-agents` 44.1, Cursor 42.7, agent architecture 40.4, smart routing 40.4. A keyword variant also surfaced `what-ctos-measure-before-renewing-ai-coding-tools` 54.6 and `ai-engineering-roi` 42.6.

All pages at 40+ were read (title, lede, section headings; smart routing, Omnigent and CTO-renewal in full). Judgement:
- Stanford: matches on "AI Index" only; it argues benchmark success is not architectural correctness in general. The draft cites it for that and does not repeat the argument.
- Smart routing: same thesis as the chat's title. Linked in one sentence; the draft does not restate routing vs guardrails.
- Omnigent: different Databricks product (orchestration). Not linked to avoid a Databricks cluster that reads as vendor commentary; no shared figures.
- CTO renewal / AI engineering ROI: budget-level metrics (total cost per merged change). The draft's proposed per-task measure is distinguished and linked.
- `/concepts/model-independent-governance/` and `models-are-temporary-...`: the draft links the concept once and does not restate the five-roles or lock-in argument.
- Others (Mistral Vibe, Liskov, BCG, reviewable, agent architecture, financial services, Cursor, heterogeneous agents, open-source map): shared generic terms only.

Body search: `git grep -i -E "ai index|unity gateway|30\.9%|7\.3%|699|cost per (completed|compliant) task|cost per task"` over `site/` found no Databricks AI Index figures; "AI Index" hits are Stanford and Glean's Work AI Index only. No overlap with other briefs in this batch was checked here (each chat is drafted separately); the orchestrator should compare.

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 38 after revision round 1 (directness 8, rhythm 7, trust 8, authenticity 7, density 8); first draft also 38 |
| `lint_prose.py` | errors: 0; warnings: 0 on the revised draft body (CLI and CI expanded at first use). Re-run on the built page |
| Cold read: thesis as restated | "Model benchmarks score whether code works and what it costs, not whether it respects a team's architectural decisions, so teams should also measure cost per compliant completed task" (matches) |
| Cold read: unclear terms, and how resolved | Unity Gateway: one clause; Mneme: introduced in plain words before the demo; `mneme check --memory` and exit 2: sentence on what the command reads and that exit 2 means a blocked violation; supported hook: names Claude Code's hook and what it blocks, and Codex CLI's patch-tool check; Architecture Audit: one clause plus link in the end CTA; provider-count caveats cut to two sentences (30.9% caveat kept); outcome table rows rewritten; shell-write sentence explained (shell writes skip the hook, checked at end of turn by both agents, CI backstop) |
| Pre-merge Opus claim audit | round 1: VERDICT FIX, 6 items; all 6 applied verbatim (demo records three decisions incl. storage; refactor wording and expiry field; benchmark also reports time per task; weekly cadence as Databricks' stated intent in body and faq.json; 30.9% is share of tokens to Databricks-hosted models; description names the Unity Gateway sample). No figure drift found live on 2026-11-22 |

## Agreed scope

Final scope from the chat's last turn and issue #316: one P1 data-led article. Thesis: enterprises are separating model selection from their applications; the Index measures task success and cost per completed task, which do not measure architectural decision conformance. Choosing which model runs is distinct from deciding which recorded decisions every implementation must respect, and from the evidence that they were respected. Audience: CTO, VP Engineering, platform leads, staff architects. Structure as built: what the Index found (with sample caveats); what the benchmark measures; completed vs compliant (three-question table); one decision, two tasks (public JSON storage demo); cost per compliant completed task as a proposed measure with four outcome counts; what to test before switching models; where Mneme fits. 1,364 words after revision round 1.

Title alternatives considered: "The Multi-Model Enterprise Has a Governance Problem That Model Routing Cannot Solve" (chat; drop, duplicates smart routing), "The Missing Metric in Multi-Model AI Coding: Architectural Conformance" (#316 preferred; not report-anchored), "What the Databricks AI Index Doesn't Measure About AI-Generated Code" (#316 alternative; close to the chosen title, longer).

Chat constraints carried: no cross-model result invented (the draft says no comparison has been published and presents the test as a design); the measure is a proposal, not observed ROI; token share is not company share; the Index is not proof that Mneme is needed.

## Key facts, figures, sources

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| Databricks launched the Databricks AI Index on 16 Nov 2026; public, updated weekly; two data sources (Unity Gateway usage, coding-agent benchmark) | https://www.databricks.com/blog/introducing-databricks-ai-index-state-enterprise-ai-tokenomics | verified (post date; "What the Databricks AI Index measures"; FAQ "updated weekly") |
| Sample: "thousands of enterprises using Unity Gateway" | same; https://developers.databricks.com/ai-index | verified. The post says "10,000+ companies" once and "thousands" in the intro, "About the data" and FAQ; the index page says "thousands". Draft uses the conservative "thousands" |
| About 64% relied on one provider in July; 28% by November 2 | blog, "Enterprises are embracing multi-AI and open-weight models" | verified against the blog text. Index chart data (2+ providers 36.0 to 71.1) gives 64.0 to 28.9; the draft uses the blog's stated 28% and attributes it to the launch post |
| Provider count is cumulative since July 20 | https://developers.databricks.com/ai-index (chart note) | verified: "counts every provider a company has used since July 20, 2026" |
| Open-weight share of enterprise token traffic 7.3% (July) to 30.9% (November) | blog, same section; index chart note | verified; stated as a share of tokens sent to Databricks-hosted models on Unity Gateway (chart note), not of companies or all AI traffic |
| Benchmark: models across nine AI labs, run in Claude Code and Codex; tasks from Databricks' private codebase; hidden tests, not an LLM judge; task success and cost per completed task | blog, "What the Databricks AI Index measures", "No single model or harness...", "About the data" | verified |
| Gemini 3.8 Flash: low token price, 140 turns per task, among the most expensive at $11.97 per task; extra turns, long outputs and failed attempts add cost | blog, "Token prices don't tell the full story of AI coding costs" | verified (post: "one of the most expensive models in the benchmark") |
| No single model or harness dominates the cost-quality frontier; evaluate combinations on own workloads | blog, section of that name | verified |
| Unity Gateway is the Databricks service for accessing and governing AI models | blog intro ("use Unity Gateway to access and govern AI models") | verified |
| Not used: "custom Python policies" in Unity Gateway | https://docs.databricks.com/gcp/en/release-notes/unity-gateway/ | found-differs: external guardrails (Beta) and custom service policies confirmed, "Python" policies not found. Cut; no Unity Gateway policy claim appears in the draft |
| Not used: P50 $2.49 / P99 $699.74 weekly user spend | blog and index page | verified but not needed for the final angle; omitted |
| Not used: ContextOS article | none | not found, and private context. Cut |

## Mneme claims and maturity

Checked against `/demo/governed-python-agent/`, `/docs/how-enforcement-works/`, `/integrations/` and `scripts/core_version.json` (minimum 0.11.0).

| Claim (as drafted) | Class |
|---|---|
| The JSON storage demo's recorded decisions include one on storage (JSON only, no external database, ORM or migration layer); the SQLAlchemy/PostgreSQL/Alembic refactor task fails the check naming `mneme_storage_json` (exit 2); the JSON-only task passes (exit 0); commands quoted from the demo page | SHIPPED (public demo; inputs ship in the repository) |
| The decision record and both inputs ship in the Mneme repository, reproducible without a model call | SHIPPED (demo page FAQ and "Run it yourself") |
| The verdict depends on the decision and the input, not on which model wrote the input | SHIPPED (deterministic check; `/docs/how-enforcement-works/`) |
| Mneme is open-source software that stores architectural decisions in the repository and checks changes against them | SHIPPED (`/integrations/` intro) |
| The check is deterministic; a failing verdict names the decision it broke | SHIPPED (`/docs/how-enforcement-works/`, demo) |
| In agents that expose a supported hook (Claude Code, Codex CLI) a proposed file write is checked before it lands; most shell writes reach disk first; CI on the pull request is the backstop for every agent | SHIPPED, with the stated limits (`/integrations/`) |
| "We have not published a comparison of models on this decision" | true statement of absence; no cross-model claim made |
| Cost per compliant completed task and the four outcome counts | CONCEPTUAL (explicitly a proposed measure, not observed) |
| Model-independent governance keeps decisions outside any one model (linked concept) | CONCEPTUAL / category framing, linked not restated |

Totals: 6 SHIPPED, 0 VALIDATED EXPERIMENT, 0 PLANNED, 2 CONCEPTUAL (plus one statement of absence).

Batch overlap: the IBM draft in this batch uses decisions surviving a vendor or model change as an example; this piece leads with the Index figures and cost per compliant completed task, and mentions model independence only as one linked sentence in the closing section.

## Positioning constraints

The Index is evidence of model diversification, not proof that Mneme is needed, not ROI or market validation. No competitive claim about Unity Gateway's policy features. No invented cross-model results. "Decision layer" thesis framing not used. Internal roadmap items, partnerships and social follow-ups from the chat are tracked privately and stay out of the article and this brief.

## Non-insight site edits requested

None.

## Open questions

- Owner: search intent for "multi-model AI coding governance" and "Databricks AI Index" was not checked in Search Console; #316 asks for that before title lock. Proceeded with the report-anchored title as the conservative choice.
- Owner: the issue suggests an optional version-pinned cross-model run. Not done; the draft presents the comparison as a test design. A run would let a later update add real numbers.
- Publish timing: the Index updates weekly; re-check the 64%/28% and 7.3%/30.9% figures against the live post close to the publish date.
