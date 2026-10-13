# Insight scope briefs

Scope text gathered from ChatGPT "Post-" chats (project "Mneme Growth and GTM") for a separate build session. Gathered 2026-10-12 read-only; no chat was renamed or messaged, `site/` is untouched, and the ledger's Published table is unchanged (only its how-to note now points to the publish-insight skill).

Build by following the `publish-insight` skill ([`.claude/skills/publish-insight/SKILL.md`](../../../.claude/skills/publish-insight/SKILL.md)) from Stage 3. `scripts/new_article.py` writes the page only (there is no `--register` flag); registration, the validators and the pre-merge Opus audit (SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL) are listed there. New briefs start from [TEMPLATE.md](TEMPLATE.md); every brief here has a **Build card** with proposed slug, hub, OG headline and editorial-gate verdict, to confirm before building.

| Brief | Chat date (UTC created) | Kind | Status |
|---|---|---|---|
| [reverse engineer decisions](2026-10-12-reverse-engineer-decisions.md) | 2026-10-12 | insight, content type Research | gathered, not built |
| [Open Architecture Page Assessment](2026-10-09-open-architecture-page-assessment.md) | 2026-10-09 | spec/ADR now, site page later | gathered, not built |
| [Clarify OSS Enterprise Pricing](2026-10-09-clarify-oss-enterprise-pricing.md) | 2026-10-09 | site edit (pricing, trust, nav) | gathered, not built |
| [Assess paper relevance (AECP)](2026-10-07-assess-paper-relevance.md) | 2026-10-07 | insight | gathered, not built |
| [Assess EY Report](2026-10-07-assess-ey-report.md) | 2026-10-07 | insight | gathered, not built; title decided |
| [Claude Frontier Academy](2026-10-07-claude-frontier-academy.md) | 2026-10-07 | insight (news) + FDE cluster verdicts | gathered, not built |
| [Business Type and decision governance](2026-10-07-business-type-and-decision-governance.md) | 2026-10-07 | concept + 2 insights | gathered, not built; concept waits on terminology amendment |
| [Cohesion And Reddit Thread](2026-10-04-cohesion-and-reddit-thread.md) | 2026-10-04 | 3 insights (no concept page) | gathered, not built |
| [AI Silo Breakdown Content](2026-09-12-ai-silo-breakdown-content.md) | 2026-09-12 | merged | merged into Cohesion's "Return of the Silo Engineer" |
| [Scope pre action governance](2026-09-08-scope-pre-action-governance.md) | 2026-09-08 | insight (mechanism; no pillar) | gathered, not built |
| [Competing with CodeRabbit](2026-09-08-competing-with-coderabbit.md) | 2026-09-08 | site edit (compare page) | gathered, not built |
| [OKF architecture article scope](2026-09-01-okf-architecture-article-scope.md) | 2026-09-01 | update existing insight | gathered, not built |
| [Writing ROI Content (backlog)](2026-09-08-writing-roi-content-backlog.md) | 2026-09-08 (updated 09-10) | insight cluster | gathered, not built; chat must stay un-marked |

## Decisions confirmed (2026-10-12, by TheoV823)

1. **Terminology: "engineering decision governance" is the one new concept term.** It gets a concept page. "Pre-action" stays a mechanism word used in insights (where enforcement happens), with no pillar or concept page. "Engineering coherence" stays a problem framing used in insights, with no concept page. Its meaning comes from **ADR-031** ("Decision Governance Semantics", MnemeHQ/mneme, accepted 2026-10-08, not yet released). Before the concept page ships: a terminology amendment in PUBLISHING.md ("Conceptual authority and editorial discipline") that cites ADR-031, and a check of ADR-001/013/014 in `MnemeHQ/mneme`.
2. **EY title:** "EY 'Beyond the Code' Report: AI Has Moved the Software Constraint Beyond Coding" (confirm the verbatim report name on the PDF cover). "Bottleneck" appears at most once, inside a verbatim EY quote marked `<!-- voice-ok: verbatim EY quote -->`.
3. **"Cheap code, scarce decisions" lives in Cohesion insight 3** ("When Code Becomes Cheap, Decisions Become the Scarce Asset"). EY uses its survey as evidence and links there; the silo article keeps its own angle.
4. **Silo: one article, "The Return of the Silo Engineer"**, built from the Cohesion scope, with the 09-12 cross-system "decision silos" argument folded in as one section. The 09-12 brief is merged, not built separately.

**Buildable now:** AECP multi-agent piece, Claude Frontier Academy news piece, OKF update to the June page, EY, The Return of the Silo Engineer, The Coherence Problem in Agentic Software Development, When Code Becomes Cheap. **After the terminology amendment:** Engineering Decision Governance concept page, From Decision Records to Decision Governance.

## Read before building

- **OKF overlaps a shipped page.** `open-knowledge-format-vs-governance` (2026-06-17) exists, and the OKF chat believed it did not.
- **CodeRabbit is mostly strategy, not an article scope.** The one content ask may fit better as a refresh of `/compare/coderabbit/`. Several roadmap and site asks were partly done by #179 and #193.
- **Pre-action is a mechanism, not a category** (decision 1): there is no pillar; the pre-action brief's definition article is retitled as a mechanism piece.
- **ROI backlog drift.** The verification-tax, DORA and NBER 240%/30% (`ai-throughput-is-not-engineering-throughput`) articles already shipped, `ai-adoption-maturity-model-engineering-analysis` overlaps the maturity-model item, and four articles scoped in the Sep 10 "Include stats" turn are missing from the ledger's list.
- Citations are copied from the chats and none is verified. Each brief lists what to re-check.

## Unmarked "Post-" chats not processed

Marker rule: a title containing `*` means published. Matching the `Post-` prefix case-insensitively (including `***`-prefixed titles), the project had 163 `Post-` chats on 2026-10-12; 30 carry a `*` mark, leaving **133 unmarked**. By last-updated date:

- **13 newer than 2026-08-29**: the 8 chats from 2026-10-04 to 10-12 and the 5 earlier scopes, all briefed above.
- **32 last updated 2026-08-11 to 08-29** (one is `Post-tv-`, which never enters `site/`). The ledger said ~119 for this window, which does not match what ChatGPT returns. 12 were *created* in that window.
- **88 last updated before 2026-08-11** (earliest created 2026-05-06). Many probably shipped without a marker, so check `git log` first, per the publish-insight skill.

The ledger's "unmarked" count is unreliable; the git log is the real test of whether a chat shipped.

Full title and date list of the 132 was read from the ChatGPT project API during this session but is not reproduced here to keep the briefs focused. The older-chat titles are available on request. Titles seen include (updated Aug-Sep): Post-Identify Mneme's Harness Role (08-29), Post - AI Security Institute (AISI) - Assess AI Control Risks (08-29), Post-Assess hardware standard relevance (08-27), Post-Architectural Use Cases and Risks (08-20), Post-Concept-Architectural Drift Prevention (08-17), Post-AI Agents and Architecture (08-15).
