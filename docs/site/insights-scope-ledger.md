# Insights scope ledger

Tracks ChatGPT scope chats (project: "Mneme Growth and GTM") against what actually
shipped, so we stop re-crawling the whole chat list on every "draft insights" run.
See [[draft-insights-workflow]] memory for the pipeline this supports.

**How to update:** after a scope chat's article ships and the chat is renamed with
the `***` prefix in ChatGPT, add/update its row here with the PR # and merged date.
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
