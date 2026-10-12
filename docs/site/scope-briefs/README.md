# Insight scope briefs

Scope text gathered from ChatGPT "Post-" chats (project "Mneme Growth and GTM", `g-p-69fb157536408191b03a29c6f51f7821`) for a separate build session. Gathered 2026-10-12 read-only; no chat was renamed or messaged, and `insights-scope-ledger.md` and `site/` are untouched.

Build by following the `publish-insight` skill ([`.claude/skills/publish-insight/SKILL.md`](../../../.claude/skills/publish-insight/SKILL.md)) from Stage 3. `scripts/new_article.py` writes the page only (there is no `--register` flag); registration, the validators and the pre-merge Opus audit (SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL) are listed there. New briefs start from [TEMPLATE.md](TEMPLATE.md); every brief here has a **Build card** with proposed slug, hub, OG headline and editorial-gate verdict, to confirm before building.

| Brief | Chat date (UTC created) | Kind | Status |
|---|---|---|---|
| [Open Architecture Page Assessment](2026-10-09-open-architecture-page-assessment.md) | 2026-10-09 | spec/ADR now, site page later | gathered, not built |
| [Clarify OSS Enterprise Pricing](2026-10-09-clarify-oss-enterprise-pricing.md) | 2026-10-09 | site edit (pricing, trust, nav) | gathered, not built |
| [Assess paper relevance (AECP)](2026-10-07-assess-paper-relevance.md) | 2026-10-07 | insight | gathered, not built |
| [Assess EY Report](2026-10-07-assess-ey-report.md) | 2026-10-07 | insight | gathered, not built; title blocked on house voice |
| [Claude Frontier Academy](2026-10-07-claude-frontier-academy.md) | 2026-10-07 | insight (news) + FDE cluster verdicts | gathered, not built |
| [Business Type and decision governance](2026-10-07-business-type-and-decision-governance.md) | 2026-10-07 | concept + 2 insights | gathered, not built; blocked on terminology |
| [Cohesion And Reddit Thread](2026-10-04-cohesion-and-reddit-thread.md) | 2026-10-04 | concept + 3 insights | gathered, not built; blocked on terminology |
| [AI Silo Breakdown Content](2026-09-12-ai-silo-breakdown-content.md) | 2026-09-12 | insight | gathered, not built; merge with Cohesion's silo piece |
| [Scope pre action governance](2026-09-08-scope-pre-action-governance.md) | 2026-09-08 | insight + pillar | gathered, not built; blocked on terminology |
| [Competing with CodeRabbit](2026-09-08-competing-with-coderabbit.md) | 2026-09-08 | site edit (compare page) | gathered, not built |
| [OKF architecture article scope](2026-09-01-okf-architecture-article-scope.md) | 2026-09-01 | update existing insight | gathered, not built |
| [Writing ROI Content (backlog)](2026-09-08-writing-roi-content-backlog.md) | 2026-09-08 (updated 09-10) | insight cluster | gathered, not built; chat must stay un-marked |

## Decisions needed before building

1. **Terminology lock.** Three candidate category terms compete: "pre-action governance" (09-08), "engineering decision governance" (10-07), "engineering coherence" (10-04). Settle together in PUBLISHING.md (and ADR-001/013/014 if they change category or tagline). Blocks the concept pages and the insights that lean on them.
2. **EY title.** "Bottleneck" is banned by house voice and fails `lint_prose.py`; reword or grant a documented exception.
3. **One home for "cheap code, scarce decisions".** EY, decision silos (09-12) and Cohesion insight 3 all argue it.
4. **Silo merge.** 09-12 Silo brief + Cohesion's "Return of the Silo Engineer" become one article.

**Buildable now (no terminology dependency):** AECP multi-agent piece, Claude Frontier Academy news piece, NBER 240%/30% (ROI backlog), OKF update to the June page, EY once its title is settled.

## Read before building

- **OKF overlaps a shipped page.** `open-knowledge-format-vs-governance` (2026-06-17) exists, and the OKF chat believed it did not.
- **CodeRabbit is mostly strategy, not an article scope.** The one content ask may fit better as a refresh of `/compare/coderabbit/`. Several roadmap and site asks were partly done by #179 and #193.
- **The pre-action and CodeRabbit chats disagree** on whether "pre-action governance" is a category or a mechanism. Resolve with the positioning ADRs before building the pillar.
- **ROI backlog drift.** The verification-tax and DORA articles already shipped, `ai-adoption-maturity-model-engineering-analysis` overlaps the maturity-model item, and four articles scoped in the Sep 10 "Include stats" turn are missing from the ledger's list.
- Citations are copied from the chats and none is verified. Each brief lists what to re-check.

## Unmarked "Post-" chats not processed

Marker rule: a title containing `*` means published. In the project there are 136 `Post-` chats, 4 carry a `*` mark (the `***` suffix ones and two `**` titles), leaving **132 unmarked**. By last-updated date:

- **12 newer than 2026-08-29**: the 7 chats from 2026-10-04 to 10-09 and the 5 earlier scopes, all briefed above.
- **32 last updated 2026-08-11 to 08-29** (one is `Post-tv-`, which never enters `site/`). The ledger said ~119 for this window, which does not match what ChatGPT returns. 12 were *created* in that window.
- **88 last updated before 2026-08-11** (earliest created 2026-05-06). Many probably shipped without a marker, so check `git log` first, per the workflow memory.

The ledger's "unmarked" count is unreliable; the git log is the real test of whether a chat shipped.

Full title and date list of the 132 was read from the ChatGPT project API during this session but is not reproduced here to keep the briefs focused. The older-chat titles are available on request. Titles seen include (updated Aug-Sep): Post-Identify Mneme's Harness Role (08-29), Post - AI Security Institute (AISI) - Assess AI Control Risks (08-29), Post-Assess hardware standard relevance (08-27), Post-Architectural Use Cases and Risks (08-20), Post-Concept-Architectural Drift Prevention (08-17), Post-AI Agents and Architecture (08-15).
