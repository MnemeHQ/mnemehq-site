# Insights scope ledger

Tracks ChatGPT scope chats (project: "Mneme Growth and GTM") against what actually
shipped, so we stop re-crawling the whole chat list on every "draft insights" run.
The publish-insight skill (`.claude/skills/publish-insight/SKILL.md`) describes the pipeline this supports.

**How to update:** follow Stage 5 of the `publish-insight` skill
(`.claude/skills/publish-insight/SKILL.md`): once a scope chat's article is deployed, add/update
its row here with the PR # and merged date, then mark the chat with the `***` prefix in ChatGPT.
Marking is a required step, not optional. Any `*` in a `Post-` title means processed.
Only chats that produced (or were meant to produce) a published insight belong here —
not every chat in the project.

## Published

| Scope chat (ChatGPT title) | Scoped | Shipped as | PR | Merged |
|---|---|---|---|---|
| ***Post-MCP Agentic SDLC Scope | 2026-09-17 | `agentic-change-management-needs-a-decision-layer` | [#136](https://github.com/MnemeHQ/mnemehq-site/pull/136) | 2026-09-17 |
| ***Post-FDE Decision Layer Article | 2026-09-15 | `forward-deployed-architects-need-a-decision-layer` + FDE supporting cluster (4 pages) | [#132](https://github.com/MnemeHQ/mnemehq-site/pull/132) | 2026-09-15 |
| ***Post-FDE ICP Content Cluster | 2026-09-15 | `most-valuable-ai-dataset-decisions-already-made`, `agent-economy-needs-decision-infrastructure`, + FDE cluster pages | [#129](https://github.com/MnemeHQ/mnemehq-site/pull/129) | 2026-09-15 |
| ***Post-Mneme Decision Data | 2026-09-15 | folded into #129 (decision-dataset article) — **not independently verified, confirm before trusting** | [#129](https://github.com/MnemeHQ/mnemehq-site/pull/129)? | 2026-09-15 |
| ***Post-Positioning strategy analysis | 2026-09-15 | not independently verified — likely folded into #129's "decision-layer thesis" | unknown | unknown |
| Post-Writing ROI Content — **no `***`, see "Partially processed" below** | 2026-09-08/10 | `ai-engineering-roi`, `ai-throughput-is-not-engineering-throughput` only | [#135](https://github.com/MnemeHQ/mnemehq-site/pull/135) | 2026-09-15 |
| ***Post-software factories + ***Post-Scope software factories | 2026-09-19 | `software-factory-governance-layer` | [#139](https://github.com/MnemeHQ/mnemehq-site/pull/139) | 2026-09-19 |
| ***Post-Conway's Law Relevance | 2026-09-18 | `conways-law-ai-coding-agents` | [#139](https://github.com/MnemeHQ/mnemehq-site/pull/139) | 2026-09-19 |
| ***Post-Brooks Law Relevance | 2026-09-18 | `brooks-law-ai-coding-agents` | [#139](https://github.com/MnemeHQ/mnemehq-site/pull/139) | 2026-09-19 |
| ***Post-Strategic Signal local infra | 2026-09-16 | `private-ai-infrastructure-governance` | [#139](https://github.com/MnemeHQ/mnemehq-site/pull/139) | 2026-09-19 |
| ***Architecture Support Rules | 2026-09-19 | Netflix Conductor 4.0 case study added to `software-factory-governance-layer` | [#141](https://github.com/MnemeHQ/mnemehq-site/pull/141) | 2026-09-19 |
| ***Post - Microsoft Assess Mneme Thesis | 2026-09-22 | `microsoft-ai-decision-brief-architectural-intent` | [#150](https://github.com/MnemeHQ/mnemehq-site/pull/150) | 2026-09-25 |
| ***Post-Atlassian Mneme Comparison | 2026-09-19 | `atlassian-agentic-pivot-engineering-system-of-record` | [#150](https://github.com/MnemeHQ/mnemehq-site/pull/150) | 2026-09-25 |
| ***Post-Package hallucinations explainer | 2026-09-14 | `package-hallucinations-pre-action-governance` | [#150](https://github.com/MnemeHQ/mnemehq-site/pull/150) | 2026-09-25 |
| ***Post-Assess EY Report | 2026-10-07 | `ey-beyond-the-code-ai-software-development` | [#216](https://github.com/MnemeHQ/mnemehq-site/pull/216) | 2026-10-14 |
| ***Post- Cohesion And Reddit Thread | 2026-10-04 | `return-of-the-silo-engineer` (insight 1); insights 2 and 3 became `/concepts/engineering-coherence/` and a section of `/concepts/engineering-decision-governance/` | [#216](https://github.com/MnemeHQ/mnemehq-site/pull/216), [#214](https://github.com/MnemeHQ/mnemehq-site/pull/214) | 2026-10-14 |
| ***Post-AI Silo Breakdown Content | 2026-09-12 | folded into `return-of-the-silo-engineer` as one section | [#216](https://github.com/MnemeHQ/mnemehq-site/pull/216) | 2026-10-14 |
| ***Post-Scope pre action governance | 2026-09-08 | `pre-action-enforcement-agent-governance` | [#216](https://github.com/MnemeHQ/mnemehq-site/pull/216) | 2026-10-14 |
| ***Post-Assess paper relevance | 2026-10-07 | `multi-agent-coding-shared-context` | [#221](https://github.com/MnemeHQ/mnemehq-site/pull/221) | 2026-10-15 |
| ***post-reverse engineer decisions | 2026-10-12 | `reverse-engineering-architectural-decisions-research` | [#221](https://github.com/MnemeHQ/mnemehq-site/pull/221) | 2026-10-15 |
| ***Post-Business Type Comparison and decision governance | 2026-10-07 | `from-decision-records-to-decision-governance` (#221), concept page (#214), software-factory section in `software-factory-governance-layer` (#224) | [#221](https://github.com/MnemeHQ/mnemehq-site/pull/221), [#224](https://github.com/MnemeHQ/mnemehq-site/pull/224) | 2026-10-15 |
| ***Post-claude frontier academy Assess program relevance | 2026-10-07 | `claude-frontier-academy-frontier-deployed-engineers` (#221), frontier section in `forward-deployed-engineers-enterprise-ai` (#224); other cluster items merged or dropped 2026-10-15 | [#221](https://github.com/MnemeHQ/mnemehq-site/pull/221), [#224](https://github.com/MnemeHQ/mnemehq-site/pull/224) | 2026-10-15 |
| ***Post- OpenShell Assess NVIDIA Interview | 2026-10-21 | `nvidia-openshell-reference-architecture-agent-policy`; integration pages `/integrations/nvidia-openshell/`, `/integrations/open-policy-agent/`, `/integrations/nvidia-sentry/` (#246); "Who Governs the AI Factory?" dropped | [#238](https://github.com/MnemeHQ/mnemehq-site/pull/238), [#246](https://github.com/MnemeHQ/mnemehq-site/pull/246) | 2026-10-22 / 2026-10-23 |
| ***Post-Scope infra governance content | 2026-10-18 | `policy-as-code-engineering-decisions` (published by the scheduler); `kubernetes-scaling-database-connection-budget` queued 10-24 | [#239](https://github.com/MnemeHQ/mnemehq-site/pull/239), [#240](https://github.com/MnemeHQ/mnemehq-site/pull/240) | 2026-10-23 / queued |
| ***Post-Anthropic code review | 2026-10-17 | `claude-code-review-trusted-decision-boundary` queued 10-25 | [#241](https://github.com/MnemeHQ/mnemehq-site/pull/241) | queued |
| ***Post-Assess OpenAI Modernization Announcement | 2026-10-20 | `openai-cobol-migration-benchmark-behavioral-parity` queued 10-26, `ai-legacy-modernization-what-must-survive` queued 10-27 | [#242](https://github.com/MnemeHQ/mnemehq-site/pull/242), [#243](https://github.com/MnemeHQ/mnemehq-site/pull/243) | queued |
| ***Post-Research migration strategies | 2026-10-13 | `nodejs-to-go-migration-architectural-decisions` queued 10-28 | [#244](https://github.com/MnemeHQ/mnemehq-site/pull/244) | queued |
| ***Post-Agent orchestrators and factories | 2026-10-20 | Integrations hub regrouped by function (#246) | [#246](https://github.com/MnemeHQ/mnemehq-site/pull/246) | 2026-10-23 |

Notes for batches 4 and 5 (2026-10-22/23): from this batch on, insights publish one per day at 13:07 UTC through the scheduled publisher (#236, #237, #245, #247; PUBLISHING.md, "Scheduled publishing"). The briefs are in #234. OpenShell was published by hand on 2026-10-22 (deploy verified at `c6c1ed46`). The integrations restructure deployed at `71d1f9b9`, and Policy as Code was the publisher's first real merge (deploy verified at `014f8476`). Pre-merge Opus audits found 4 blockers and 11 should-fix items in batch 4, and 2 blockers and 3 should-fix items in batch 5, all fixed. All six chats were renamed with the `***` marker on 2026-10-23 and verified by re-listing the project. By owner decision (2026-10-22), chats are marked once their batch ships even if later phases are open. Their remaining items are listed under "Partially processed" below, and articles still queued are tracked by their PRs.

Notes carried over: the software-factory pillar is one article refined across two chats (the 2nd adds the Bob Bemer/1968 historical framing) — it's the pillar of a planned 5-article cluster, only the pillar is scoped/shipped so far. Conway and Brooks are cross-linked as a pair. The private AI piece's Latham facts were verified against Bloomberg Law and Legal IT Insider; the FT citation named in the original scope chat could not be located and was dropped.

All five ChatGPT chats were renamed with the `***` marker on 2026-09-19 after this PR went live.

`***Architecture Support Rules` (a mixed chat covering EDA roadmap discussion plus the Netflix Conductor scope) was renamed with the `***` marker on 2026-09-19 after PR #141 shipped its one content-publishing item, the Conductor case study. The EDA roadmap discussion in that same chat was not acted on here, since it's internal roadmap sequencing, not a content ask.

Notes for #150: only the insight article from each chat shipped. The Microsoft chat also scoped non-insight site edits that are **not** done here and need their own PRs (different contracts): a homepage "Why now" section, an "agent governance vs architectural governance" section on `/concepts/architectural-governance/`, a control-plane stack on `/platforms/`, a new `/concepts/decision-index/` page, and an Authority → Index → Applicability → Enforcement → Evidence block on `/docs/how-enforcement-works/`. The Atlassian chat's LinkedIn comment/repost/long-form drafts are social, not site, work.

Sources verified 2026-09-25 against primary documents: Microsoft AI Decision Brief PDF (pp. 22, 28, 34, 35, 38); Atlassian Agentic Pivot PDF (all 21 pages, OCR); USENIX Security 2025 (Spracklen et al.); arXiv 2605.17062 (not peer reviewed, labelled as such); Trend Micro June 2025; Orygn July 2026. The Atlassian PDF prints the system-of-record figure as 84% in one lifecycle table and 88% in the overview and conclusion; the article uses 88% and notes the discrepancy.

All three chats were renamed with the `***` marker on 2026-09-25 after #150 deployed (deploy verified at `f30fd2d`, `site-deployed` tag matched, all three URLs 200).

**Other unmarked `Post-` chats found 2026-09-25, not yet assessed:** Post-AI Silo Breakdown Content (09-13), Post-Scope pre action governance (09-08), Post-Competing with CodeRabbit (09-08), Post-OKF architecture article scope (09-01), plus ~119 unmarked `Post-` chats from 2026-08-11 to 08-29 that predate this ledger.

## In review (drafted, not merged, not yet marked `***`)

None currently.

## Partially processed — do not mark done

**Marked `***` on 2026-10-23 with open items (owner decision; full scope in the briefs):**

- **Post-Assess OpenAI Modernization Announcement:**
  - Phase 2: "Behavioral Equivalence Is Not Architectural Compliance", which absorbs the migration chat's "Why Compiling Is Not Enough".
  - Evidence-gated: the COBOL-to-Java cutover checklist and the controlled migration experiment.
  - Site edit: a "before the migration" section on `/use-cases/ai-assisted-software-migrations/`.
- **Post-Research migration strategies:** three phase 2 articles: Go translation idioms, strangler vs big-bang, and when not to rewrite.
- **Post-Scope infra governance content:**
  - Phase 2: "The Missing Link Between Platform Engineering and Enterprise Architecture".
  - Evidence-gated: the decision-to-infrastructure-guardrail reference architecture.
  - Owner decision: the Infrastructure Governance concept page, which needs a terminology amendment first.
- **Post-Agent orchestrators and factories:** `/use-cases/software-factory-governance/` and the how-to guides wait on experiment evidence (#231).

**Post-Writing ROI Content** (located 2026-09-19) scoped a full pillar + ~10 supporting-article cluster for AI Engineering ROI. Only the pillar and one deferred spoke shipped, in PR #135 ("pillar + AI Throughput Is Not Engineering Throughput only, hold the rest for a follow-up round"). The five *other* articles named in that PR's description as "already-published spokes" (`ai-roi-problem-is-about-systems-not-models`, `ai-coding-agent-verification-tax`, `dora-metrics-insufficient-for-agentic-development`, `acceleration-whiplash-governance-gap`, `ai-coding-productivity-gains-rework`) predate this chat's scoping and are unrelated to its backlog.

**Confirmed unpublished** (checked against `git log` and `site/insights/` on 2026-09-19), still scoped inside this chat and not marked — the chat itself should stay `***`-free as a reminder there's a backlog:

- How to Measure AI Coding ROI Without Counting Lines of Code (P0)
- The Hidden Cost of AI-Generated Rework (P0)
- When AI Saves Developer Time but Creates More Work for Senior Engineers (P0)
- Architectural Drift Is an AI ROI Leak (P1)
- What CTOs Should Measure Before Renewing Their AI Coding Tools (P1)
- The Economics of Preventing an Incompatible Change Before It Is Written (P2)
- From AI Adoption to AI Value: A Maturity Model for Engineering Organizations (P2)

Do not rename this chat with `***` until these are either shipped or explicitly dropped. Note the chat's own guidance: keep the cluster 60–70% neutral executive/engineering economics, only 10–20% explicitly Mneme/audit — write these as standalone economics pieces, not governance pitches.


**Last insight-article PR before this ledger was created:** [#136](https://github.com/MnemeHQ/mnemehq-site/pull/136),
merged 2026-09-17T13:37:05Z — "Position Mneme's Decision Index against post-MCP
agentic change management."

Notes for #216 (batch 1, 2026-10-14): deployed at `93d47012` (deploy run 38632284531; `site-deployed` = `main`). The Reddit thread from the Cohesion chat was dropped as unverifiable (reddit.com is blocked in both browsers). The pre-merge Opus audit caught one blocker, the EY chart's code-review and test-generation figures swapped by text extraction. All four chats were renamed with the `***` marker on 2026-10-14 after the deploy, and the new titles were verified by re-listing the project.

Notes for #221 (batch 2, 2026-10-15): deployed at `88d8edd9` (deploy run 38718979840; `site-deployed` = `main`). The pre-merge Opus audit caught five blockers: a misattributed definition of knowledge vaporization in the erosion study, and four Mneme enforcement overclaims (all decisions path-scoped and enforced before every write; accepted proposals enforced). The two fully shipped chats (AECP and reverse engineer decisions) were renamed with the `***` marker on 2026-10-15 and verified by re-listing the project; the Business Type and Frontier Academy chats stay unmarked (see "Partially processed").

Notes for #224 (batch 3, 2026-10-15): deployed at `7dfed00a` together with the install-and-activate how-to (#225); deploy runs 38800394435 and 38800444133 succeeded and `site-deployed` = `main`. It closed the last open items of the Business Type and Frontier Academy chats (the Frontier cluster verdicts were decided by TheoV823 on 2026-10-15). Both chats were renamed with the `***` marker on 2026-10-15 and verified by re-listing the project.
