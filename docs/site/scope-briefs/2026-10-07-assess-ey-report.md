# Scope brief: Post-Assess EY Report

Status: **built 2026-10-14** as `/insights/ey-beyond-the-code-ai-software-development/` (batch 1 PR; not yet merged or deployed)

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Assess EY Report` |
| Created / last updated (UTC) | 2026-10-07 / 2026-10-07 |
| Shape | 3 turns: report assessment, "Scope article to capture SEO intent", then a retitle to name the report. The last turn sets the title. |
| Repo check | No page cites the EY report. Not shipped. |

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | **Decided 2026-10-12: "EY 'Beyond the Code' Report: AI Has Moved the Software Constraint Beyond Coding"** (confirm the verbatim report name). Background: Chat's final: "EY Report: AI Is Moving the Software Development Bottleneck Beyond Coding" (SEO title "EY Report: The AI Software Development Bottleneck Has Moved Beyond Coding"). "Bottleneck" is banned in house prose and fails `lint_prose.py`. The `voice-ok` escape covers only a block that quotes an external source verbatim (a title or a quotation), so it cannot cover a title Mneme writes. Proposed: "EY 'Beyond the Code' Report: AI Has Moved the Software Constraint Beyond Coding" |
| Slug | `ey-beyond-the-code-ai-software-development` (chat: `ey-ai-software-development-bottleneck`) |
| Report-anchored (ADR-015) | yes: entity = the report's verbatim title. The PDF file name suggests "Beyond the code: How AI is redefining the software industry" (2026); confirm on the cover |
| Topic hub | engineering-performance |
| Content type (`--type`) | Report Response (the EY report is the primary object) |
| OG headline | EY: Coding Is No Longer the Constraint (7 words) |
| Editorial gate | pass: named-report entry point plus new evidence (400-CTO survey) |
| Five questions | changed: AI made code generation cheap; matters: EY's CTOs rank QA, architecture/context and security above coding as delivery constraints; breaks: controls are mostly human review, only 20% trace AI-assisted code, about one in three had an AI-related production incident; do: move validation and decision context to machine speed; governance: determine which approved decisions apply to a change and enforce the enforceable ones |
| Cannibalisation | `find_overlap.py`: `cursor-developer-habits-report-governance-infrastructure` 51.1, `bain-ai-development-lifecycle-governance` 43.7 (different reports), `brooks-law-ai-coding-agents` 39.8. Verdict: **clear** (distinct named report). **Body search:** the "code is cheap, X is scarce" line is already argued in 10+ shipped articles (e.g. `ai-makes-software-more-ambitious`, `ai-roi-problem-is-about-systems-not-models`); this piece adds EY's survey evidence and must link them rather than restate the argument |
| Cross-links | the Engineering Coherence and Engineering Decision Governance concept pages once they exist, `ai-makes-software-more-ambitious`, `ai-roi-problem-is-about-systems-not-models`, `why-code-review-cannot-scale-with-ai-output`, `memory-is-not-governance`, `concepts/ai-native-sdlc`, `ai-coding-governance-should-be-reviewable`; the planned Engineering Decision Governance concept page once it exists |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 39 (directness 8, rhythm 8, trust 8, authenticity 7, density 8) |
| `lint_prose.py` | 0 errors; 1 warning kept: "EY" is the firm's legal brand name, not an abbreviation to expand |
| Cold read: thesis as restated | "With AI generating code cheaply, the real delivery constraints are now QA, architecture/context and security review, so teams need machine-applicable decision governance rather than relying on human review alone." Matches. |
| Cold read: unclear terms, and how resolved | Software Strategy Group (replaced with "EY's strategy consulting brand"), context-setting (glossed after the table), escaped defects (glossed), typed rules and hooks (glossed in Where Mneme fits), Mneme (introduced by its category). Unsourced generalisations ("few teams", "most teams") rewritten to EY figures; the four-layer stack is now attributed as Mneme's reading of EY. |

## Agreed scope

- **Thesis:** AI has not removed the software-development constraint; it moved it from producing code to deciding, validating and governing what gets produced. Mneme's step beyond EY: if architecture, context-setting and validation are the constraints, previously made engineering decisions need to become machine-operational controls.
- **Search intent:** "If AI makes coding faster, what becomes the new constraint in software development?" Answer before mentioning Mneme. Chat's primary keyword was "AI software development bottleneck" with secondaries (AI software engineering bottleneck, AI coding bottleneck, AI software development governance, AI coding agents governance, AI SDLC, AI-generated code review, AI software engineering productivity). The house-voice ban makes the primary keyword unusable in prose; decide whether to target "constraint" phrasing instead.
- **Meta description (chat):** "EY's survey of 400 CTOs finds QA, architecture and governance are becoming bigger software-development bottlenecks than coding. Here's what changes when AI makes code generation cheap." Needs rewording for house voice and the 150-160 character limit.
- **Structure (from the chat):**
  1. AI removed one constraint and exposed the others (put the numbers in a table up front; no Mneme yet).
  2. What are the biggest software-development constraints with AI? Answer-engine section, 2-3 sentence answer plus the EY ranking; attribute "According to EY-Parthenon's 2026 survey of 400 European CTOs".
  3. Why AI moves the constraint downstream (queueing; link, don't repeat, `why-code-review-cannot-scale-with-ai-output`).
  4. Architecture and context are becoming production constraints ("more context is not the same as authoritative context"; link `memory-is-not-governance`).
  5. Human review cannot be the control plane (EY control findings; Gartner as category legitimacy).
  6. The missing layer is decision governance (define compactly; do not optimise this article for "decision governance": AsDecided ranks an exact-match article, and the concept page should own the term).
  7. What changes for the AI-native SDLC (four layers: generation, context/retrieval, decision governance, deterministic validation plus evidence; link the concept page).
  8. The moat may move too (one section only; a separate "software moat" article later).
  9. FAQ, 4-5 questions, 60-100 words each.
- **Priority in chat:** P0, publish quickly while the report is news.

## Key facts, figures, sources

**Verified 2026-10-14** against the live PDF (read in Chrome via pdf.js on ey.com, then cross-checked with `pdftotext`). Verbatim cover title: *Beyond the code: How AI is redefining the software industry*, subtitle "Insights from 400 European software CTOs", 2026, EY-Parthenon with Potloc. Page numbers below are the report's printed pages.

| Claim | Source | Verified? |
|---|---|---|
| Survey of 400 CTOs across 13 European countries; CATI/CAWI interviews June 16 to July 10; ~43-minute average; 24% UK, 14% Germany, 13% France; size/turnover quotas | EY PDF (tracking query removed): https://www.ey.com/content/dam/ey-unified-site/ey-com/en-nl/services/strategy/documents/ey-beyond-the-code-how-ai-is-redefining-the-software-industry-2026.pdf | verified, pp. 40-41 |
| Top-3 SDLC constraints: QA/validation 54%, architecture and context-setting 39%, security/compliance 38%, requirements/specs 36%, code review 32%, test generation and test maintenance 24%, coding/implementation 22% | same | verified, p. 18, against the rendered chart image. Text extraction misorders this chart's labels and values (pdf.js put the 32% next to test generation); the Opus audit caught that swap in the first draft, and the rendered page confirms the scope chat's code-review figure |
| About one in three software companies had an AI/agent-related production incident in the past year | same | verified, pp. 18-19 ("roughly one-third"; breakdown base 100% = 131, pp. 20-21) |
| Controls in use: 62% mandatory human review before merge, 45% static/security analysis, 41% AI coding policies, 36% approved tool lists, 35% privacy/compliance checks, 34% automated test requirements, 20% traceability of AI-assisted code (plus 22% developer training) | same | verified, pp. 18-19 |
| Evidence boards would accept: 45% production AI/agent use cases with live controls and audit trail; 44% architecture and data foundations that absorb new AI use cases without rework | same | verified, pp. 8-9 (44% used; 45% not used) |
| CTO mandates: 69% primary rights over internal R&D coding agents; 45% production AI governance accountability; 45% model/vendor selection; 31% AI data governance | same | verified, pp. 26-27 (not used in the article) |
| One-third of CTOs expect over half of new or materially modified production code to be AI-authored within 3-5 years | same | verified, pp. 14-15 (not used) |
| Quote "AI didn’t remove the bottleneck — it pushed it downstream" | same; quoted once with `<!-- voice-ok: verbatim EY report heading -->` | verified, p. 18 (section heading) |
| Additional figures used: 56% redeploy saved time to QA and code review, 55% to new features; among CTOs who measure it, 84% improved lead time/release cadence and 60% saw no material change in escaped defects and incidents; "The construction of the software code is becoming replicable. The context around it is not."; "moved up the stack" | same | verified, pp. 6-7, 16-17 |
| Enterprise coding-agent market moving control and validation toward platforms | https://www.gartner.com/en/newsroom/press-releases/2026-05-20-gartner-says-the-market-for-enterprise-ai-coding-agents-is-entering-a-new-phase-of-expansion-and-competitive-realignment | verified 2026-10-14 in the in-app browser (scripted fetch returns 403): "by 2027, over 65% of engineering teams using agentic coding will treat integrated development environments (IDEs) as optional, shifting control, governance, and validation to automated platforms" |
| Exact-match competitor article "Decision Governance for Coding Agents" | https://asdecided.com/articles/decision-governance-for-coding-agents | not used (context only) |
| AI shifting the constraint toward requirements | https://www.wearedevelopers.com/videos/1855-the-intent-engineer-closing-the-gap-between-business-engineering-manuel-klein | not used |
| Investor framing of "software moat" | https://www.bailliegifford.com/en/uk/individual-investors/insights/ic-article/2026-q1-us-perspectives-is-ai-eating-software-10060821/ | not used (the moat section cites EY's own chapter instead) |

The chat linked some Mneme pages on `mail.mnemehq.com`; use `mnemehq.com` only (house rule). The chat says keyword volumes were not scored (Semrush API units exhausted).

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Mneme turns approved decisions into deterministic controls for applicable changes | SHIPPED for repository architectural decisions (verify scope wording) |
| Decision Index | SHIPPED (OSS, mneme-hq 0.10.0: canonical Decision Index persistence; the Decision MCP reads it). Cross-system ingestion is PLANNED; ADR-031 governance semantics are accepted but unreleased |
| Enterprise decision ingestion (Confluence, Jira, Teams, Slack) | Confluence ADR ingestion: PLANNED (site roadmap). Jira, Slack, Teams and telemetry connectors: CONCEPTUAL (the core roadmap plans a source-independent ingestion contract and warns against assuming such connectors) |
| Evidence/traceability of enforcement | check current state before claiming |

## Positioning constraints

- Use "decision governance" only after the terminology amendment (see the Business Type brief); until then describe the layer in plain words.
- The chat's "decision governance for agentic software development" category and "decision layer" thesis follow the PUBLISHING.md 2026-09-11 amendment: thesis framing on insights only, never as something Mneme ships in full.
- Do not overstate the survey: self-reported, European CTOs only.

## Non-insight site edits requested

None for the site. (Non-site follow-ups from the chat are tracked outside this public repository.)

## Open questions

- Title: decided. "Bottleneck" may appear once, inside a verbatim EY quote with `<!-- voice-ok: verbatim EY quote -->`.
- "Cheap code, scarce decisions" thesis: already argued on shipped pages (the Cohesion brief's insight 3 is blocked on that overlap); this article uses the survey as evidence and links `ai-makes-software-more-ambitious`.
- Verbatim report title for ADR-015.
- Publish before or after the Engineering Decision Governance concept page? (The chat routes authority into it.)
