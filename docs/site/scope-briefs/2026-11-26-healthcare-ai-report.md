# Scope brief: Post-Assess Healthcare AI Report

Status: **5 insights built** (HC-A01 #339 queued 12-01, HC-A03 #340 12-02, HC-A04 #341 12-03, HC-A07 #342 12-04, HC-A08 #343 12-05); HC-A02 use-case page, HC-A05/A06/A10 and the topic hub not built

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Assess Healthcare AI Report` |
| Created / last updated (UTC) | 2026-11-26 / 2026-11-26 |
| Shape | 21 turns, read in full. The truncation check passed: no "Show more" marker remains. The first turn assesses Menlo Ventures' "2026: The State of AI in Healthcare" report. The site scope is set in the turn that answers "We should create one use case for healthcare and as content pillar. Scope". Later turns change no site scope. Non-site follow-ups from the chat are tracked privately. |
| Repo check | Overlapping pages, to link and not repeat: /insights/ai-governance-for-regulated-industries/ (Perspective, architectural-governance) and /insights/ai-coding-agents-life-sciences-governance/ (Perspective, architectural-governance). /use-cases/data-platform-governance/ already covers data platform governance. No page covers the Menlo report (`git grep -i menlo -- site/insights` returns nothing). |

## Agreed scope (series)

The chat proposes a healthcare vertical: one commercial use-case page plus a series of insights about how engineers build, change and verify healthcare software with AI. It does not take on general healthcare AI governance, which is a crowded market and the wrong query. The governing distinction is that Mneme governs the software engineering decisions underneath healthcare AI systems, not the clinical decisions the AI makes.

The chat's ten-article list is HC-A01 to HC-A10. The owner approved this subset and these dates:

| ID | Working title (chat) | Publish on | Status |
|---|---|---|---|
| HC-A01 | Who Governs the Code Behind Healthcare AI? (report response to Menlo; follows the chat's 8-point structure) | 2026-12-01 | in this batch |
| HC-A03 | Preventing Patient Data Boundary Violations in AI-Generated Code | 2026-12-02 | in this batch |
| HC-A04 | Architectural Fitness Functions for Medical Device Software | 2026-12-03 | in this batch |
| HC-A07 | Governing FHIR Integrations in AI-Assisted Development | 2026-12-04 | in this batch |
| HC-A08 | IEC 62304 and AI-Assisted Software Engineering | 2026-12-05 | in this batch |
| HC-A02 | Architectural Governance for AI-Assisted Healthcare Software | n/a | the use-case page, not an insight; separate page-contract PR (below) |
| HC-A05 | From Architecture Decision Records to Verifiable Compliance Evidence | n/a | deferred pending re-angle |
| HC-A06 | Why AI Code Review Is Insufficient for Regulated Software | n/a | deferred pending re-angle |
| HC-A09 | Architectural Governance for Pharmaceutical Data Platforms | n/a | dropped: covered by /use-cases/data-platform-governance/ |
| HC-A10 | Can AI Coding Agents Safely Modify Medical Device Software? | n/a | deferred pending re-angle |

Audience: CTOs, VPs of Engineering, platform engineering leaders, software architects and software quality leaders in digital health, MedTech, pharmaceutical technology and healthcare SaaS.

Lanes within the batch: HC-A01 is the market-awareness entry point from the Menlo report. It keeps the patient-data scenario to one short worked example. HC-A03 owns the technical treatment of patient-data boundaries. HC-A04 owns fitness functions. HC-A07 owns FHIR. HC-A08 owns IEC 62304 and regulatory framing.

## Positioning constraints

- Distinguish supporting technical controls from demonstrating regulatory compliance. Mneme is not a medical device certification or compliance management platform. Never write that it ensures HIPAA (or any other) compliance, or that it enforces patient-data isolation at runtime.
- Mneme governs software engineering decisions in the code (dependency boundaries, approved routes, recorded decisions). It does not govern clinical decisions, model outputs or clinical validation.
- No regulatory or legal advice framing. Standards such as IEC 62304, ISO 14971, FDA device software guidance, HIPAA, EU MDR, GxP / 21 CFR Part 11 and HL7 FHIR may be described and cited, but how they apply to an organization is for its quality and regulatory teams.
- Mneme claims stay at the released core version (`scripts/core_version.json`). Enforcement is exact-literal typed rules with optional path scope, at supported agent hooks (native writes) and in CI. Hooks fail open by default. Data-flow and layer-structure rules are roadmap. The Decision Index records no approver identity.
- The chat's illustrative decisions (analytics must not import the clinical patient repository; external AI calls go through an approved model gateway) are the shippable examples. Clinical-workflow review, FHIR contract preservation and log redaction are expansion areas, not enforceable capabilities today.
- Avoid broad keywords such as "AI in healthcare". Do not use "Decision Engineering". Use the terminology lock (decision corpus, enforcement, drift).
- The chat's search-term list is hypothesised, not measured. Titles are validated against `find_overlap.py`, and against Search Console where data exists.

## Non-insight site edits requested

- **HC-A02, healthcare use-case page** (`/use-cases/healthcare-software-governance/` proposed in the chat): a separate page-contract PR under `.claude/skills/publish-page/SKILL.md`, not part of the insight PRs. The chat proposes the hero, the problem statement, a patient-data-isolation reference scenario and the Architecture Protection Audit as the conversion step.
- **Insights topic hub** "Healthcare & Regulated Software Engineering" (`/insights/topics/healthcare-regulated-software/` proposed): not created in this batch. The articles use existing hubs. Adding an eighth hub would change `TOPIC_NAMES` in `scripts/new_article.py` and the archive sections, so it would need its own PR and an owner decision.
- No insight in this series may describe a healthcare demo or reference implementation as shipped.

## Open questions

- Whether to create the healthcare topic hub once the five articles and HC-A02 are live. Re-home them then.
- Re-angles for HC-A05, HC-A06 and HC-A10 before any of them is scoped.

## HC-A01: Menlo's State of AI in Healthcare 2026: Who Governs the Code?

Publish on: 2026-12-01 (first in the series). Series working title "Who Governs the Code Behind Healthcare AI?" (chat, HC-A01). The entity now leads the title, per ADR-015.

### Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | Menlo's State of AI in Healthcare 2026: Who Governs the Code? (use this string verbatim in all six title fields; 60 chars) |
| Slug | `menlo-state-of-ai-in-healthcare-2026-code-governance` |
| Report-anchored (ADR-015) | yes: entity = "State of AI in Healthcare 2026" with publisher "Menlo". The report's own title is "2026: The State of AI in Healthcare". Body and FAQ cite that exact form; the title uses the searchable order. The meta description leads with Menlo Ventures and $3.7B / 2.5x, both in the body. |
| Topic hub | architectural-governance |
| Content type (`--type`) | Report Response (the article's primary object is a named industry report) |
| OG headline | "Menlo's State of AI in Healthcare 2026" (7 words; leads with the same entity as the title, per PUBLISHING.md OG rule; changed from "Menlo Healthcare AI 2026: Who Governs Code?" after audit F4). |
| Eyebrow | Report Response · Architectural governance · 10 min read |
| Editorial gate | pass: named-source entry point (no existing page covers the Menlo report; `git grep -i menlo site/insights` returns nothing). It also supports a cornerstone: it links into /insights/ai-governance-for-regulated-industries/ and opens the healthcare series. |
| Five questions | What changed: healthcare AI spend reached $3.7B (2.5x), growth moved toward clinical copilots and patient-facing agents, and Menlo says AI coding has made product advantages less durable. Why it matters: the software that delivers clinical AI is shipped faster, increasingly with coding agents, and it carries deliberate patient-data and model-routing boundaries. What breaks: an AI-written change can pass its tests and review and still cross one of those boundaries. What teams should do: inventory the boundaries, sort them by checkability, run rules at the agent hook and in CI, give the rest owners, and decide what evidence to keep (six-item audit list). How governance helps: decisions with exact rules become checks that run on every change, independently of the agent, and name the decision when they fail. |
| Cannibalisation | `python scripts/find_overlap.py "Menlo's State of AI in Healthcare 2026: Who Governs the Code?" --keywords "state of ai in healthcare 2026,menlo ventures healthcare ai report,healthcare software engineering governance,ai coding agents healthcare"`. Top hits: stanford-ai-index-2026-engineering-governance 82.4; /concepts/autonomous-software-engineering-governance/ 81.3; datadog-state-of-ai-engineering-governance-crisis 79.2; palantir-agentic-governance-engineering-governance 73.9; cursor-developer-habits-report-governance-infrastructure 72.6; loop-engineering-ai-coding-agents 66.7; /open-source-ai-coding-agent-governance/ 66.5; four-architecture-protection-states 66.0; gartner-ai-governance-engineering-governance 64.1; ai-coding-agents-life-sciences-governance 62.0. Every hit at 40 or more matches on generic terms ("2026", "state", "AI coding", "engineering governance"), not on Menlo or healthcare. None of them serves a search for the Menlo report. ai-governance-for-regulated-industries (Perspective: provenance and auditability across regulated verticals) and ai-coding-agents-life-sciences-governance (Perspective: FDA computer software assurance and GxP) share the vertical but neither the source nor the thesis, so both are linked rather than repeated. **Verdict: clear.** Within the batch: HC-A03 (patient data boundary violations) owns the deep technical treatment of the boundary scenario. This article keeps it to one worked paragraph and two decisions, with no code listing. It does not touch fitness functions (HC-A04), FHIR (HC-A07) or IEC 62304 / FDA guidance (HC-A08). |
| Cross-links | Out: /insights/ai-governance-for-regulated-industries/, /insights/ai-coding-agents-life-sciences-governance/, /insights/gartner-ai-governance-engineering-governance/, /concepts/architectural-drift/, /docs/decision-index/, /docs/governance-violations/, /integrations/, /audit/, /tools/adr-checker/. Reciprocal (manifest): the same three insights. |

### Draft quality gate

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 36/50 after both revision passes (unchanged by audit-2: B1 adds two plain factual sentences, B2 a descriptor) (was 38 on the first draft): directness 8, rhythm 7, trust 7, authenticity 7, density 7. The cold-read definitions (clinical copilots, ambient scribes, front-office AI, vertical AI, Morning Consult, typed rule, pre-write hook, fail open, data-flow analysis, layer structure, GitHub Actions gate, Claude Code, Decision Index) cost some density and trust. The first pass had already cut a meta closer, merged two quotable one-liners, restated a "not X, Y" contrast and removed three unsourced generalisations. |
| `lint_prose.py` | Run on revised body.html: errors 0, warnings 0 (after audit-2: 2,157 words, 160 sentences, average 13.5 words per sentence, 1% over 30 words, Flesch 62). CLI is expanded at first use in "Codex CLI (OpenAI's command-line coding agent)". Re-run on the built page in Stage 4. |
| Cold read: thesis as restated | "Healthcare AI spending is surging and AI coding tools add pressure to ship fast, so healthcare engineering teams need architectural decisions (especially patient-data boundaries) turned into automated checks that run on every change, because tests and code review alone will not reliably catch AI-written violations." This matches the brief's thesis. The action was read correctly: healthcare CTOs and engineering leaders run the six-item audit list, then the Architecture Protection Audit. |
| Cold read: unclear terms, and how resolved | Every flagged term is now defined at first use or removed. Mneme is introduced in one plain sentence before the mid-article CTA band. The band no longer uses "deterministic check" or "ADR": it says "automated rule" and "architecture decision record", and its copy explains the audit. Defined inline: Morning Consult, vertical AI, clinical copilots, front-office AI, ambient scribes, EHR (moved to first use), typed rule, pre-write hook, fail open, data-flow analysis, layer structure, GitHub Actions gate, Claude Code, Codex CLI, Decision Index (described before it is named). "Requires modelling" was made non-circular. The incumbents-versus-startups context is set up (startups held 67% of a $600M scribing market in 2025; Microsoft and Epic took two of every three new dollars in 2026). Reread sentences rewritten: the title reference, the "Suppose" hypothetical, the exact-text limits, independence, the repeated "every change", and the vague "that record". |

**Thesis (for the cold-read comparison):** Menlo's report shows healthcare AI moving into clinical and patient-facing products, built under pressure from fast AI coding. Healthcare AI governance covers the models, so the architectural decisions in the code that delivers them (patient-data boundaries, single routes to external models) need their own checks: exact rules run at the agent hook and in CI, independently of the agent, with owners for whatever a rule cannot cover.

**Agreed structure (chat, 8 points) and where each lands:** 1 Menlo findings → "What Menlo's State of AI in Healthcare 2026 found" and "The one line about AI coding". 2 Healthcare AI governance vs governing healthcare software engineering → "Healthcare AI governance and the software around it". 3 → "How an AI-written change breaks a decision". 4 → "Why passing tests is not enough". 5 → "Architectural decisions as engineering controls". 6 → "A patient data boundary, worked through" (kept short for HC-A03). 7 → "Independent verification and traceability". 8 → "What healthcare CTOs should audit before expanding AI coding". Then "Where Mneme fits" and the FAQ.

### Key facts, figures, sources

Primary source: Menlo Ventures, "2026: The State of AI in Healthcare", November 16, 2026. Web page: https://menlovc.com/perspective/2026-the-state-of-ai-in-healthcare/ . PDF: https://menlovc.com/wp-content/uploads/2026/11/menlo_ventures_healthcare_ai_report-2026-112026.pdf (21 pages). Both were fetched 2026-11-26. Every figure below appears in the report's prose, and the PyMuPDF text layer was checked page by page. The Step E audit rendered pages 1-5 and 8-10 as images; the p3 chart splits pharma's $700M into $600M discovery and research and $100M commercial and other.

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| Published November 16, 2026, titled "2026: The State of AI in Healthcare" | PDF p1 header; web page header | verified |
| September 2026 Morning Consult survey of 550 executives, director level and above, who took part in procuring an AI solution: 150 provider technology decision-makers, 100 health plan / benefits executives, 300 pharma and biotech executives | PDF pp20-21, "Data Sources and Methodology" | verified |
| Healthcare AI spend grew 2.5x to $3.7B in 2026; largest vertical; more than double legal ($1.8B) | PDF p1 Key Findings; p2 | verified |
| 50% of healthcare AI spend goes to industry-specific applications vs 24% across all enterprises | PDF p3 ("Fifty percent"); p4 (24%) | verified |
| Clinical copilots grew 5.5x to $550M; patient engagement and front office grew 4.5x to $450M | PDF p1; p3; p9 | verified |
| Pharma AI spend went from $30M to $700M, of which drug discovery and research is $600M | PDF p2; p3 chart (Pharma $700M = Discovery + research $600M + Commercial + other $100M); p5 ("$600 million") | verified. p1 Key Findings labels the full $700M "AI for drug discovery", which the p3 chart and p5 body contradict, so the article attributes $700M to pharma overall. The report also gives "28.6x" (p3, discovery + research) and "23x" (p1, p5, all pharma); the article states neither multiple. |
| 51% of pharma run AI at scale, up from 15% | PDF p5 | verified |
| Ambient scribes $950M; still the largest category | PDF p3 ("ambient scribes ($950M) and coding and billing ($600M) still lead") | verified |
| Scribing was led by startups in 2025: 67% of a $600M market | PDF p8, "Scribing: The Empire Struck Back" | verified |
| Microsoft and Epic took about two of every three new scribing dollars | PDF p2 ("captured $2 of every $3 of new scribe spend"); p1 says 68% of new scribing dollars | verified. p9 waterfall labels the incumbents Microsoft and Epic (68% of the $350M increase); the article uses the p2 "$2 of every $3" wording. Descriptor per audit-2 B2: Microsoft is named for its Dragon Copilot scribe (p9), and Epic as the EHR maker (p9 lists Epic among the EHRs). |
| Quote: "Rapid advances in AI coding have made product advantages less durable, increasing competitive pressure." | PDF p8, "Provider AI Moves from Paperwork to Patients" | verified verbatim |
| Menlo portfolio companies named in the report include Anthropic, OpenEvidence, Benchling and Assort Health, each asterisked as a portfolio company | PDF p4 (Anthropic*, OpenEvidence*), p6 (Benchling*), p11 (Assort Health*), p21 footnote; closing section p20 | verified |
| The report does not measure how much healthcare software is AI-written | Full-text search of the PDF: "coding" appears only for medical coding and billing, plus the p6 and p8 lines | verified (negative check) |
| Cut, not used: procurement times rose from 7 to 10 months (health systems) and 5 to 11 months (outpatient) | PDF p13 (p2 Key Findings gives "10 to 11 months vs. five to seven") | verified but cut: not needed for the argument, and the two passages disagree |

### Mneme claims and maturity

Checked against site/docs/ (how-enforcement-works, governance-violations, decision-index, protection-activation), /setup/, /audit/, and the released core version in `scripts/core_version.json` (0.11.0).

| Claim (as worded in the body) | Class | Source |
|---|---|---|
| Mneme is open source, stores a team's architectural decisions in its repository and checks code changes against them | SHIPPED | /docs/how-enforcement-works/ |
| A decision is enforced when it carries an active typed rule, a version of the decision a program can check. The released version ships two kinds: one forbids exact, case-sensitive text, optionally path-limited; the other sets an upper limit on a number in Python code, checked only by a whole-file command-line audit, not by the CI gate or the agent hooks | SHIPPED (FORBID_LITERAL and FORBID_NUMERIC_ABOVE are the two `TYPED_RULE_KINDS` in mneme-hq 0.11.0). FORBID_NUMERIC_ABOVE is Python-only and is decided only by the whole-file `mneme check --source-file` audit; the CI gate and the agent hooks do not support it, and the body says so (audit-2 B1). | core v0.11.0: `mneme/adr_constraints.py`; CHANGELOG v0.11.0; docs/releases/v0.11.0.md ("Edits, existing-file writes, Bash, Stop, CI and the other integrations are not covered"); docs/integrations/adr-import.md. /docs/governance-violations/ describes FORBID_LITERAL only. |
| A change that breaks a rule returns a FAIL that names the decision behind it (violations only; a PASS names no decision, and the article never says every verdict names one) | SHIPPED (violations name the decision) | /docs/how-enforcement-works/ "From decision to verdict" |
| A decision without an active typed rule is not enforced | SHIPPED (statement of a limit) | /docs/how-enforcement-works/ ("Retrieval is not enforcement") |
| Checks run in CI on pull requests through a GitHub Actions gate | SHIPPED | /docs/how-enforcement-works/ diagram ("GitHub CI · Actions gate") |
| In Claude Code the hook checks a change before Edit, Write and MultiEdit write it; most shell writes are checked at the end of the agent's turn; Codex CLI also has a supported hook; hooks fail open by default; the integrations page lists per-agent coverage | SHIPPED (the single cat-heredoc form, also checked before the write, is not mentioned; the article makes no claim beyond Edit/Write/MultiEdit) | /integrations/; /setup/ |
| Those hooks fail open by default | SHIPPED (stated limit) | /setup/ ("Hooks fail open by default") |
| Decision Index records each decision's version history, lifecycle status and source, and does not record who approved a decision | SHIPPED (0.10.0+) | /docs/decision-index/; PUBLISHING.md 2026-10-12 amendment |
| Rules that follow data flow or layer structure are not enforced today | SHIPPED (stated limit); such rule types are on the roadmap = PLANNED, and the article does not promise them | /docs/governance-violations/ ("Roadmap rule type · Represented, not yet proven") |
| The Architecture Protection Audit reads recorded decisions and sorts each as Protected, Mneme-ready, Requires modelling or Guidance, with those definitions | SHIPPED | /audit/; /docs/protection-activation/ |
| Mneme does not govern clinical models or their outputs, does not replace code review, and does not make software compliant with any healthcare regulation | SHIPPED (negative scope statement) | /docs/how-enforcement-works/ ("Mneme doesn't replace your coding agent, CI system, policy engine, or code review") |
| Worked scenario: a rule forbidding `clinical.repositories` under `analytics/` fails the import; in an agent with a pre-write hook the write by the agent's own file-editing tool is stopped (audit F3 wording); aliased or relative imports that spell out `clinical.repositories` still match; an import that never spells it out (such as `from clinical import repositories`) or access through a third module would not (reproduced in audit-3 with mneme-hq 0.11.0 `mneme.rule_matcher.literal_in_text`) | SHIPPED semantics (literal, path-scoped), framed as "Suppose"; an illustration, not a shipped healthcare demo | /docs/governance-violations/ |

Not claimed anywhere: HIPAA or other compliance, runtime patient-data isolation, data-flow analysis, approver identity, any healthcare demo or reference implementation, or the broader evidence return path (PLANNED, shown dashed on /docs/how-enforcement-works/). "Decision Engineering" is not used.

### Open risks for E (claim audit)

- Title form: "Menlo's State of AI in Healthcare 2026" is not the report's own word order ("2026: The State of AI in Healthcare"). The search-friendly order follows the "State of Startups 2026" precedent. Flag this if the auditor reads ADR-015's "verbatim" strictly.
- The worked scenario overlaps HC-A03's subject. It is kept to prose with no code listing, but the HC-A03 drafter should not reuse the same `clinical.repositories` / `analytics/` example word for word.
- The general traceability paragraph ("A version history of each decision tells a later reader what the decision said and what it replaced") is about practice in general, not a Mneme linkage claim. Confirm the auditor reads it that way.

### Revision pass (after audit F1-F7 and cold read)

- F1 and F2 applied: pharma's AI spend went from $30M to $700M, $600M of it on drug discovery and research (body and FAQ). F3 applied: the pre-write hook wording is limited to the agent's own file-editing tool. F4 applied: OG headline. F5 applied: the source rows. F6 and F7 applied: the briefs no longer mention any planned healthcare demo or reference implementation.
- Advisory wording applied: "in the team's repository"; FAQ 4 now opens "No tool on its own makes code compliant."
- Cross-batch facts applied: two typed rule kinds in 0.11.0; Claude Code checks Edit, Write and MultiEdit before the write and most shell writes at the end of the turn; only violations name the decision. Kiro is not mentioned.
- faq.json was regenerated from the visible FAQ, so the two match.
- A fresh re-audit (claim-audit §5) is still required.

### Revision pass 2 (after audit-2)

- B1 applied: the body now says the second typed rule kind sets an upper limit on a number in Python code, is checked only when a whole Python file is audited from the command line, and is not supported by the CI gate or the agent hooks.
- B2 applied: Microsoft is named with its Dragon Copilot scribe; Epic is the maker of the EHR software many hospitals run. Microsoft is no longer described as an EHR vendor.
- B3 applied: the Mneme claims row for typed rules records the two `TYPED_RULE_KINDS` in 0.11.0, the Python-only, whole-file scope of FORBID_NUMERIC_ABOVE, and the core sources.
- Advisory applied: the Microsoft/Epic source row now cites the p9 waterfall (68% of the $350M increase, labelled Microsoft and Epic).
- lint_prose and stop-slop were re-run after these edits (see the Draft quality gate). A fresh re-audit of the two edited body sentences and the brief row is still required.


Revision pass 3 (after audit-3): B4 body sentence and B5 brief cell replaced with audit-3 text by the orchestrator.

# HC-A03: Preventing Patient Data Boundary Violations in AI-Generated Code

Section for the series brief `Post-Assess Healthcare AI Report` (chat 2026-11-26). Series slot HC-A03, technical intent, publish 2026-12-02.

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | Preventing Patient Data Boundary Violations in AI-Generated Code |
| Slug | `preventing-patient-data-boundary-violations-ai-generated-code` |
| Report-anchored (ADR-015) | no. No named report is the spine; HIPAA text, Veracode and Perry et al. are supporting citations. |
| Topic hub | `architectural-governance` (same hub as the two regulated-industries pieces it links; switch if a healthcare pillar hub lands first) |
| Content type (`--type`) | Guide (primary object is a task: stop an agent crossing a patient data boundary) |
| OG headline | Keep patient data inside its boundary (6 words) |
| Editorial gate | pass: distinct query (patient data boundary / HIPAA access control applied to AI-generated code; no existing page covers it) and cornerstone support (links up to `ai-governance-for-regulated-industries`) |
| Five questions | **Changed:** agents now write the imports that decide which components reach patient records; models write compiling code >95% of the time but secure code ~55% (Veracode, Mar 2026); HHS proposed requiring a map of how ePHI moves (Jan 2025, final projected Jul 2027). **Matters:** 164.312(a)(1) limits access to "persons or software programs" granted rights; a new import is a new program with access that nobody approved. **Breaks:** analytics imports the clinical repository, identifiers reach logs, a model call skips the gateway; tests pass, and the engineer using the assistant misses it (Perry et al.). **Do:** list boundaries, one ADR each, encode import forms, add an import graph check, check while the agent works and before the merge, protect governance files. **Governance:** a typed rule fails the change at the hook and in CI and names the decision; it does not prove compliance or isolate data at runtime. |
| Cannibalisation | `find_overlap.py "Preventing Patient Data Boundary Violations in AI-Generated Code" --keywords "patient data boundary,PHI,HIPAA,AI-generated code,data isolation,healthcare software"`: 79.3 `/use-cases/ci-governance-for-ai-generated-code/`; 42.2 `/insights/ai-coding-productivity-gains-rework/`; 42.1 `/insights/hidden-cost-ai-generated-rework/`; 40.0 `/insights/enforce-engineering-standards-across-ai-assisted-teams/`. All matches are on the generic tokens "AI-generated code"; none on patient, HIPAA, PHI, boundary or isolation. Read the 79: a generic product use case for running `mneme check` in CI, no healthcare, data or HIPAA content; a searcher for patient data boundaries is not served by it. 42/42/40 are rework/standards pieces, unrelated intent. Body grep (`164.312`, Veracode, Perry, import-linter, CWE-532, `clinical.repositories`) finds no existing insight using these sources. **Verdict: clear.** Link to the CI use case is not needed; the article links the CI how-to instead. **Batch overlap:** HC-A01 (market awareness) also lists the patient data isolation scenario as one section; A03 owns the technical depth (rule, verified variants, limits), so A01 should summarise and link here. HC-A04 (fitness functions) may also mention import graph tools; A03 names Import Linter only as the transitive-path complement. HC-A07 (FHIR) and HC-A08 (IEC 62304) are not touched: no FHIR, no device-software lifecycle content here. |
| Cross-links | Out: `/insights/ai-governance-for-regulated-industries/`, `/insights/ai-coding-agents-life-sciences-governance/`, `/concepts/architecture-as-code/`, `/docs/how-to/adr-to-enforceable-decision/`, `/docs/how-to/stop-agent-crossing-architectural-boundary/`, `/docs/how-to/fail-pull-request-that-breaks-adr/`, `/audit/`. Reciprocal hosts: `ai-governance-for-regulated-industries`, `ai-coding-agents-life-sciences-governance`, `ai-coding-agent-guardrails`. |

## Draft quality gate

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | **Revision 2 (after audit F1-F2 and cold read): 40/50**: directness 8, rhythm 8, trust 8, authenticity 8, density 8 (density down one for the added definitions). Revision 1: **41/50**: directness 8, rhythm 8, trust 8, authenticity 8, density 9. Revisions made: removed "Here is" openers (2), "quietly", "just", "reliably", "actually"; rewrote the ADR intro sentence. Positive checks hit: specific case (ADR-021 with recorded output), disagreeable claim (an import is a new program with access under 164.312(a)(1)), non-obvious angle (verified table of what the rule misses), actor, clean stop on the checklist. |
| `lint_prose.py body.html` | Revision 2: 2202 words, avg 15.1 words/sentence, 5% over 30, Flesch 59, 0 errors, 1 warning (PHI, justified as below). Revision 1: 1921 words, avg 15.7 words/sentence, 10% over 30, Flesch 57. **errors: 0**; warnings: 1, justified: `PHI` appears only inside the verbatim HHS quotation ("e-PHI"); the term is expanded at first use as "electronic protected health information (ePHI)". |
| Cold read: thesis as restated | Run by the coordinator (`coldread.md`): "approved patient-data boundaries stop matching the code unless each boundary is written as a machine-checkable rule that runs before the agent writes a file and before the merge ... import-graph tools and runtime controls must cover the rest." Matches the brief thesis. |
| Cold read: unclear terms, and how resolved | All resolved in revision 2. Mneme introduced in one plain sentence before `mneme check` and before the version ("an open-source command-line tool"; mneme-hq named as its Python package). Defined at first use: decision file (`.mneme/project_memory.json`), typed rule (defined as a rule in a fixed form the tool can check mechanically; FORBID_LITERAL named as the one the hook and CI apply; FORBID_NUMERIC_ABOVE deliberately not mentioned, see revision 3), FORBID_LITERAL, `status`/`scope`/`priority`, Claude Code, Edit/Write/MultiEdit, hook, "finishes its turn", GitHub Actions, required status check, CODEOWNERS/code owners, import graph, transitive reachability, re-export, static check, CI. Audit named "Architecture Protection Audit" everywhere (page title of `/audit/`), CTA included; tier list dropped. Added "The ADR and code in this article are illustrative; the results are from real runs of the released tool." "Risk analysis" tied to HHS's Guidance on Risk Analysis by name. "Before the write" heading renamed "while the agent works"; shell-write timing now its own paragraph. List items referred to by name, not number. Reread sentences rewritten: import-graph sentence, "Software programs are named", the Veracode leap (F1), the verdict/audit-controls sentence (now tied to 164.312(b) and split), the "sensible split" sentence. |

## Agreed scope

From the chat's series scope (HC-01 pillar, table row HC-A03, and the HC-DEMO-01 patient data isolation scenario with HC-ADR-001 "Analytics cannot import the clinical patient repository", HC-ADR-002 model gateway, HC-ADR-005 sensitive information in logs). The chat says the demo "must verify the supported rule semantics, including what import variants the checker can and cannot detect" and that messaging must separate "supporting technical controls" from "demonstrating regulatory compliance". The draft does both: it runs the rule against five variants on mneme-hq 0.11.0 and states that Mneme does not make a system compliant.

Thesis: a patient data boundary that lives only in an ADR is enforced by reviewer attention; written as a typed rule it fails the agent's edit before the write and the pull request before the merge, and names the decision, but an exact-text rule misses dynamic and transitive imports and cannot see runtime data, so it needs an import graph tool and runtime controls beside it.

Audience: CTOs, VPs of Engineering, platform and architecture leads in digital health and healthcare SaaS.

## Key facts, figures, sources

| Claim | Source URL | Verified? |
|---|---|---|
| 164.312(a)(1): access "only to those persons or software programs that have been granted access rights as specified in § 164.308(a)(4)" | https://www.law.cornell.edu/cfr/text/45/164.312 | Verified, 45 CFR 164.312(a)(1), verbatim (eCFR blocks automated fetches; LII mirror of the CFR text) |
| 164.312(b) audit controls: "record and examine activity in information systems that contain or use electronic protected health information" (paraphrased in body) | https://www.law.cornell.edu/cfr/text/45/164.312 | Verified, 45 CFR 164.312(b) (LII mirror; eCFR unreachable to automated clients) |
| 164.308(a)(4) information access management (context only, not quoted in body) | https://www.law.cornell.edu/cfr/text/45/164.308 | Verified |
| OCR Guidance on Risk Analysis: "must identify where the e-PHI is stored, received, maintained or transmitted" | https://www.hhs.gov/hipaa/for-professionals/security/guidance/guidance-risk-analysis/index.html (linked in body, per audit A3) | Verified, "Data Collection" element, via Wayback snapshot 2026-01-06 (https://web.archive.org/web/20260106161908/https://www.hhs.gov/hipaa/for-professionals/security/guidance/guidance-risk-analysis/index.html; page last reviewed 2025-09-26). hhs.gov returns 403 to automated fetches. |
| NPRM published 2025-01-06, 90 FR 898; proposes written technology asset inventory and network map; preamble: how ePHI moves through systems | https://www.govinfo.gov/content/pkg/FR-2025-01-06/html/2024-30983.htm | Verified, pages 898-1022; network map text in the 164.308(a)(1) section-by-section discussion |
| Final action projected July 2027 (RIN 0945-AA22, Long-Term Actions) | https://www.reginfo.gov/public/do/eAgendaViewRule?pubId=202510&RIN=0945-AA22 | Verified, timetable "Final Action 07/00/2027". Corroborated by Holland & Knight, 2026-07-06 (not cited in body). |
| Veracode Spring 2026 update: passes syntax checks >95% (audit A2 wording); ~55% of generation tasks secure; 80 tasks, 4 CWEs | https://www.veracode.com/blog/spring-2026-genai-code-security | Verified, blog dated 2026-03-24. Body states Veracode measures weakness classes, not architecture. |
| Perry, Srivastava, Kumar, Boneh, CCS 2023: AI-assisted participants wrote significantly less secure code and were more likely to believe it secure | https://arxiv.org/abs/2211.03622 | Verified, abstract; CCS '23 pp. 2785-2799 |
| CWE-532 "Insertion of Sensitive Information into Log File" | https://cwe.mitre.org/data/definitions/532.html | Verified, name verbatim |
| Import Linter forbidden contract: "Indirect imports will also be checked." | https://import-linter.readthedocs.io/en/stable/contract_types/forbidden/ | Verified, verbatim |
| ADR-021 example: preview, import, check FAIL exit 2 on direct import; PASS on approved import; PASS under `clinical/` (PATH EXCLUDED); FAIL on alias import and on `from clinical import repositories`; PASS on `importlib` dynamic import and on an import of a `reporting` module; hook exit 2 on a Write event; audit counts it Protected | local run, mneme-hq 0.11.0 (`scripts/core_version.json` minimum), clean venv at `C:\dev\live-e2e-01-evidence\preflight\venv-host` | Verified 2026-11-26. Inputs and ADR in `hc-a03/verify/`. Note: `scope: analytics.patient-data` was rejected (segments must match `[a-z0-9_]+`); the article uses `analytics.patient_data`. |
| Cut: Veracode CWE-117 log injection figure | | Cut deliberately: log injection is not sensitive data in logs; citing it would misattribute. |
| Cut: HHS NPRM fact sheet (hhs.gov 403) | | Not used; the govinfo full text covers it. |

## Mneme claims and maturity

| Claim (as written in body) | Class |
|---|---|
| ADR with `## Constraints` imports to a decision with FORBID_LITERAL rules scoped by `include_paths` | SHIPPED (0.11.0, reproduced; `/docs/how-to/adr-to-enforceable-decision/`) |
| `mneme check` fails with exit 2 and names the decision; same text outside the path passes | SHIPPED (reproduced) |
| Exact-text rule misses dynamic imports and indirect paths; cannot see runtime values | SHIPPED limitation (reproduced; docs Limits) |
| Claude Code plugin hook checks Edit/Write/MultiEdit before the file changes and exits 2 to block; shell writes mostly checked at end of turn; fails open on crash/timeout | SHIPPED (reproduced hook exit 2; limits per `/docs/how-to/stop-agent-crossing-architectural-boundary/`) |
| CI required check runs the rule on added/modified files; JSON verdict records decision, rule, matched text, selector, decision version identifier | SHIPPED (`/docs/how-to/fail-pull-request-that-breaks-adr/`; fields seen in recorded JSON) |
| Decision without a typed rule is guidance only, blocks nothing | SHIPPED |
| Architecture Protection Audit shows which recorded decisions a typed rule protects today and which are guidance only | SHIPPED (reproduced `mneme audit`) |
| Decision file does not record who approved a decision | SHIPPED limitation (confirmed on 0.11.0 by the claim audit) |
| Mneme does not make a system HIPAA compliant, does not isolate data at runtime, trace data flows or inspect database permissions | Negative statement, accurate |
| JSON verdicts record what each PR was checked against; whether they help meet 164.312(b) is for the compliance team | CONCEPTUAL usage suggestion, hedged; no compliance claim |
| A failing verdict names the decision in its violations; a passing verdict lists none but still names each decision and rule checked (applicability) | SHIPPED (reproduced `check --json` by audit 2) |

No PLANNED features are described. "Decision Engineering" not used. No legal-advice framing; one explicit "None of this is legal advice" line.

## Positioning constraints

- Never imply Mneme ensures HIPAA compliance or runtime isolation (FAQ answers "No").
- The healthcare scenario is labelled hypothetical and names no organization.
- Non-site follow-ups are tracked privately.

## Open questions

- Topic hub: `architectural-governance` assumed; if a `healthcare-regulated-software` hub is created for the series, move it.
- Claim audit round 1: FAIL (F1 Veracode inference, F2 Perry framed as "human review"); both applied verbatim in revision 2, plus advisories A1 ("Every Mneme step shown above runs on the released version, mneme-hq 0.11.0"), A2 (syntax-check wording), A3 (canonical hhs.gov link; LII kept for the CFR) and A4 (life-sciences reciprocal now "checked at the agent's edit and again before the merge"). Re-audit by a fresh agent still required.
- **Revision log.** Rev 1: initial draft (slop 41, lint 0 errors). Rev 2: audit-1 F1-F2, A1-A4 and cold-read fixes (slop 40, lint 0 errors). Rev 3: audit-2 FAIL; applied F3 verbatim ("A passing file's verdict lists no violations, but it still names each decision and rule that was checked against the file."), F4 verbatim (FORBID_NUMERIC_ABOVE removed from the page: on 0.11.0 it is Python-only, whole-file `mneme check --source-file`, not covered by hooks or CI), and A5 ("The hook does not undo the write, so the file exists until the agent fixes it."). A6 needs no change once F4 is applied. Brief claim rows corrected; the two-typed-rules row removed. Two paragraphs split to clear a long-paragraph lint warning (the shell-write paragraph and the CI evidence paragraph). Rev 3: 2236 words, Flesch 59, slop 40/50, lint 0 errors and 1 justified warning (PHI). Re-audit by a fresh agent required again.
- HC-A01 should link here for the scenario rather than repeat the ADR and variant table.

# HC-A04: Architectural Fitness Functions for Medical Device Software

Series: healthcare content pillar from the "Post-Assess Healthcare AI Report" scope chat (2026-11-26, 21 turns, read from the full-text transcript). Article HC-A04, technical intent, priority P1 in the chat's series table. Publish on 2026-12-03.

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | Architectural Fitness Functions for Medical Device Software |
| Slug | `architectural-fitness-functions-medical-device-software` |
| Report-anchored (ADR-015) | no. The FDA guidance supports the argument but is not the article's primary object, so the title stays concept-first. |
| Topic hub | `architectural-drift-prevention` (fitness functions keep code matching documented structure). Alternative: `architectural-governance`, where the two regulated-industry insights sit. The orchestrator should pick one hub for the whole series; there is no healthcare hub yet. |
| Content type (`--type`) | Guide (primary object: a task, deriving fitness functions from submission documents) |
| OG headline | "Fitness functions for medical device software" (6 words) |
| Editorial gate | pass: distinct query ("medical device architectural fitness functions", the chat's keyword list, technical intent) and cornerstone support (links up to the regulated-industries pillar and the life sciences article). Five questions answered below. |
| Five questions | What changed: AI coding agents now make design-level edits in device codebases. Why it matters: FDA premarket guidance (June 2023) expects a documented architecture and a prospective SDS with minimal ad hoc design decisions. What breaks: an agent's working shortcut crosses a documented module boundary and the diagram goes stale. What teams should do: derive fitness functions from the diagram and SDS, name the decision behind each, run them at write time and in CI, protect the check files. How governance helps: ties checks to decision records and checks agent edits before they land (Mneme, narrow exact-text rules). |
| Cannibalisation | `find_overlap.py "Architectural Fitness Functions for Medical Device Software" --keywords "architectural fitness functions,medical device software,fitness function,IEC 62304,FDA software documentation"`: top hits 21.0 `/architecture/decision-memory-vs-documentation/`, 19.0 `/insights/ai-assisted-software-migrations-architectural-drift/`, 19.0 `/concepts/autonomous-software-engineering-governance/`, 18.3 `/insights/software-factory-governance-layer/`, 17.6 `/insights/ey-beyond-the-code-ai-software-development/`. None at 40 or above. Body grep: `git grep -i "fitness function" -- site` hits `/concepts/architecture-as-code/` (defines fitness functions, detect vs prevent; linked, not repeated) and passing mentions in three insights (dora-metrics, goal-driven-agents, productivity-paradox). `git grep -i -E "62304\|IMDRF\|SaMD\|premarket submissions"`: no hits on the site. **Verdict: clear.** Batch overlap: HC-A08 owns IEC 62304 lifecycle detail (this piece names 62304 in one sentence only); HC-A03 owns patient-data boundaries (the example here is a device module boundary, not PHI); HC-A01 owns the market framing. |
| Cross-links | Out: `/insights/ai-governance-for-regulated-industries/`, `/insights/ai-coding-agents-life-sciences-governance/`, `/concepts/architecture-as-code/` (twice), `/concepts/deterministic-enforcement/`, `/concepts/architectural-drift/`, `/audit/`, `/setup/ci/`. Reciprocal hosts in `meta.json`: the two regulated insights plus `why-context-alone-doesnt-prevent-architectural-drift`. |

## Draft quality gate

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | **37/50** after revision 1 (was 39): directness 8, rhythm 8, trust 7, authenticity 7, density 7. The cold-read definitions add explanatory sentences, which cost a little trust and density. First pass removed a "not X, but Y" contrast, adverbs, a quotable closer and "In practice"; revision 1 removed "the rest of this article" meta-commentary. |
| `lint_prose.py body.html` | errors: 0; warnings: 0 after revision 1 (2134 words, avg 16.4 words/sentence, 5% over 30, Flesch 55). Revision 1 first flagged meta-commentary and two paragraphs over 120 words; fixed by rewording and splitting. |
| Cold read: thesis as restated | "Medical device teams already document their architecture for the FDA, and AI coding agents can quietly make the code diverge from it, so teams should turn the rules in that documentation into automated checks (fitness functions) that run before and after agent edits, and tie each check to a recorded decision." Matches the intended thesis. |
| Cold read: unclear terms, and how resolved | All resolved in revision 1. Fitness function now defined in an opening paragraph before first use. Defined at first use: premarket submission, device software function, software verification, traceability analysis, Basic and Enhanced Documentation (contents of both), cleared or approved device, import linter, ArchUnit slices, pre-write hook, fails open, active rule, owner review (CODEOWNERS approval), submission documents (listed), Architecture Protection Audit (CTA copy). "Pillar" replaced with "overview"; "validated system" replaced with "the design a team verified". "## Constraints heading" replaced with a plain description of the ADR's Constraints section. Mneme introduced in one plain sentence before first use. Reread fixes: SDS and verification split into two paragraphs; "it" antecedent fixed (F6); IEC 62304 sentence split into three; data-flow check now says the developer must change the check, which prompts the diagram update in the same review; coverage limits moved out of the hook paragraph into their own paragraph; alias-import example now names both forms; scope-to-practice transition rewritten. Duplicate in-body architecture-as-code link removed (it stays in the related panel). Agents not glossed (Claude Agent SDK, Antigravity) are product names in a list. |

Intended thesis for the cold read to match: a medical device team's submission documents already state its architecture, so it can turn those statements into fitness functions that keep AI-written code matching them, tie each check to a named decision and run it before and after the agent writes, without treating passing checks as compliance.

## Agreed scope

From the chat's series table: HC-A04 "Architectural Fitness Functions for Medical Device Software", technical, P1. Use case table in the same chat: "Medical device architecture: enforce separation between safety-critical and non-critical modules", with the note that several such controls "could be expressed through architectural fitness functions, agent guidance and independent CI verification". Constraint from the chat: do not claim regulatory compliance because Mneme enforces some technical controls; distinguish supporting technical controls from demonstrating compliance. The chat's research arm C ("ADRs and conventional fitness functions in CI") frames fitness functions as the baseline Mneme adds to, not replaces. That framing holds in the draft.

Structure: the documented architecture (FDA guidance) → how agents strain it → fitness functions in brief (link to the concept page) → four fitness functions derived from submission documents → what they do not do → where Mneme fits → what to do this quarter → FAQ.

## Key facts, figures, sources

All FDA page numbers are the printed page numbers of the final guidance PDF (fda.gov/media/153781/download, extracted with pdftotext; printed page = PDF page minus 4).

| Claim | Source URL | Verified? |
|---|---|---|
| Title "Content of Premarket Submissions for Device Software Functions", final, June 2023, docket FDA-2021-D-0775, replaces the 2005 guidance | https://www.fda.gov/regulatory-information/search-fda-guidance-documents/content-premarket-submissions-device-software-functions | verified (landing page) |
| Architecture diagram purpose: modules and layers; relationships; data inputs/outputs and flows; how users and external products (IT infrastructure, peripherals) interact | https://www.fda.gov/media/153781/download | verified, Section VI.E "System and Software Architecture Diagram", p. 20 |
| For a modification to a cleared or approved device, the diagram should identify and reference the modules affected | same | verified, p. 21 (Reference Considerations) |
| SDS should be sufficient that the work was clear and unambiguous "with minimal ad hoc design decisions"; created prospectively, not "documented retrospectively" | same | verified, Section VI, "Software Design Specification (SDS)", p. 22; repeated for Enhanced level, p. 23 |
| Software verification includes technical evaluations (e.g., software architecture) and traceability analyses, including source code to SDS | same | verified, Section IV Definitions, p. 7 |
| Enhanced Documentation where a failure or flaw could present a hazardous situation with a probable risk of death or serious injury; Basic otherwise | same | verified, Section V, p. 8 |
| Enhanced: full SDS in the submission; Basic: SDS not recommended in the submission, kept in the DHF | same | verified, p. 23 |
| Enhanced: all unit and integration test protocols and reports provided | same | verified, p. 26 |
| Guidance does not recommend any software life cycle model or development methodology | same | verified, Section III Scope, p. 6 |
| OTS software definition: generally available component, manufacturer cannot claim complete life cycle control (e.g., operating system, printer/display libraries) | same | verified, Section IV, p. 7 |
| Software version history: versions tested and a brief description of changes relative to the previous tested version | same | verified, Section VI, "Software Version History", p. 26 |
| Sponsors may provide a Declaration of Conformity to clauses of the FDA-recognized ANSI/AAMI/IEC 62304 | same | verified, p. 23 |
| Fitness function: term borrowed from evolutionary computing; Ford, Parsons, Kua applied it to architecture in Building Evolutionary Architectures (O'Reilly, 2017); the book describes one as providing an objective integrity assessment of architectural characteristic(s); a second edition added Sadalage | O'Reilly ch. 2 listing (https://www.oreilly.com/library/view/building-evolutionary-architectures/9781492097532/ch02.html), Thoughtworks Radar (https://www.thoughtworks.com/radar/techniques/architectural-fitness-function), InfoQ quoting the book (https://www.infoq.com/articles/fitness-functions-architecture/) | verified at secondary level: the O'Reilly chapter page returns 403 and the Thoughtworks free-chapter PDF returned 502, so the book text was not read directly. The search snippet of the O'Reilly ch. 2 page, the Radar entry and the InfoQ quotation agree on the wording. Draft paraphrases and quotes nothing. 2017 first edition verified (Open Library, ISBN 9781491986363, per audit); second-edition year cut, sources disagree (2022 vs 2023). Chapter number cut (unverified). "Pass or fail" wording cut (not in any source). "Introduced the term" replaced: the Radar says the term is borrowed from evolutionary computing. |
| Fitness functions may include tests, metrics, monitors | Thoughtworks Radar (above) | verified |
| ArchUnit: Java library, runs in any plain Java unit test framework, checks dependencies between packages and classes, layers and slices, cyclic dependencies | https://www.archunit.org/ | verified (home page) |
| IMDRF SaMD definition | https://www.fda.gov/medical-devices/digital-health-center-excellence/software-medical-device-samd | verified via the FDA page; the IMDRF document itself timed out twice. **Not used in the body**, so no exposure. |

Cut or not used: IEC 62304 clause content (standard is paywalled; HC-A08 territory); 21 CFR 820 references in the 2023 guidance (QMSR amendments since; avoided); Menlo Ventures figures (HC-A01).

## Mneme claims and maturity

Checked against `site/docs/how-enforcement-works/`, `site/docs/how-to/adr-to-enforceable-decision/`, `site/docs/governance-violations/`, `site/setup/claude-code/`, `site/setup/ci/`.

| Claim (as worded in the draft) | Class |
|---|---|
| Mneme is open source and checks changes against architecture decisions written as machine-checkable rules (R1) | SHIPPED |
| ADR (accepted, then imported: R2) Constraints section can carry a `FORBID_LITERAL` rule ("one kind of rule"; 0.11.0 also ships FORBID_NUMERIC_ABOVE, which is Python-only and decided only by `mneme check --source-file`, not by hooks or CI; the article does not mention it): exact, case-sensitive text in the files the rule covers; optional path selectors (F1) | SHIPPED (how-to, ADR to enforceable decision) |
| Each violation it reports names the decision, the rule and the triggering text (F2; FAQ 4 F5). The draft says nothing about PASS verdicts; a passing file's JSON verdict also names each decision checked. | SHIPPED (setup/ci verdict file) |
| Pre-write hooks for Claude Code, Claude Agent SDK, Codex CLI, the Kiro CLI 3.0 engine, Google Antigravity (F3) | SHIPPED (how-enforcement-works; integrations index) |
| Claude Code hook refuses Edit/Write/MultiEdit and one shell form, a single `cat` heredoc write with a quoted delimiter (R3), before the file changes; other shell writes checked at end of turn, after the file exists (F4) | SHIPPED (setup/claude-code) |
| Hook fails open by default | SHIPPED (setup/claude-code) |
| CI job checks every text file a PR adds or modifies; deleted, binary files and pushes that skip PRs not covered | SHIPPED (setup/ci) |
| Exact-text rule misses an alias import form; add one rule per form or keep an import linter | SHIPPED limitation (how-to troubleshooting) |
| Layering in general, cycles, coupling, dependency manifests are not Mneme checks | limitation statement; structural analysis is roadmap per governance-violations (PLANNED, not claimed) |
| Mneme does not produce submission documents, assess OTS software or establish conformity | negative claim, consistent with the chat's constraint |

No CONCEPTUAL or PLANNED capability is presented as available. No claim that Mneme has been used on a medical device codebase.

## Positioning constraints

No compliance or certification claim. No legal or regulatory advice framing; the body says so in the first section. "Decision Engineering" not used. Domain is mnemehq.com. The illustrative device (handheld diagnostic reader) is fictional and labelled as such.

## Open questions

1. Topic hub for the series (drift prevention vs governance).
2. Resolved: book years (F8).
3. Resolved: duplicate architecture-as-code link removed.
4. Fitness function 4 (modified modules vs change record) is a team practice inferred from the guidance's p. 21 recommendation, not an FDA requirement; the draft words it as "can".
5. Closed by re-audit N3: p. 5 (premarket submission), p. 6 (device software function), p. 7 (verification), pp. 23/25-26 (Basic contents) verified; ArchUnit slices verified against the user guide; ADR import activation fixed by R2 (ADR must be accepted). Original note, revision 1: definitional sentences for premarket submission ("before many medical devices can be sold in the US, the maker files..."), device software function (p. 6 definition), software verification (p. 7), Basic level contents (p. 23 SDS kept in DHF; p. 25 testing summary plus system-level protocol), cleared or approved device (plain gloss), ArchUnit slices ("groups of classes selected by package name", from general knowledge of the ArchUnit user guide, not re-fetched), ADR import making the rule active (as in the published Claude Ship article).

## Revision log

- Revision 2 (2026-11-26): applied re-audit R1 (Mneme intro: decisions written as machine-checkable rules), R2 (ADR must be accepted before import activates the rule), R3 (the one shell form is a single `cat` heredoc with a quoted delimiter), R4 ("technical evaluations", the guidance's wording); took the optional N1 wording for premarket submission ("for example before deciding"); N2 note added to the claims table; open question 5 closed per N3. lint_prose 0 errors, 0 warnings; stop-slop 37/50 unchanged. Needs a fresh re-audit.
- Revision 1 (2026-11-26): applied audit F1-F9 verbatim (F5 and F9 in body and faq.json); cold-read fixes listed in the quality gate; lede now glosses fitness functions; read_time 10 min. Needs a fresh re-audit.

## HC-A07: Governing FHIR Integrations in AI-Assisted Development

Status: **drafted, not built** (2026-11-26; cold read FIX and claim audit FAIL (B1-B3) applied in revision 1; awaiting re-audit)

Source: chat `Post-Assess Healthcare AI Report`, scope turn "We should create one use case for healthcare and as content pillar. Scope" (series table row HC-A07, technical intent, P2; FHIR listed under "Standards and regulatory authority" as "Interoperability and interface constraints"; scenario table HC-ADR-004 "FHIR integrations must preserve approved contracts", marked "Future validation"). Only the content-series scope is used; other follow-ups from the chat are tracked privately and not recorded here.

### Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | Governing FHIR Integrations in AI-Assisted Development |
| Slug | `governing-fhir-integrations-ai-assisted-development` |
| Report-anchored (ADR-015) | no. FHIR is a named standard but the article is a task guide, not a response to one artifact; "FHIR" still leads the second word of the title. |
| Topic hub | architectural-governance |
| Content type (`--type`) | Guide (primary object: a task, governing FHIR integration code an agent writes) |
| OG headline | Governing FHIR integrations written by agents (6 words) |
| Publish on | 2026-12-04 |
| Editorial gate | pass: distinct query ("FHIR architecture governance", "FHIR AI coding agents"; no site page mentions FHIR, HL7, US Core or SMART, checked with `git grep -i -w`) and cornerstone support (links to `ai-governance-for-regulated-industries`, `ai-coding-agents-life-sciences-governance`, `/docs/governance-violations/`, `/setup/ci/`) |
| Five questions | Changed: certification names exact FHIR, US Core, SMART and Bulk Data versions while newer ones (R5, US Core 9.0.0, SMART 2.2.0) exist, so every integration embodies version choices. Matters: those choices are architecture decisions binding code to servers the team does not control. Breaks: an agent mixes R5 into R4, widens scopes to wildcards, claims a profile in `meta.profile` without meeting it, bypasses the client module or starts `$export` from the wrong place (hypothetical, labelled). Do: write six ADRs; map each to the check that can catch it (text rule, FHIR Validator, CapabilityStatement test, Must Support fixtures); protect check files. Governance: Mneme enforces the four prohibition-shaped decisions as path-scoped exact-text rules in the agent hook and CI; it does not validate FHIR. |
| Cannibalisation | `find_overlap.py "Governing FHIR Integrations in AI-Assisted Development" --keywords "fhir,hl7 fhir,smart on fhir,us core,fhir api governance,healthcare interoperability,ai coding agents"`: 94.2 `/insights/smart-routing-ai-coding-agents/` (false match on the word "smart"; model routing, unrelated); 68.5 `/open-source-ai-coding-agent-governance/`; 63.3 `/supported-languages/`; 61.1 `/supported-languages/javascript-governance/`; 59.8 `/use-cases/`; 58.5 `/insights/ai-coding-agents-life-sciences-governance/`. Each matches only generic "AI coding agent governance" terms; none covers FHIR. Body grep `git grep -n -i -w -E "fhir|hl7|uscdi|us core|information blocking" -- 'site/*.html'`: no hits. **Verdict: clear.** Batch: distinct from HC-A03 (PHI/data-domain boundaries; this article does not discuss patient data isolation), HC-A04 (fitness functions; this article names the FHIR Validator and tests but does not develop fitness-function framing), HC-A08 (IEC 62304; not mentioned), HC-A01 (market framing; not repeated). |
| Cross-links | Out: `ai-governance-for-regulated-industries`, `ai-coding-agents-life-sciences-governance`, `/docs/governance-violations/`, `/setup/ci/`. Reciprocal in: the same two insights (see meta.json). Once HC-A01/A03/A04 are live, consider linking HC-A03 from the "One client module" decision and HC-A04 from the checks table (not done: unpublished on draft date). |

### Draft quality gate

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 36/50 after revision 2 (unchanged by the B4-B7 wording fixes); 36/50 after revision 1 (directness 8, rhythm 7, trust 7, authenticity 7, density 7; was 37). The added definitions cost a point of trust (more explanation), and no new slop phrases were introduced. First pass cut "The limits matter here more than in most domains", "worth having", a "wrong as FHIR / wrong for this system" contrast pair, "usually writes", "many teams". |
| `lint_prose.py body.html` | errors: 0; warnings: 2, justified. After revision 1: 1,955 words, 132 sentences, avg 14.8 words/sentence, 7% over 30, Flesch 65 (was 1,592 words, Flesch 64). Revision 1 also expanded ANSI and split two paragraphs over 120 words. Remaining: `SMART` and `HAPI` "not expanded": both are proper names of a specification (SMART App Launch) and a library (HAPI FHIR), introduced by full name at first use; the expansion of SMART was not verified against a primary source, so it is not added. Fixed earlier: long paragraph (split), CFR expanded, SHALL quote paraphrased. |
| Cold read: thesis as restated | "FHIR integrations depend on external version and scope choices that AI coding agents cannot know, so teams should record those choices as architecture decisions and enforce the text-checkable ones with rules (Mneme) plus the FHIR Validator and tests for the rest." Matches the brief's thesis. |
| Cold read: unclear terms, and how resolved | FIX applied in revision 1. Mneme introduced in one sentence at the end of the first section (open-source tool that checks code changes against recorded architecture decisions). Now defined at first use: SMART scopes (permission strings an app requests), US Core (minimum constraints on FHIR resources for US use), Trial Use and normative (locked versus still changeable), Must Support (server can send, client can process; missing means no data), CapabilityStatement (what a server can do for a FHIR version), text rule (a check that fails a change containing exact text, optionally in certain paths), hook (a script Claude Code runs around the agent's actions; Edit, Write, MultiEdit glossed as file tools), fails open (with the two example causes from /setup/claude-code/), required check (a GitHub branch rule says the job must pass), code-owner review (CODEOWNERS file plus required owner review in a branch rule). The roadmap rule type is named: required-presence rule. Architecture Audit described and linked in the body before the CTA. Reread sentences rewritten: the newest-versions paragraph (split into short statements), the fragment (now a full sentence), "first four rows" (rows named; scope row marked as wildcard half only), the certification paragraph, the shell-write sentence (split by tool type), the same-verdict sentence. Wildcard rule strings explained: each stops at the dot so one rule matches every suffix, with three complete examples. Already defined before: FHIR, HL7, ONC, CFR, ADR, CI, profile, `meta.profile`, FHIR Validator. |

### Agreed scope

Thesis: a FHIR integration's contract lives in external specifications whose versions a team has chosen; an AI coding agent knows all versions and none of those choices, so the team records each choice as a decision and matches it to the check that can catch it. Mneme covers the prohibition-shaped decisions only. Audience: engineering leaders and platform owners at health IT vendors building FHIR integrations with AI coding agents. Structure: the contract lives outside your repository; four hypothetical agent failures; six ADRs; decision-to-check table; where Mneme fits (with limits and a no-compliance-claim paragraph); five-step checklist; FAQ (4). Not legal advice: one paragraph says certification applies to certified products and is assessed by the program, and that a text rule demonstrates no regulatory conformance.

### Key facts, figures, sources

All checked 2026-11-26 with WebFetch against the live pages.

| Claim | Source URL | Verified? |
|---|---|---|
| (g)(10) adopted standards: FHIR Release 4.0.1 (§170.215(a)(1)); US Core STU 6.1.0 (§170.215(b)(1)(ii)), SVAP-approved STU 7.0.0 and STU 8.0.1; SMART App Launch 2.0.0 (§170.215(c)(2)), SVAP 2.2.0; Bulk Data v1.0.0 (§170.215(d)(1)), SVAP v2.0.0. Companion guide is "not a substitute for the requirements outlined in regulation." | https://www.healthit.gov/test-method/standardized-api-patient-and-population-services | verified (Certification Companion Guide, regulation text and "Standards & References"; first 100k chars read) |
| ONC expanded as "Office of the National Coordinator for Health Information Technology" | https://hl7.org/fhir/us/core/ | verified (US Core home page text on ONC certification testing) |
| US Core current published version 9.0.0, "based on FHIR Version R4" | https://hl7.org/fhir/us/core/ | verified (home page: "This is the current published version") |
| R5: backward compatibility "is not guaranteed by FHIR"; R5 "has NOT been submitted to ANSI" as normative (article now keeps "to ANSI", per audit B3); Normative content is "locked" under the inter-version compatibility rules; for Draft/Trial Use content "there are no rules for maintaining any sort of compatibility between versions" | https://hl7.org/fhir/R5/versions.html | verified (§2.1.7.0.1, §2.1.7.0.5) |
| HAPI FHIR modules `hapi-fhir-structures-r4` / `-r5`: "FHIR R4/R5 model classes" | https://hapifhir.io/hapi-fhir/docs/getting_started/modules.html | verified (modules table) |
| SMART v2 suffixes `.cruds`; `patient/Observation.rs` = read and search observations; wildcard = "all data for all available FHIR resources, both now and in the future"; "avoid the use of wildcard scopes purely for the sake of convenience"; v1 `.read` ⇒ v2 `.rs`; search modifiers, chaining and `_filter` "should be considered experimental" (plain `?category=` constraints are not); "seeking community consensus on a small common core of search parameters" | https://hl7.org/fhir/smart-app-launch/scopes-and-launch-context.html | verified (2.2.0, "Scopes for requesting FHIR Resources") |
| SMART 2.0.0 defines `.cruds`, `patient/Observation.rs`, and `patient/Observation.rs?category=http://terminology.hl7.org/CodeSystem/observation-category|laboratory` | https://hl7.org/fhir/smart-app-launch/STU2/scopes-and-launch-context.html | verified (2.0.0 STU page) |
| `meta.profile`: profiles the resource "claims to conform to"; a resource "may falsely claim to conform to a profile"; conformance determined "by testing it against the profile" | https://hl7.org/fhir/R4/resource.html | verified (§2.26.3.7, §2.26.3.8.2) |
| FHIR Validator is a Java jar provided with the spec; validation aspects include structure, cardinality, bindings, invariants, profiles; validator "is only as good as the underlying definitions" | https://hl7.org/fhir/R4/validation.html | verified (§7.5, §7.5.4) |
| CapabilityStatement "documents a set of capabilities (behaviors) of a FHIR Server for a particular version of FHIR"; `fhirVersion` required | https://hl7.org/fhir/R4/capabilitystatement.html | verified (§5.2, §5.2.3) |
| Must Support: responders SHALL be capable of populating (CONF-0075), requestors SHALL be capable of processing (CONF-0076) and SHALL interpret missing data elements as data not present (CONF-0079) | https://hl7.org/fhir/us/core/must-support.html | verified (US Core 9.0.0, "Must Support Elements"); article paraphrases without quotation marks (audit-2 B7) |
| Bulk Data kick-off `[fhir base]/Group/[id]/$export` (also Patient, system level); async request pattern | https://hl7.org/fhir/uv/bulkdata/STU2/export.html | verified (Bulk Data 2.0.0) |

Cut as unverified or out of scope: information-blocking rules (45 CFR 171) (not needed for an engineering guide; legal-framing risk); ASTP/ONC renaming (not checked against a primary source, so the article uses "ONC" as the US Core page does); the expansion of "SMART"; any claim about how often agents make FHIR mistakes (no data; the four cases are labelled hypothetical); HTI-1 sub-resource scope requirements for certified servers (verified on the companion guide but left out to keep the article on client-side integration code).

### Mneme claims and maturity

Checked against `/docs/governance-violations/`, `/docs/how-enforcement-works/`, `/setup/ci/` and `/setup/claude-code/` (both "Tested with mneme-hq 0.11.0"; `scripts/core_version.json` minimum 0.11.0), and the wording the `claude-ship-architecture-ai-approved-code` audit passed on 2026-11-23.

| Claim | Class |
|---|---|
| Mneme is an open-source tool that enforces architecture decisions on code changes once each decision is written as a rule | SHIPPED |
| mneme-hq 0.11.0 ships two typed rules (FORBID_LITERAL and FORBID_NUMERIC_ABOVE); the one used here forbids exact, case-sensitive text, optionally limited to paths. The other "sets an upper limit on a number in Python code and does not apply here" | SHIPPED (core repo `docs/releases/v0.11.0.md`: FORBID_NUMERIC_ABOVE declares an inclusive upper bound on a Python module-level symbol and/or a positional argument of direct calls; Python only; checked only by the whole-file audit `mneme check --source-file`, not by CI or the hooks. The article does not use it.) |
| Example rules: `hapi-fhir-structures-r5` in build files; `patient/*.`, `user/*.`, `system/*.` in auth config; `$export` outside the export job's directory; base URL outside the client module | SHIPPED mechanism (FORBID_LITERAL, path-scoped); the rules themselves are illustrative, not tested on a FHIR repository |
| A decision with no rule blocks nothing | SHIPPED |
| Claude Code hook refuses Edit/Write/MultiEdit that breaks an active rule before the file changes, and checks one shell form before it runs (a single `cat > file <<'EOF'` with a quoted delimiter, per `/setup/claude-code/`); any other shell write is checked at end of turn and the agent is sent back | SHIPPED |
| Hook fails open by default; examples: `mneme` missing, or check over 10 seconds | SHIPPED (limitation; /setup/claude-code/ "Fails open by default") |
| Architecture Audit sorts a repository's recorded decisions into those a rule protects today and those that still depend on a reviewer | SHIPPED (`/audit/`, per audit M16) |
| Required check = a GitHub branch rule says the job must pass; code-owner review = CODEOWNERS plus required owner review | GitHub behaviour, not a Mneme claim |
| CI runs `mneme check` on every text file a PR adds or modifies, fails on an active rule; blocks only where required; deleted, binary files and pushes that skip PRs not covered | SHIPPED |
| Same verdict on every change it checks | SHIPPED (deterministic literal matching) |
| Mneme does not read FHIR, cannot validate profiles, judge scope breadth or missing-element handling | SHIPPED (limitation) |
| Required-presence rules (e.g. a profile URL on every resource) are a roadmap rule type | PLANNED (per `/docs/governance-violations/` "Roadmap rule type", card 11 "Needs required-presence rules") |
| Mneme is not a certification or compliance tool | statement of fact |

Not claimed: FORBID_DEPENDENCY (repo-wide WARN, ignores paths; avoided on purpose), Decision Index, MCP, evidence records, tested FHIR or healthcare deployment, the transcript's HC-ADR-004 demo (marked "Future validation" in the chat).

### Positioning constraints

No "Decision Engineering". No regulatory-compliance or certification claim; no legal-advice framing. No PHI/data-domain boundary content (HC-A03 owns it). Do not restate the two linked regulated-industry insights.

### Open questions

- Should the series' later articles (HC-A03, HC-A04) be linked from this one once live? Proposed above.
- Closed: ONC naming. The audit (N1) found the cited healthit.gov pages use only "Office of the National Coordinator for Health Information Technology"; keep as written.

### Revision log

- Revision 1 (2026-11-26): audit B1 (SMART experimental sentence replaced with the auditor's text), B2 ("or token code" removed from table row 3), B3 ("to ANSI" restored); brief sources row corrected; cold-read fixes as listed in the quality gate; coordinator addendum applied (two typed rules in 0.11.0; cat-heredoc form checked before the write). Previous body kept at `../hc-a07-body.v1.html`.
- Coordinator addendum 2 checked: the draft never says a verdict names the decision (the one "same verdict" sentence claims determinism only) and does not mention Kiro. No change needed.
- Revision 2 (2026-11-26): audit-2 B4 (table row 1 back to "Text rule in CI and in the agent's hook"), B5 (numeric rule scoped to Python code), B6 (code-owner review prevents an unapproved merge, not the edit), B7 (Must Support quote removed; paraphrase without quotation marks). Numeric-rule claims row now cites `docs/releases/v0.11.0.md` (Python only; `mneme check --source-file` only; not CI or hooks).

# HC-A08: IEC 62304 and AI Coding Agents: Keeping the Record True (brief section)

Revision 2 (2026-11-26): claim audit FAIL (5 blockers) and cold read applied. See "Revision log" at the end.

Series: healthcare pillar from `Post-Assess Healthcare AI Report` (2026-11-26), scope turn "We should create one use case for healthcare and as content pillar. Scope", row HC-A08 (Regulatory, P2). Publish date 2026-12-05.

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | IEC 62304 and AI Coding Agents: Keeping the Record True (55 chars). Changed from the owner-approved series title "IEC 62304 and AI-Assisted Software Engineering" because the claim audit ruled it a bare-keyword title under ADR-015 (`<entity>: <angle>` required). Owner to confirm before publish. Apply verbatim to `<title>`, `<h1>`, `og:title`/`twitter:title`, JSON-LD `headline`, BreadcrumbList final `name`, index card and the inbound anchors in meta.json. |
| Slug | `iec-62304-ai-assisted-software-engineering` (unchanged: ADR-015 and the insight contract govern the six title fields, not the slug; no rule requires the slug to match the title, and the slug keeps the "IEC 62304 AI software development" query terms) |
| Report-anchored (ADR-015) | yes: entity = "IEC 62304" (named standard); leads title, H1, OG headline and the meta description (with FDA recognition 13-79, verified in body). The earlier variant "... What the Software Record Must Show" (66 chars, not 63 as first recorded) was rejected by the audit: "must" asserts a requirement the nonbinding guidance does not make. |
| Topic hub | architectural-governance (the proposed `healthcare-regulated-software` hub does not exist; re-home if the series hub is built first) |
| Content type (`--type`) | Analysis (a named standard and FDA guidance the article applies) |
| OG headline | IEC 62304 meets AI coding agents (6 words) |
| Editorial gate | pass: distinct query ("IEC 62304 AI software development", listed High fit in the scope) with no existing page; named-source entry point (IEC 62304, FDA premarket software guidance); supports the regulated-industries cornerstone through links |
| Five questions | Changed: AI coding agents now write device code; the FDA-recognized 62304 edition (2015) and the 2023 premarket guidance treat AI only as a device function. Matters: the guidance asks for a tools summary, a prospective design with minimal ad hoc design decisions, an architecture diagram that identifies affected modules, and regression analysis. Breaks: an agent's undocumented design choice (layer bypass) passes tests and makes the diagram and design spec untrue. Do: name agents in the development record, write diagram boundaries as checkable rules, check at write time and as a required CI check, keep verdicts with the change, keep approval with people. Governance: deterministic checks of encoded architecture decisions; explicitly not compliance. |
| Cannibalisation | `find_overlap.py "IEC 62304 and AI-Assisted Software Engineering" --keywords "IEC 62304,medical device software,AI-assisted development,software lifecycle,traceability,FDA premarket software"`: 70.4 `ai-assisted-software-migrations-architectural-drift`; 65.5 `bain-ai-development-lifecycle-governance`; 54.6 `/supported-languages/`; 50.7 `/concepts/autonomous-software-engineering-governance/`; 49.2 `generative-ai-software-engineering-stack`. All matches are generic tokens ("ai assisted", "softwar", "lifecycl"); none mentions IEC 62304, medical devices or FDA. The 70 hit is about migrations: a searcher for IEC 62304 is not served by it. Body grep `git grep -i -E "premarket|predetermined change|PCCP|device software function|IEC 62304|2017/745" -- site`: zero hits. Closest by body: `ai-coding-agents-life-sciences-governance` (FDA computer software assurance, GxP, 21 CFR 820: production and quality system software) and `ai-governance-for-regulated-industries` (cross-vertical requirements). **Verdict: clear.** Both are linked once, not restated: CSA and validation histories stay in the life-sciences piece; the cross-vertical six capabilities stay in the regulated-industries piece. Batch: distinct from HC-A01 (market framing, Menlo), HC-A03 (patient data boundary), HC-A04 (fitness functions), HC-A07 (FHIR). Overlap risk with HC-A04: both may use a "layer bypass" example; this piece uses it only to show the FDA architecture diagram going untrue, not to define fitness functions. Coordinate so HC-A04 does not also walk through the FDA documentation elements. |
| Cross-links | out: `/insights/ai-governance-for-regulated-industries/`, `/insights/ai-coding-agents-life-sciences-governance/`, `/setup/ci/`, `/audit/`. Reciprocal in: the two regulated pieces (see meta.json); optional `bain-ai-development-lifecycle-governance`. Series siblings should be linked once published. |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | Revision 3: 36/50 (unchanged dimensions; the three Mneme sentences are longer but plainer). Revision 2: 36/50 (directness 8, rhythm 7, trust 7, authenticity 7, density 7). The added first-use definitions cost some density; removed one "X matters because" construction introduced in revision. Revision 1: 36/50 (directness 8, rhythm 7, trust 7, authenticity 7, density 7). One revision pass: removed a rhetorical setup ("So the question ... is practical"), two "not X, it is Y" contrasts (PCCP model vs editor agent; "not a regulated AI function"), a quotable closer ("That record is where the agent's effect shows up"), and a "None of this makes..." negative opener. Remaining density cost: the documentation-element list in section 2 is reference-heavy by design. |
| `lint_prose.py` | Revision 3: errors: 0; warnings: 0 (2,079 words, 127 sentences, avg 16.4 words/sentence, 6% over 30, Flesch 54; split the hook paragraph after Fix 3 pushed it to 123 words). Revision 2: errors: 0; warnings: 0 (2,047 words, 126 sentences, avg 16.2 words/sentence, 6% over 30, Flesch 54; fixed an "HQ" acronym and a 124-word paragraph on the way). Revision 1: errors: 0; warnings: 0 (1,748 words, 112 sentences, avg 15.6 words/sentence, 4% over 30, Flesch 52). Fixed on the way: IEC, ANSI, AAMI, ML, "VI" acronyms (ANSI/AAMI dropped; "Section VI (Recommended Documentation)" defined), one 125-word paragraph split. No `voice-ok` markers used. |
| Cold read: thesis as restated | (coldread.md) "The FDA's software documentation expects design and architecture to be decided in advance and described accurately, and AI coding agents that make unrecorded design choices can quietly make that record untrue, so device teams should name agents in the development record and enforce architecture decisions as checkable rules at the agent and in CI." Matches the brief's thesis. |
| Cold read: unclear terms, and how resolved | Revision 2 resolved every listed term at first use: Mneme introduced in one sentence at the end of section 1; recognition number, Edition 1.1 and extent of recognition (section 1); Basic vs Enhanced applicability made explicit (Basic = every other submission with device software); Declaration of Conformity; cleared or approved device; regression analysis now defined before its first use; typed rule, active, hook, Edit/Write/MultiEdit, end of turn ("finishes its reply"), fails open, `mneme check`, workflow artifact, Decision Index (versions added, earlier versions left as they were); CTA now says what the Architecture Audit does. Reread sentences rewritten: VI.G two-route paragraph; "the record shows its effect"; cleared-device transition; circular regression sentence; Decision Index "unchanged"; "Device teams can still...". A fresh cold read of the revised page is still needed. Revision 1 notes: Defined at first use in the draft: IEC, FDA, AI coding agent, premarket submission, AI/ML, PCCP, CI, ADR, architectural drift, Decision Index, Declaration of Conformity (context). Candidates for the cold reader: "DHF" is not used; "Basic/Enhanced documentation level" is explained; "active typed rule" is explained by example. |

## Agreed scope

From the scope turn: HC-A08 is the regulatory-intent article of the healthcare pillar. The pillar is about how engineers build, modify and verify healthcare software with AI, not healthcare AI governance in general. Messaging constraint from the same turn: distinguish "supporting technical controls" from "demonstrating regulatory compliance"; Mneme is not a medical device certification or compliance management platform. The scope also cites the FDA June 2023 device software guidance on architecture documentation and traceability.

Thesis (as drafted): IEC 62304 and the FDA's premarket software guidance regulate a planned, documented process, and treat AI only as a device function. An AI coding agent is a development tool whose small, unplanned design choices can make the architecture diagram, design specification and change records untrue while tests pass. Teams keep the record true by writing the architecture boundaries as checkable rules, checking them at write time and in a required CI check, and keeping the verdicts with the change, while approval and conformity stay in their own process.

Audience: CTOs, VPs of Engineering, software quality leaders at MedTech and digital health companies with device software. Structure: what the standard is (public record only); where it appears in an FDA submission; AI in the guidance means AI in the device (PCCP contrast); four places an agent touches the record; what teams can do (not regulatory advice); where Mneme fits and where it does not; FAQ (3).

## Key facts, figures, sources

All checked 2026-11-26. IEC 62304 text itself was not read (paywalled); no clause content is described, only clause numbers and titles as the FDA guidance quotes them.

| Claim | Source URL | Verified? |
|---|---|---|
| IEC webstore: "Defines the life cycle requirements for medical device software"; common framework of processes, activities, tasks; applies to software that is a device or embedded/integral; excludes validation and final release; consolidated 2006+AMD1:2015 | https://webstore.iec.ch/en/publication/6792 | verified (abstract; product listing "IEC 62304:2006+AMD1:2015 CSV") |
| FDA recognition 13-79: IEC 62304 Edition 1.1 2015-06 Consolidated Version, ANSI AAMI IEC 62304:2006/A1:2016 in same entry; entered 01/14/2019; extent "Complete standard"; consolidated = first edition 2006 + amendment 1 2015; lists the June 2023 premarket guidance as relevant | https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfStandards/detail.cfm?standard__identification_no=38829 | verified (detail page; search `results.cfm?title=62304` shows 13-79 Complete) |
| Guidance title, issued June 14, 2023; supersedes May 2005 guidance; current PDF carries a QMSR note (Part 820 now QMSR, effective Feb 2, 2026) | https://www.fda.gov/media/153781/download | verified (PDF p.1-2) |
| Two documentation levels, Basic and Enhanced; Enhanced where a failure or flaw could present a hazardous situation with a probable risk of death or serious injury | same | verified (Section V, printed p.8) |
| Table 1 documentation elements and section letters (VI.D SRS with traceability; VI.E System and Software Architecture Diagram; VI.F SDS, not recommended in submission at Basic, recommended at Enhanced; VI.G; VI.H; VI.I; VI.J) | same | verified (Table 1, printed pp.10-12; TOC p.iv) |
| VI.G alternative: Declaration of Conformity to FDA-recognized IEC 62304; Basic lists 5.1.1 "Software development plan", 5.1.2, 5.1.3, 5.1.6, 5.1.7, 5.1.8, 5.1.9 "Software configuration management planning", clause 6 "Software maintenance process", clause 8 "Software configuration management process", among others; Enhanced lists 5.1, clause 6, clause 8; DoC to complete standard "not needed" | same | verified (Section VI.G, printed pp.23-25; footnote 54: clause refs based on ANSI/AAMI/IEC 62304:2006 & A1:2016) |
| VI.G Basic summary includes "Software coding standards, methods, and tools used in software development"; tools to link needs, requirements, design, testing, risk controls (traceability); maintenance incl. risk assessment of software changes, regression analysis and testing | same | verified (Section VI.G(1), printed p.24) |
| SDS: work "clear and unambiguous, with minimal ad hoc design decisions"; SDS a prospective activity, not documented retrospectively | same | verified (Section VI.F, printed p.22) |
| Architecture diagram: modules, layers, interfaces, data flow; for modifications, identify and reference affected modules | same | verified (Table 1 printed p.11; Section VI.E printed p.21) |
| Regression analysis = documented evaluation of a change's impact based on documentation incl. source code, to decide whether regression testing is needed | same | verified (Section VI.H, printed p.26) |
| AI/ML mentions in the guidance concern the device function (analysis methodology, model training data; an AI/ML-enabled imaging example); no mention of code-writing tools | same | verified (text search of full PDF: AI/ML at printed p.13 and Appendix example; no "generative", "assistant", "language model") |
| PCCP guidance: final; applies to AI-enabled device software functions; three components (modifications, methodology to develop/validate/implement, impact assessment) | https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial-intelligence | verified (page "August 2025", content current as of 08/18/2025; the auditor confirmed the PDF https://www.fda.gov/media/166704/download says "Document issued on August 18, 2025"; body says "later" and gives no date) |

Cut as unverifiable: EU MDR Annex I Section 17.2 wording (EUR-Lex HTML/PDF did not render the annex via WebFetch; secondary sources only); EN 62304 harmonisation status under MDR (secondary sources conflict); any description of what IEC 62304 clauses require, software safety classes A/B/C, SOUP requirements (not in public primary material read); EU AI Act (not needed); IMDRF (not fetched; not needed). MDR Articles 2(1) and 2(4) were verified (software in the device definition; software deemed an active device) but not used.

## Mneme claims and maturity

Checked against `/docs/how-enforcement-works/`, `/docs/decision-index/`, `/docs/cli/`, `/setup/claude-code/` and `/setup/ci/` (both "Tested with mneme-hq 0.11.0"; `scripts/core_version.json` minimum 0.11.0), `/docs/how-to/fail-pull-request-that-breaks-adr/`.

| Claim | Class |
|---|---|
| Mneme is an open-source tool that enforces a team's architecture decisions on code changes once each is written as a rule | SHIPPED |
| Does not make software conform to IEC 62304, does not produce a Declaration of Conformity, is not a quality management system | statement of scope (negative; true) |
| Compiles ADRs into one file in the repository | SHIPPED |
| Enforces a decision only through an active rule; the article uses FORBID_LITERAL (ban on exact text, optionally path-limited, checked by the hook and CI). FORBID_NUMERIC_ABOVE (0.11.0) is Python-only, always path-limited and checked only by whole-file `mneme check --source-file`, not by the hook or CI, so the article does not mention it. A rule is active once its ADR is accepted (proposed ADRs are inactive; `adr_compiler.py` status filter, v0.11.0) and the rule is switched on (ADR `## Constraints` at import, or `mneme protect activate`); no active rule, no block | SHIPPED (0.11.0) |
| Example boundary (store client import forbidden under interface-layer paths) expressible as such a rule | SHIPPED (FORBID_LITERAL with path selector; hypothetical scenario) |
| Claude Code hook checks Edit/Write/MultiEdit and one shell form only, a single `cat > file <<'EOF'` write with a quoted delimiter, before the write and refuses one that breaks an active rule; other shell writes checked at end of turn, after the write | SHIPPED |
| Hook fails open by default; repository can opt in to refusing | SHIPPED |
| Documented CI job runs `mneme check` on every text file a PR adds or modifies, fails on a broken active rule | SHIPPED (documented workflow in /setup/ci/) |
| Documented CI job fails the PR on a broken active rule and each violation names the decision; the CI guide keeps one JSON verdict per changed file as a workflow artifact (no claim about what a PASS verdict contains) | SHIPPED (documented workflow; retention is the CI platform's, not claimed) |
| FAQ 3: "the documented CI job keeps one verdict per checked file" (was "records a verdict per checked file", which implied a product evidence store) | SHIPPED (documented workflow) |
| Not covered: deleted files, binary files, pushes that skip PRs | SHIPPED (stated limitation) |
| Decision Index keeps each decision version unchanged; for ADR imports records source file and hash; does not record approver | SHIPPED (since 0.10.0) |
| Verdicts (a failure names the decision it broke) are an input to regression analysis / version history, not a replacement | CONCEPTUAL (practice recommendation, no product claim) |
| CTA: Architecture Audit sorts recorded decisions into rule-enforced, could-be-rule, and reviewer-reliant | SHIPPED (site/audit: Protected / Mneme-ready / Requires modelling / Guidance) |

No PLANNED features are mentioned. "Decision Engineering" is not used. No claim that Mneme has been used in a device submission.

## Positioning constraints

Not compliance, not regulatory advice (explicit disclaimer in "What engineering teams can do" and FAQ 3). No category or tagline changes. Terminology lock respected: "drift" (defined), "enforcement"; "decision corpus" not needed. "Decision Index" capitalised and described as the stored record; no approver-identity claim.

## Open questions

1. Title: owner to confirm "IEC 62304 and AI Coding Agents: Keeping the Record True" (audit's ADR-015 fix) over the approved series title.
2. Topic hub: re-home to the healthcare pillar hub if it ships before 2026-12-05.
3. Claim audit must re-verify the FDA clause titles against the PDF (printed pp.24-25) and the 13-79 entry.
4. A regulatory reviewer may want "Section VI.G" Basic vs Enhanced clause lists both shown; the body shows only the Basic list by design.

## Revision log

Revision 2, 2026-11-26, after `audit.md` (VERDICT: FAIL, 5 blockers) and `coldread.md`:

- Blocker 1 (ADR-015 title): title changed to the auditor's "IEC 62304 and AI Coding Agents: Keeping the Record True" in meta.json and all reciprocal link texts. Reason: the series title pairs the entity with a second keyword, not an angle. Owner confirms before publish. Slug kept.
- Blocker 2: the "ad hoc design decision" sentence uses the auditor's wording. The unsourced "dozens in an afternoon" figure is gone, and the sentence before it was reworded to avoid repeating "every task".
- Blocker 3: "Device teams can still use AI coding agents..." replaced verbatim with the auditor's text.
- Blocker 4: the PCCP subject is now "AI-enabled software inside the product".
- Blocker 5: FAQ 3 changed in both body.html and faq.json to "the documented CI job keeps one verdict per checked file".
- Cross-batch facts applied: the CI text says each violation names the decision (it makes no claim that a passing verdict names none; a PASS JSON verdict still lists each decision checked), FORBID_NUMERIC_ABOVE is not enforced by the hook or CI (release notes v0.11.0) and is not mentioned, and the hook's pre-write coverage includes the single cat-heredoc. Kiro is not mentioned.
- Cold read fixes are listed in the draft quality gate.
- Lede: "software design specification" (auditor's non-blocking note).
- read_time is now 9 min, and og_alt was updated.
- A fresh claim audit of the changed text and a fresh cold read are still required (claim-audit skill section 5).

Revision 3, 2026-11-26, after `audit-2.md` (VERDICT: FAIL, 3 blockers; all five round-1 blockers confirmed fixed):

- Fix 1 (M4-M6): the paragraph that called typed rules the only enforcement path, with two kinds, now uses the auditor's text word for word. It describes an active rule and the exact-text ban the article uses, enforced by the hook and in CI, and says how a rule becomes active. FORBID_NUMERIC_ABOVE is no longer mentioned.
- Fix 2 (M8): "A decision without an active rule blocks nothing."
- Fix 3 (M9): the hook is now "a command Claude Code runs before the agent edits a file or runs a shell command, and again when the agent finishes its reply." The hook paragraph was then split in two to stay under 120 words.
- Brief correction: the Mneme-claims "two typed rules" row was replaced with the auditor's row, and the revision 2 "Cross-batch facts" line was reworded.
- Optional tweaks applied: the lede now says "needs to hold". Reciprocal 1 uses the exact title-case title, so all three reciprocals carry the same string.
- Corrected cross-batch note: a passing file's JSON verdict still names each decision checked. The body says only that each violation names the decision and never says a PASS names no decision.
- Still required: a fresh audit of the changed text, a cold read of the revised page, owner confirmation of the title, and a check on the built page that all six title fields match.


Revision 4 (after audit-3): blockers 1-2 and both brief rows applied by the orchestrator with audit-3 text.
