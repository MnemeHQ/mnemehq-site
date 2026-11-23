# Scope brief: Post-Enterprise Architecture Pillar

Status: **gathered; two articles drafted and revised after round-1 cold read and audit, not built** (`architecture-principles-to-enforceable-decisions`, `will-ai-replace-enterprise-architects`); Articles 03 and 04 folded into an update of an existing insight (not built); pillar page and phase-2 articles held

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Enterprise Architecture Pillar` |
| Created / last updated (UTC) | 2026-11-18 / 2026-11-18 (creation date not exposed; project list shows Nov 18, in-chat stamp Wednesday) |
| Shape | 4 turns (2 user, 2 assistant); read in full, truncation check passed. Turn 2 proposes a pillar and five articles; turn 4 (final scope) settles on one pillar page, four supporting articles and two phase-2 articles. |
| Repo check | Heavy existing coverage. `platform-engineering-enterprise-architecture-decisions` (2026-11-13) already covers accept/revise/waive authority between architects and platform teams, waivers, agents raising the rate of change, and per-decision measurement (coverage, exceptions, intervention cost). Also `four-architecture-protection-states`, `are-your-adrs-enforceable`, `programmable-ai-policy-executable-architectural-intent`, `policy-as-code-engineering-decisions`, `forward-deployed-architects-need-a-decision-layer`, `dora-metrics-insufficient-for-agentic-development`, `/concepts/executable-architectural-intent/`, `/concepts/engineering-coherence/`, `/docs/how-to/adr-to-enforceable-decision/`. No page mentions TOGAF, ArchiMate or ISO/IEC/IEEE 42010; no page targets "architecture principles" or "will AI replace enterprise architects". |

## Verdict summary

| # | Proposed article | Verdict | Top overlap (score) |
|---|---|---|---|
| 01 | Will AI Replace Enterprise Architects? | **clear** (drafted) | `platform-engineering-enterprise-architecture-decisions` 61.1 |
| 02 | From Architecture Principles to Executable Governance | **re-angle** (drafted as "From Architecture Principles to Enforceable Decisions") | `platform-engineering-enterprise-architecture-decisions` 50.2; `/docs/how-to/adr-to-enforceable-decision/` 73.9 on keyword variant |
| 03 | Architecture Review Boards at Agent Speed | **update instead**: `platform-engineering-enterprise-architecture-decisions` | `platform-engineering-enterprise-architecture-decisions` (body); script top 36.5 |
| 04 | How to Measure Architecture Conformance in AI-Generated Software | **update instead** (same page) / evidence-gated | `/use-cases/ci-governance-for-ai-generated-code/` 73.8; `four-architecture-protection-states` 50.1 |

## Build card: Article 02

| Field | Value |
|---|---|
| Kind | insight |
| Title | From Architecture Principles to Enforceable Decisions |
| Slug | `architecture-principles-to-enforceable-decisions` |
| Report-anchored (ADR-015) | no |
| Topic hub | architectural-governance |
| Content type (`--type`) | Perspective (no named external anchor in title or lede) |
| OG headline | Principles Need Scoped, Checkable Decisions (5 words) |
| Editorial gate | pass: distinct query ("architecture principles" with AI agents / enforcement; unserved on the site) and cornerstone support for the EA cluster |
| Five questions | changed: agents implement changes that no reviewer reads against the principle list; matters: a principle has no scope or construct, so nothing can return a verdict on it; breaks: principles stay true on paper while changes ignore them; teams should: split each principle into scoped decisions per system and sort them by checkability; governance helps: checkable decisions get typed rules and verdicts that name the decision, judgment calls stay with named reviewers |
| Cannibalisation | `find_overlap.py` title + keywords: `platform-engineering-enterprise-architecture-decisions` 50.2, `/concepts/executable-architectural-intent/` 34.8, `claude-code-self-hosted-environments-architectural-governance` 22.4. Keyword variant (ADR, enforceable, deterministic check, human judgment): `/docs/how-to/adr-to-enforceable-decision/` 73.9, `are-your-adrs-enforceable` 50.2, `how-ai-coding-agents-use-adrs` 45.0, `/tools/adr-checker/` 42.8. All 40+ pages read. Verdict: **re-angle**. The existing pages start from an ADR or a decision and make it enforceable (`programmable-ai-policy-executable-architectural-intent` covers decision to scope to constraint to verdict; the concept page defines promotion). None starts one level up, at the enterprise principle. This article's own contribution is the principle-to-decisions split (one principle, several scoped decisions, each in a different protection state) and the per-principle profile. It must not re-explain enforcement surfaces or redefine executable architectural intent; it links to both. Body grep: no page mentions TOGAF, ArchiMate or 42010; "architecture principle" appears only in `microsoft-agentic-transformation-playbook-ai-agent-governance`, in passing. |
| Cross-links | `four-architecture-protection-states`, `platform-engineering-enterprise-architecture-decisions`, `programmable-ai-policy-executable-architectural-intent`, `/docs/how-to/adr-to-enforceable-decision/`, `/concepts/executable-architectural-intent/` |

## Build card: Article 01

| Field | Value |
|---|---|
| Kind | insight |
| Title | Will AI Replace Enterprise Architects? What the Role Keeps |
| Slug | `will-ai-replace-enterprise-architects` |
| Report-anchored (ADR-015) | no |
| Topic hub | architectural-governance |
| Content type (`--type`) | Perspective |
| OG headline | What AI Leaves Enterprise Architects (5 words) |
| Editorial gate | pass: distinct query ("will AI replace enterprise architects", "future of enterprise architecture"); supports the EA cluster through internal linking |
| Five questions | changed: AI drafts architecture documents and agents raise the rate of implementation; matters: EA governance was sized for periodic review of a few changes; breaks: boards see a shrinking share of what ships; teams should: measure decisions not documents, move conformance checks to every change, record who may change what; governance helps: checkable decisions run on every change and architects read coverage and exceptions |
| Cannibalisation | `find_overlap.py`: `platform-engineering-enterprise-architecture-decisions` 61.1, `forward-deployed-architects-need-a-decision-layer` 47.4 / 48.3, `future-of-software-engineering-after-vibe-coding` 35.9 / 40.8. All 40+ pages read. Verdict: **clear**. The platform-engineering article is about the handoff between architects and platform teams; the forward-deployed article is about embedded engineers capturing business-process knowledge; the vibe-coding article is about the software engineer's role. None answers the enterprise-architect role question. The draft links to the platform-engineering article for the delegation split instead of repeating it. |
| Cross-links | `platform-engineering-enterprise-architecture-decisions`, `forward-deployed-architects-need-a-decision-layer`, `future-of-software-engineering-after-vibe-coding`, `/concepts/engineering-coherence/` |

## Articles 03 and 04: update instead

**03, Architecture Review Boards at Agent Speed.** The chat's thesis (separate decision-making from verifying compliance; do not re-approve each implementation of an approved decision), its outline (what the board retains, what is delegated to platform teams and automated controls, waivers and superseded decisions) and its original asset (a responsibility matrix across board, architect, platform team, service team and agent) restate `platform-engineering-enterprise-architecture-decisions`, published 2026-11-13: its accept/revise/waive table, delegation record, waiver section and "Agents raise the rate of change" section. A new page would compete with a nine-day-old article for the same reader. Proposed update: add a short section to that article on what the architecture review board keeps (new decisions, revisions, exceptions) once conformance runs on every change, plus an FAQ entry targeting "architecture review board". `find_overlap.py` did not surface the page (top hits `/architecture/decision-memory-vs-documentation/` 36.5, `/docs/mcp/` 30.4, `github-agent-pull-requests-review-wrong-layer` 29.0); the overlap is in the body ("review board", "waiver", delegation), found by `git grep`.

**04, Measuring Architecture Conformance.** The chat's measures (protection coverage by the four Audit classifications, violations, evidence from decisions to checks) are already in the same article's "Measure the decision, not the control" section (coverage, exceptions, intervention cost) and in `four-architecture-protection-states` (50.1) and `are-your-adrs-enforceable`. `find_overlap.py` on title: `/use-cases/ci-governance-for-ai-generated-code/` 73.8, `dora-metrics-insufficient-for-agentic-development` 51.7, `hidden-cost-ai-generated-rework` 43.2; on keywords: `four-architecture-protection-states` 50.1, `/docs/how-to/install-mneme-and-activate-protection/` 42.3. The parts that would be new (first-attempt compliance, false-positive rates, a reproducible pilot evaluation) depend on Mneme's architecture-compliance benchmark and ADR research results, which the chat itself says not to use until ready. Mneme does not measure first-attempt compliance, false positives or intervention cost today. Verdict: fold the scorecard idea (declared vs verified protection, explicit denominators) into the same update, and revisit a standalone article when benchmark results publish.

## Draft quality gate (filled at build time)

| Check | Article 02 | Article 01 |
|---|---|---|
| stop-slop score (/50, pass >= 35) | 38 after revision round 1 (directness 8, rhythm 8, trust 8, authenticity 7, density 7; first draft 39, density down for the added definitions) | 39 after revision round 1 (directness 8, rhythm 8, trust 8, authenticity 7, density 8; first draft 38) |
| `lint_prose.py` (draft body) | 0 errors, 4 warnings, justified: ISO, IEC, IEEE and TOGAF are parts of standard names, not acronyms to expand; each standard is glossed at first use. 1,355 words, avg 12.9 words/sentence, Flesch 58 | 0 errors, 4 warnings, same justification. 1,162 words, avg 12.9, Flesch 57 |
| Cold read: thesis as restated | "Principles can't be checked by machines or agents; split each into scoped decisions, sort them by how checkable they are, and turn only the checkable ones into rules" (matches) | "AI can draft architecture documents but cannot own decisions, so architects shift to choosing, scoping decisions into machine-checkable form, and verifying them" (matches) |
| Cold read: unclear terms, and how resolved | typed rule, `FORBID_LITERAL`, `mneme check`, agent hook and content hash each defined in one clause at first use; Mneme introduced in plain words before the Audit, and "the Audit" defined with its link at first use; "Your job is to know which ones can" rewritten to name the architect who writes the decision; standards paragraph cut to what matters (none of the three checks a repository) | "construct to check" replaced with a plain example (an import that must not appear); "active typed rule" and the Audit labels removed from the role article (the principles article defines them); Decision Index glossed in one clause; "The site calls" self-reference removed; opening ISO/ArchiMate paragraph cut to two sentences; "Where Mneme fits" rewritten in plain words, three short paragraphs |
| Pre-merge Opus claim audit | round 1: FIX (A-D), all four applied verbatim (body and faq.json); C sits inside a shortened standards paragraph. Also changed "checked in CI" to "enforced in CI" for the terminology lock, matching Article 01's audit item 7. Re-audit pending | round 1: FIX (1-7). Items 1-5 applied verbatim (5 in body FAQ and faq.json). Items 6 and 7 applied in substance inside the rewritten "Where Mneme fits": item 6's wording kept verbatim ("so an architect can see, for one repository, which decisions a deterministic check protects today"); item 7's "enforced" kept as "Mneme enforces it in continuous integration (CI)", because the cold read asked to remove the phrase "active typed rule" around it. The Audit's four labels are no longer listed in this article. Re-audit pending |

## Agreed scope

Final turn: one evergreen pillar page at `/enterprise-architecture/` ("Enterprise Architecture in the Age of AI Agents"), four supporting insights, two phase-2 insights. Audience: enterprise architects, chief architects, CTOs and platform engineering leaders. Positioning boundary from the chat: EA is wider than Mneme (business capabilities, application landscapes, data, technology, investment); Mneme covers making technical architecture decisions operational in repositories, and the articles say so. Standards (ISO/IEC/IEEE 42010, TOGAF, ArchiMate) are reference points only, with no implied certification or conformance. The chat recommends avoiding broad "what is enterprise architecture" queries.

- 01 Will AI Replace Enterprise Architects? (awareness). Drafted.
- 02 From Architecture Principles to Executable Governance (principles to scoped decisions to checks; worked example: controlled data access becomes a scoped decision forbidding direct database access outside an approved adapter; introduce the four Audit classifications). Drafted under a re-angled title using the house term "enforceable" rather than the unlocked "executable governance". The worked example reuses the recorded output of `/docs/how-to/adr-to-enforceable-decision/` (ADR-012) rather than an invented check.
- 03 Architecture Review Boards at Agent Speed. Update instead (above).
- 04 How to Measure Architecture Conformance. Update instead / evidence-gated (above).
- Phase 2, **held**: "TOGAF, ArchiMate and ADRs: Connecting Enterprise Architecture to AI Implementation" and "Governing Legacy Modernisation When AI Agents Rewrite Applications" (the latter must build on `reverse-engineering-architectural-decisions-research` and the existing migration cluster, not duplicate them). Revisit after the pillar ships and search data exists.

## Key facts, figures, sources

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| ISO/IEC/IEEE 42010:2022 specifies requirements for the structure and expression of an architecture description for entities including software, systems and enterprises | https://www.iso.org/standard/74393.html | verified (ISO standard page, abstract; edition 2, published 2022-11; read in browser, curl returns 403) |
| The same standard "does not specify the processes, architecting methods, models, notations, techniques or tools by which an AD is created, utilized or managed" | https://www.iso.org/standard/74393.html | verified (ISO standard page, abstract) |
| TOGAF Standard is "a proven Enterprise Architecture methodology and framework" (The Open Group) | https://www.opengroup.org/togaf | verified (TOGAF page, opening paragraph). The page does **not** list the EA scope the transcript gives (business capabilities, applications, data, technology, transformation, investment); the articles do not attribute that scope to TOGAF. Article 01 states the wider scope in house voice and cites TOGAF only as an EA methodology and framework. |
| ArchiMate Specification is a modelling language for EA; describes business processes, organizational structures, information flows, IT systems and technical infrastructure, and relationships among business domains | https://www.opengroup.org/archimate-forum/archimate-overview | verified (ArchiMate overview page, first two paragraphs) |
| Audit classifies each decision as Protected, Mneme-ready, Requires modelling or Guidance | https://mnemehq.com/audit/ | verified (own site, audit page intro); definitions per `/insights/four-architecture-protection-states/` |
| Decision Index stores versions, lifecycle and source; does not store who approved a decision | https://mnemehq.com/docs/decision-index/ | verified (own docs, "What it does not record") |
| ADR-012 example: FORBID_LITERAL `from app.db.client import` on `app/handlers/**`; recorded FAIL output; same content passes under `app/repositories/` | https://mnemehq.com/docs/how-to/adr-to-enforceable-decision/ | verified (own docs, "Configure" step 2 and "Expected result"; tested with mneme-hq 0.11.0, matching `scripts/core_version.json`) |
| Reddit r/EnterpriseArchitect thread (practitioner sentiment) | reddit.com (blocked) | **dropped**: unreachable; owner chose to drop it. No sentiment claim appears in either draft. |

## Mneme claims and maturity

Checked against released mneme-hq 0.11.0 (`scripts/core_version.json`) via the site's docs pages.

| Claim (as written in the drafts) | Class |
|---|---|
| Mneme is an open-source decision and control layer for agentic software development (category line, ADR-001) | SHIPPED (category claim) |
| Mneme works at the decision and rule layers inside a repository; does not hold principles, model business capabilities, manage portfolios or replace EA tools | SHIPPED (scope limit) |
| ADRs are imported into the Decision Index, a persisted, versioned record of a repository's decisions | SHIPPED (`/docs/decision-index/`) |
| The index keeps each decision's lifecycle status and, for an imported ADR, the source file and its content hash | SHIPPED (`/docs/decision-index/`) |
| A decision with an active typed rule (02) / a rule a program can match (01) is enforced in CI, and before the write lands when a supported coding agent edits through its own file tools; the integrations page lists agents and paths | SHIPPED (`/docs/how-enforcement-works/`, integrations matrix; stated without naming agents to avoid drift) |
| A typed rule names exact text it forbids and the paths it covers (FORBID_LITERAL, `include_paths`) | SHIPPED (`/docs/how-to/adr-to-enforceable-decision/`, `/docs/how-enforcement-works/`) |
| `mneme check` fails on the ADR-012 example and names the decision; passes the same content under `app/repositories/` | SHIPPED (recorded output in the how-to) |
| Each verdict names the decision and rule it enforced (and version: `decision_version_id` in JSON) | SHIPPED (how-to JSON evidence) |
| The Audit classifies each decision it finds as Protected, Mneme-ready, Requires modelling or Guidance (02); in 01: the Audit shows, for one repository, which decisions a deterministic check protects today | SHIPPED (`/audit/`) |
| Protected = a typed rule exists on the decision and the Audit verified it; the how-to's audit reports ADR-012 as Protected once imported. Mneme-ready = one rule can express it without guessing, the Audit proposes it, nobody has activated it (02 only) | SHIPPED (`four-architecture-protection-states`, how-to) |
| The Decision Index does not record who approved a decision; keep approvals in identity-verified places such as PR review | SHIPPED limitation (`/docs/decision-index/`) |
| Linking a decision to an enterprise principle is an ADR-text convention, not a tracked field; governance across many repositories is not a Mneme feature today | SHIPPED limitation (stated as absent) |
| Principle-to-decision split, per-principle profile, "choose / scope / verify" role model | CONCEPTUAL (editorial model, not a Mneme feature) |

Article 02: 11 SHIPPED, 1 CONCEPTUAL. Article 01: 8 SHIPPED, 1 CONCEPTUAL (after revision; the four labels and typed-rule wording left the article). Article 01's empirical sentences about agent adoption are now framed as possibilities ("can make more changes", "is likely to build more"), per audit items 2, 3 and 5. No PLANNED or VALIDATED EXPERIMENT claims. Neither draft uses the ADR-031 decision-governance semantics, approval workflows, waiver records or cross-repository features.

## Positioning constraints

- EA is wider than Mneme; say so in each article and keep Mneme to the repository side.
- Do not attribute an EA scope list to TOGAF; cite TOGAF only as The Open Group describes it.
- Standards as references only: no claim that 42010, TOGAF or ArchiMate prescribe enforcement, and no certification or conformance implied.
- Do not present approval, waiver or exception management as a Mneme workflow; the Decision Index records no approver.
- No conformance metrics (first-attempt compliance, false positives) until benchmark results publish.
- "Architecture Execution Gap" (the chat's proposed signature concept) is **not used** in either draft: it is a new defined term and needs an owner decision and a PUBLISHING.md terminology amendment first.

## Non-insight site edits requested

- **Pillar page `/enterprise-architecture/`**, "Enterprise Architecture in the Age of AI Agents" (2,000 to 2,500 words). **Separate follow-up, not an insight**: a new top-level page follows its own contract, not this procedure. Until it exists, the two drafts link to existing hubs (the architectural-governance topic hub, the platform-engineering article, concept pages). Add the pillar link to both articles when the page ships.
- **Update to `platform-engineering-enterprise-architecture-decisions`** absorbing Articles 03 and 04 (review-board section, FAQ, declared-vs-verified scorecard note). Substantial prose change, so it passes both pre-merge gates.
- An "Enterprise Architecture" topic filter on Insights once the cluster has enough material; no new primary navigation item (chat's own advice).
- Other follow-ups from the chat (CTAs, reporting and distribution) are tracked privately.

## Open questions

1. Owner: build the pillar page at `/enterprise-architecture/`, and under which contract? Until then the articles link to existing hubs.
2. Owner: admit "Architecture Execution Gap" as a defined term (terminology amendment), or keep it out? Drafts avoid it.
3. Owner: confirm Articles 03 and 04 become an update to `platform-engineering-enterprise-architecture-decisions` rather than new pages.
4. Once both drafts ship, add a reciprocal link between them (01's "Scope" job points to 02).
5. Phase-2 articles held; revisit after Search Console data on the cluster.
