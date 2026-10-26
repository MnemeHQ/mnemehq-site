# Insight scope briefs

Scope text gathered from ChatGPT "Post-" chats (project "Mneme Growth and GTM") for a separate build session. Gathered 2026-10-12 read-only; no chat was renamed or messaged, `site/` is untouched, and the ledger's Published table is unchanged (only its how-to note now points to the publish-insight skill).

Build by following the `publish-insight` skill ([`.claude/skills/publish-insight/SKILL.md`](../../../.claude/skills/publish-insight/SKILL.md)) from Stage 3. `scripts/new_article.py` writes the page only (there is no `--register` flag); registration, the validators and the pre-merge Opus audit (SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL) are listed there. New briefs start from [TEMPLATE.md](TEMPLATE.md); every brief here has a **Build card** with proposed slug, hub, OG headline and editorial-gate verdict, to confirm before building.

| Brief | Chat date (UTC created) | Kind | Status |
|---|---|---|---|
| [OpenShell Assess NVIDIA Interview](2026-10-21-openshell-assess-nvidia-interview.md) | 2026-10-21 | insight (re-angled); AI factory piece dropped; integration pages in #232/#233 | published 2026-10-22 (#238) |
| [Agent orchestrators and factories](2026-10-20-agent-orchestrators-and-factories.md) | 2026-10-20 | site edit (integrations, use case, how-tos; #231) | gathered, not built |
| [Assess OpenAI Modernization Announcement](2026-10-20-assess-openai-modernization-announcement.md) | 2026-10-20 | insight cluster (2 now, 1 phase 2, 2 evidence-gated) | A queued 10-26 (#242), B 10-27 (#243), C 10-29 (#249); D, E evidence-gated |
| [Scope infra governance content](2026-10-18-scope-infra-governance-content.md) | 2026-10-18 | insight cluster + concept page (owner decision) | 2 published 10-23 (#239), 1 queued 10-24 (#240), 6 queued 10-30 (#250); 4 and concept page held |
| [Anthropic code review](2026-10-17-anthropic-code-review.md) | 2026-10-17 | insight | queued 10-25 (#241) |
| [Research migration strategies](2026-10-13-research-migration-strategies.md) | 2026-10-13 | insight cluster (1 now, 3 phase 2, 2 merged) | 1 queued 10-28 (#244), 4 10-31 (#251), 3 11-01 (#252), 5 11-02 (#253) |
| [Engineering Coherence (concept)](2026-10-14-engineering-coherence-concept.md) | derived 2026-10-14 from the 10-04 chat | concept page | published 2026-10-14 (#214) |
| [reverse engineer decisions](2026-10-12-reverse-engineer-decisions.md) | 2026-10-12 | insight, content type Research | published 2026-10-15 (#221) |
| [Open Architecture Page Assessment](2026-10-09-open-architecture-page-assessment.md) | 2026-10-09 | spec/ADR now, site page later | parked until O1 validation results (owner, 2026-10-25) |
| [Clarify OSS Enterprise Pricing](2026-10-09-clarify-oss-enterprise-pricing.md) | 2026-10-09 | site edit (pricing, trust, nav) | built 2026-10-26 (#269) |
| [Assess paper relevance (AECP)](2026-10-07-assess-paper-relevance.md) | 2026-10-07 | insight | published 2026-10-15 (#221) |
| [Assess EY Report](2026-10-07-assess-ey-report.md) | 2026-10-07 | insight | published 2026-10-14 (#216) |
| [Claude Frontier Academy](2026-10-07-claude-frontier-academy.md) | 2026-10-07 | insight (news) + FDE cluster verdicts | news piece published 2026-10-15 (#221); FDE pillar update published (#224); other cluster items merged or dropped 2026-10-15 |
| [Business Type and decision governance](2026-10-07-business-type-and-decision-governance.md) | 2026-10-07 | concept + 2 insights | concept published (#214); From Decision Records published 2026-10-15 (#221); software-factory insight merged into the existing pillar (#224) |
| [Cohesion And Reddit Thread](2026-10-04-cohesion-and-reddit-thread.md) | 2026-10-04 | silo insight + inputs to two concept pages | insight 1 published 2026-10-14 (#216); concepts in #214 |
| [AI Silo Breakdown Content](2026-09-12-ai-silo-breakdown-content.md) | 2026-09-12 | merged | merged into Cohesion's "Return of the Silo Engineer" |
| [Scope pre action governance](2026-09-08-scope-pre-action-governance.md) | 2026-09-08 | insight (mechanism; no pillar) | published 2026-10-14 (#216) |
| [Competing with CodeRabbit](2026-09-08-competing-with-coderabbit.md) | 2026-09-08 | site edit (compare page) | built as a refresh (#264) |
| [OKF architecture article scope](2026-09-01-okf-architecture-article-scope.md) | 2026-09-01 | update existing insight | built as an update (#266) |
| [Writing ROI Content (backlog)](2026-09-08-writing-roi-content-backlog.md) | 2026-09-08 (updated 09-10) | insight cluster | resolved: pillar update (#255), 3 queued 11-03 to 11-05 (#258 to #260), rest dropped |

## Decisions confirmed (2026-10-12, by TheoV823)

1. **Terminology: "engineering decision governance" is the one new concept term.** It gets a concept page. "Pre-action" stays a mechanism word used in insights (where enforcement happens), with no pillar or concept page. "Engineering coherence" stays a problem framing used in insights, with no concept page. Its meaning comes from **ADR-031** ("Decision Governance Semantics", MnemeHQ/mneme, accepted 2026-10-08, not yet released). Before the concept page ships: a terminology amendment in PUBLISHING.md ("Conceptual authority and editorial discipline") that cites ADR-031, and a check of ADR-001/013/014 in `MnemeHQ/mneme`.
2. **EY title:** "EY 'Beyond the Code' Report: AI Has Moved the Software Constraint Beyond Coding" (confirm the verbatim report name on the PDF cover). "Bottleneck" appears at most once, inside a verbatim EY quote marked `<!-- voice-ok: verbatim EY quote -->`.
3. **"Cheap code, scarce decisions" lives in Cohesion insight 3** ("When Code Becomes Cheap, Decisions Become the Scarce Asset"). EY uses its survey as evidence and links there; the silo article keeps its own angle. *Update after the #209 audit: this thesis is already argued in 10+ shipped articles (e.g. `ai-makes-software-more-ambitious`), so insight 3, and the Coherence insight with it, is blocked pending a new owner decision; see the Cohesion brief.*
4. **Silo: one article, "The Return of the Silo Engineer"**, built from the Cohesion scope, with the 09-12 cross-system "decision silos" argument folded in as one section. The 09-12 brief is merged, not built separately.
5. **2026-10-14: own two terms, coherence and decisions, through one concept page each.** Engineering Coherence gets a concept page ([brief](2026-10-14-engineering-coherence-concept.md)), reversing decision 1's "no coherence concept page"; the Cohesion insight 2 becomes its body. Decision 3's thesis becomes a section of the Engineering Decision Governance concept page instead of an article. Articles support and link to the two concept pages rather than restating them. Both terms go through one PUBLISHING.md terminology amendment as concept terms (not category or tagline copy). Build cards: AECP keeps its evergreen title (AECP named in description and lede), hub agent-infrastructure; the Claude Frontier Academy piece and the FDE cluster go on agent-infrastructure.

## Batch 4 (gathered 2026-10-20; TheoV823 asked for full clusters, phased if too big)

Five unmarked `Post-` chats created 2026-10-13 to 10-20, each read in full with every collapsed turn expanded.

- **Phase 1 (6 insights, one per day 2026-10-23 to 10-28 via the scheduled publisher, #239-#244):** Claude Code review trusted decision boundary; OpenAI COBOL benchmark analysis; AI legacy modernization cornerstone; When Kubernetes Works but the Application Still Fails; Policy as Code vs the decisions behind it; Node.js to Go migration.
- **Phase 2:** behavioral equivalence vs architectural compliance (merges the migration chat's "why compiling is not enough"); Go translation idioms; strangler vs big-bang; when not to rewrite; platform engineering and enterprise architecture.
- **Evidence-gated:** infrastructure guardrail reference architecture, COBOL cutover checklist, controlled migration experiment, the runnable software-factory guide.
- **Merged, not built separately:** business-logic recovery (into the modernization cornerstone; 92.1 overlap with the reverse-engineering research piece), database connection budgets (into the Kubernetes piece), multi-language codebase governance (into the Node.js to Go piece).
- **Separate contracts:** the infrastructure governance concept page (owner decision; terminology amendment first) and the orchestrators site edit (#231).

**Ready to build** (build card complete; every citation still has to be verified during the build): OKF update to the June page. Shipped since: EY, The Return of the Silo Engineer and the pre-action mechanism article (#216); the AECP multi-agent piece, Claude Frontier Academy news piece, From Decision Records to Decision Governance and the reverse-engineering Research piece (#221).

**Small site edits:** done. The FDE cluster pages are on the agent-infrastructure hub, and `ai-makes-software-more-ambitious`, `agent-governance-in-the-sdlc` and `concepts/architectural-drift` link the coherence concept (both shipped with #214 and the topic work in #217).

**Folded into concept pages (not articles):** The Coherence Problem in Agentic Software Development (into Engineering Coherence); When Code Becomes Cheap, Decisions Become the Scarce Asset (a section of Engineering Decision Governance).

**Terminology amendment and both concept pages:** merged in #214 (2026-10-14). From Decision Records to Decision Governance, which waited on them, shipped in #221.

## Read before building

- **OKF overlaps a shipped page.** `open-knowledge-format-vs-governance` (2026-06-17) exists, and the OKF chat believed it did not.
- **CodeRabbit is mostly strategy, not an article scope.** The one content ask may fit better as a refresh of `/compare/coderabbit/`. Several roadmap and site asks were partly done by #179 and #193.
- **Pre-action is a mechanism, not a category** (decision 1): there is no pillar; the pre-action brief's definition article is retitled as a mechanism piece.
- **ROI backlog drift.** The verification-tax, DORA and NBER 240%/30% (`ai-throughput-is-not-engineering-throughput`) articles already shipped, `ai-adoption-maturity-model-engineering-analysis` overlaps the maturity-model item, and four articles scoped in the Sep 10 "Include stats" turn are missing from the ledger's list.
- Citations are copied from the chats and none is verified. Each brief lists what to re-check.

## Unmarked "Post-" chats not processed

Marker rule: a title containing `*` means processed (shipped, merged into a shipped article, or dropped). Matching the `Post-` prefix case-insensitively (including `***`-prefixed titles), the project had 163 `Post-` chats on 2026-10-12; 30 carry a `*` mark, leaving **133 unmarked**. By last-updated date:

- **13 newer than 2026-08-29**: the 8 chats from 2026-10-04 to 10-12 and the 5 earlier scopes, all briefed above.
- **32 last updated 2026-08-11 to 08-29** (one is `Post-tv-`, which never enters `site/`). The ledger said ~119 for this window, which does not match what ChatGPT returns. 12 were *created* in that window.
- **88 last updated before 2026-08-11** (earliest created 2026-05-06). Many probably shipped without a marker, so check `git log` first, per the publish-insight skill.

The ledger's "unmarked" count is unreliable; the git log is the real test of whether a chat shipped.

Full title and date list of the 133 was read from the ChatGPT project API during this session but is not reproduced here to keep the briefs focused. The older-chat titles are available on request. Titles seen include (updated Aug-Sep): Post-Identify Mneme's Harness Role (08-29), Post - AI Security Institute (AISI) - Assess AI Control Risks (08-29), Post-Assess hardware standard relevance (08-27), Post-Architectural Use Cases and Risks (08-20), Post-Concept-Architectural Drift Prevention (08-17), Post-AI Agents and Architecture (08-15).
