# Scope brief: Post-Assess OpenAI Modernization Announcement

Status: **queued** for the scheduled publisher: A on 2026-10-26 (#242), B on 10-27 (#243), C on 10-29 (#249); D and E evidence-gated

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Assess OpenAI Modernization Announcement` |
| Created / last updated (UTC) | 2026-10-20 / 2026-10-20 |
| Shape | 3 user turns: assess OpenAI's 2026-10-19 post on X, add to the roadmap, scope a content expansion. The last turn is the scope (4 articles first, then 2 gated pieces, plus one use-case page edit). Read in full 2026-10-20; no collapsed turns. |
| Repo check | No page mentions COBOL, MultiLangBench, AWS Transform or behavioral equivalence testing. The software-migrations-modernization hub has a cornerstone and supporting pieces (all 2026-08-28/29): `ai-assisted-software-migrations-architectural-drift`, `adrs-for-software-migrations`, `why-ai-coding-agents-copy-legacy-architecture`, `strangler-fig-migrations-architectural-drift`, `codebase-memory-during-migrations`, `migration-guardrails-for-ai-coding-agents`, `architectural-drift-cloud-platform-migrations`, plus `use-cases/ai-assisted-software-migrations`. `reverse-engineering-architectural-decisions-research` (2026-10-14) covers decision recovery. |

The existing cluster is about **governing change during a migration** (agents copying legacy patterns, transitional ADRs, strangler boundaries). This brief adds a second track: **deciding what must survive** before and during modernization (observed behavior vs inferred decision vs approved decision). Both stay on one hub; no second migration hub.

## Build cards

### A. OpenAI announcement analysis (phase 1, publish first)

| Field | Value |
|---|---|
| Kind | insight |
| Title | OpenAI's COBOL Migration Benchmark: What Behavioral Parity Does Not Measure (lead with OpenAI's verbatim announcement name if it has one; the chat's working title is "Advancing Coding in Low-Resource Programming Languages: What COBOL Migration Benchmarks Don't Measure") |
| Slug | `openai-cobol-migration-benchmark-behavioral-parity` |
| Report-anchored (ADR-015) | yes: entity = OpenAI's announcement / post title, verbatim, confirmed at verification |
| Topic hub | software-migrations-modernization |
| Content type (`--type`) | Analysis (a named launch with vendor benchmarks; not Research, since the benchmarks are the vendor's own) |
| OG headline | Passing the Tests Is Not Approval (6 words) |
| Editorial gate | pass: named-source entry point (OpenAI) plus new evidence for the migration thesis |
| Five questions | changed: OpenAI reports 97.9% on a COBOL migration evaluation that requires exact output parity; matters: AI is making legacy rewrites economically feasible; breaks: a migration can match every tested output and still break an approved boundary or residency rule, or faithfully preserve a bug; do: separate observed behavior, inferred decisions and approved decisions before migrating; governance: only approved decisions become constraints the migration is checked against |
| Cannibalisation | `find_overlap.py`: `why-ai-coding-agents-copy-legacy-architecture` 55.4, `adrs-for-software-migrations` 51.6, `ai-accelerating-cybersecurity-migration-problem` 46.5 (match on "migration"/"legacy" only). No page covers vendor migration benchmarks or behavioral parity. Verdict: **clear**. |
| Cross-links | `ai-assisted-software-migrations-architectural-drift`, `adrs-for-software-migrations`, `reverse-engineering-architectural-decisions-research`, article B |

Scope: 900-1,200 words. Distinguish benchmark success, semantic understanding, architectural authority and production acceptance. Credit behavioral parity as valuable (financial rounding rules are the chat's example of why exact parity matters). OpenAI itself says production systems need expert review and testing. Mention MultiLangBench (87.4%, 20 languages) and its Apache 2.0 harness if verified.

### B. Evergreen cornerstone (phase 1)

| Field | Value |
|---|---|
| Kind | insight |
| Title | AI Legacy Modernization: What Must Survive the Rewrite? |
| Slug | `ai-legacy-modernization-what-must-survive` |
| Report-anchored (ADR-015) | no |
| Topic hub | software-migrations-modernization |
| Content type (`--type`) | Perspective (Mneme's argument; no single external anchor) |
| OG headline | What Must Survive the Rewrite? (5 words) |
| Editorial gate | pass: distinct query (AI legacy modernization, legacy application modernization) and cornerstone support for the new "what survives" track |
| Five questions | changed: models and vendor tools now extract business rules and map dependencies; matters: extraction is becoming a commodity, so the hard part moves to deciding which recovered rules are authoritative; breaks: teams promote whatever the old system does into the spec, bugs and retired workarounds included; do: classify each recovered fact as observed, inferred or approved, and give approval an owner; governance: approved decisions become constraints that migration work is checked against |
| Cannibalisation | `find_overlap.py`: `why-ai-coding-agents-copy-legacy-architecture` 33.6, `use-cases/legacy-codebase-memory` 28.2, `demo/legacy-vs-target-architecture` 23.9. Verdict: **re-angle, clear on that angle**: before-migration adjudication of what survives, not during-migration drift. It must not restate the existing cornerstone's "four states" and path-scoping argument; link to it. |
| Cross-links | `ai-assisted-software-migrations-architectural-drift`, `reverse-engineering-architectural-decisions-research`, `concepts/engineering-decision-governance`, article A |

Scope: 1,800-2,200 words. Flow: system evidence → behavioral reconstruction → candidate decisions → human adjudication → governing constraints → migration execution → differential tests and decision-linked evidence. Include the organizational questions: who authorizes a changed business rule, how conflicting sources are handled, which checks can be automated.

**Merged into B (not a separate article):** the chat's P1 "Recovering Business Logic Is Not the Same as Recovering Decisions". `find_overlap.py` scores it 92.1 against `reverse-engineering-architectural-decisions-research`, which already argues that recovery finds structure but misses rationale. It becomes one section of B (business-rule extraction tools vs decision authority), linking to the research piece.

**Running example (all articles in this brief):** a legacy banking application.

| Recovered information | What it tells us | Treatment |
|---|---|---|
| COBOL truncates a decimal value | observed behavior | test parity; confirm the intended financial rule |
| A legacy service reads the database directly | architectural implementation | decide whether it was deliberate or incidental |
| The target architecture requires a storage adapter | reviewed engineering decision | check with an enforceable rule |
| Data must stay in an approved jurisdiction | deployment requirement | validate with an authorized deployment control (not Mneme) |
| A workaround exists for a retired interface | historical implementation | review whether to remove it |

Governing line: observed does not automatically mean authoritative.

### C. Behavioral parity vs architectural compliance (phase 2)

Merged with the migration-strategies chat's P0 "AI-Assisted Language Migrations: Why Compiling Is Not Enough" (see [that brief](2026-10-13-research-migration-strategies.md)): both argue that behavior-preserving verification and decision compliance answer different questions. One article, owned here.

| Field | Value |
|---|---|
| Kind | insight |
| Title | Behavioral Equivalence Is Not Architectural Compliance: Verifying an AI-Assisted Migration |
| Slug | `behavioral-equivalence-architectural-compliance-migration` |
| Report-anchored (ADR-015) | no |
| Topic hub | software-migrations-modernization |
| Content type (`--type`) | Perspective |
| OG headline | Same Outputs, Different Architecture (4 words) |
| Editorial gate | pass: distinct query (behavioral equivalence testing, migration verification) |
| Five questions | changed: AI-assisted rewrites now run at scale (GitHub's Copilot TypeScript-to-Rust migration); matters: shadow and differential tests become the acceptance gate; breaks: code can match outputs and pass local tests while changing retry, ordering, cancellation or error semantics, or crossing a boundary; do: define acceptance as both behavioral evidence and decision compliance; governance: decision checks run alongside equivalence tests, each answering its own question |
| Cannibalisation | `find_overlap.py`: `ai-assisted-software-migrations-architectural-drift` 65.1 / 71.1, `adrs-for-software-migrations` 60.7, `use-cases/ai-assisted-software-migrations` 46.5 / 54.2. Those pages cover drift and decision states, not verification methods. Verdict: **re-angle**: the article is about what each verification method can prove. |
| Cross-links | article A, `ai-assisted-software-migrations-architectural-drift`, `strangler-fig-migrations-architectural-drift` |

Evidence: Grab's shadow testing and response comparison; GitHub's Copilot Rust migration (800k+ lines, 128 merged PRs, ~14.5 weeks); all to verify.

### D. COBOL-to-Java: which decisions need verification before cutover (evidence-gated)
### E. Decision-governed migration: a controlled experiment (evidence-gated)

Both **deferred**. The chat gates them on a reproducible fixture, accurate capability classification and reviewed results. Rebrief when the experiment exists.

## Draft quality gate (filled at build time)

| Check | openai-cobol-migration-benchmark-behavioral-parity | ai-legacy-modernization-what-must-survive |
|---|---|---|
| stop-slop score (/50, pass >= 35) | 40 | 38 (8/7/8/8/7) |
| `lint_prose.py` (built page) | 0 errors; 4 warnings kept: COBOL appears in OpenAI's verbatim title before its body expansion; GPT, IBM and Codex CLI are product or company names | 0 errors; 2 warnings kept: 'PL' is the linter splitting PL/I (expanded at first use); CLI is part of Codex CLI |
| Cold read: thesis as restated | Matching outputs byte for byte cannot tell you which legacy behaviors the organization wants to keep, so a person has to approve them. Matches. | Vendor tools can extract what a legacy system does, but only behavior a named owner approved should bind the rewrite. Matches. |
| Cold read: unclear terms, and how resolved | low-resource languages, reasoning effort, model names, oracle, typed rule, lifecycle all defined; cost claim cut; low-effort comparison labelled; built-page pass: PASS. | 14 terms defined (copybooks, IBM Z, storage adapter, parity, typed rule and others); 'equal confidence' claim corrected; built-page pass: PASS. |

**Pre-merge Opus audit (2026-10-20):** 4 blockers and 11 should-fix findings across the batch, all fixed before the PR: shell-write coverage per agent (Claude Code review), typed-rule capability and a misquoted Grab line (Node.js to Go), an invented Kyverno quote (Policy as Code), warn vs strict exit codes (Kubernetes), Codex CLI naming, OpenAI's evaluation order, and the overstated decision-recovery study finding (OpenAI, cornerstone). The audit re-verified every load-bearing figure against the live sources.

## Key facts, figures, sources

| Claim | Source URL | Verified? |
|---|---|---|
| OpenAI announcement on legacy / low-resource-language coding, 2026-10-19 | https://x.com/OpenAI/status/2112310345863930168 (find the linked OpenAI blog or research page and cite that, not X) | unverified |
| 97.9% pass rate on OpenAI's COBOL migration evaluation (GPT-6.1 Sol, higher reasoning effort); the evaluation requires migrated programs to reproduce observable outputs exactly | OpenAI page (to capture) | unverified |
| MultiLangBench: 87.4% average across 20 languages (GPT-6 Astra) | OpenAI page | unverified |
| OpenAI says production systems still need expert review and testing | OpenAI page | unverified |
| MultiLangBench harness released under Apache 2.0 | GitHub repo (to capture) | unverified |
| AWS Transform extracts business functions and rules, maps dependencies, generates specifications linked to tests | AWS Transform docs (to capture) | unverified |
| IBM watsonx Code Assistant for Z: application discovery, COBOL refactoring, semantic-equivalence validation | IBM product docs (to capture) | unverified |

**Verified record (2026-10-20).** The table above is the scope-time list. Each built article's checked sources follow; anything absent from them was cut, not softened.

### `openai-cobol-migration-benchmark-behavioral-parity`

| Claim | Source URL | Verified? |
|---|---|---|
| OpenAI announcement, 2026-10-19 | https://openai.com/index/low-resource-programming-languages/ | verified: https://openai.com/index/low-resource-programming-languages/ (header, "October 19, 2026") |
| COBOL migration eval: migrate to C++, Java, Kotlin, Python or Rust; hidden tests require "byte-for-byte parity on observable outputs"; success only if all tests pass | same | verified: same (section "2. Migrating a COBOL codebase") |
| GPT-6.1 Sol 86.6% at low reasoning effort vs 5.4% for GPT-5.6 Sol; 97.9% at higher reasoning effort, "close to saturation" | same | verified: same (intro and section 2). Brief said "higher reasoning effort": matches. |
| Fixed-point arithmetic truncation vs rounding example | same | verified: same (section 2) |
| Production caveat: "still requires expert review and testing against the system's business rules and dependencies" | same | verified: same (section 2, paragraph 3). The one direct quote in the article (12 words). |
| MultiLangBench: SQLite-compatible engine, 20 languages, GPT-6 Astra 87.4% at maximum reasoning effort, up from 26.8% for GPT-5.6 Sol; COBOL hardest at 72.1% | same | verified: same (section "1. Building SQLite from scratch (MultiLangBench)"). Brief's "GPT-6 Astra" matches. Note: some press coverage gives a ~38% baseline; OpenAI's page says 26.8%, used here. |
| Tests adapted from SQLite's test suite | same | verified: same (section 1) |
| MultiLangBench harness released under Apache 2.0 | https://github.com/openai/MultiLangBench | verified: https://github.com/openai/MultiLangBench (README "License": "licensed under the Apache License, Version 2.0"); linked from OpenAI's page |
| AWS Transform: analysis of mainframe codebases, documentation generation, business logic extraction, decomposition of monoliths | https://docs.aws.amazon.com/transform/latest/userguide/transform-app-mainframe.html | verified: same (opening paragraph "Modernization of mainframe applications") |
| AWS Transform "maps dependencies, generates specifications linked to tests" | brief | cut: not stated on the AWS user-guide page fetched; only on re:Post / partner pages. Article keeps the four verified capabilities. |
| IBM watsonx Code Assistant for Z: dependencies insight, refactor COBOL into modular business services, auto-generated unit tests comparing semantic equivalence of Java to COBOL | https://www.ibm.com/products/watsonx-code-assistant-z | verified: same (sections "Understand and Discovery", "Refactoring", "Validation, Semantic Equivalence, and Testing") |

### `ai-legacy-modernization-what-must-survive`

| Claim (as used in the article) | Verified |
|---|---|
| AWS Transform for mainframe builds dependency graphs across programs, entry points, data stores | verified: https://aws.amazon.com/blogs/migration-and-modernization/reimagine-mainframe-applications-with-traceability-and-speed-using-aws-transform/ ("Business Function Catalog"; post dated 26 June 2026, title "Reimagine mainframe applications with traceability and speed using AWS Transform") |
| Deterministic static analysis on each program; rules extracted with natural-language description and source traceability | verified: same URL ("Business Rule Extraction") |
| Requirements with testable acceptance criteria | verified: same URL ("Generating Requirements"). Note: the post says "requirements", not "specifications", and does not mention test generation, so the brief's "specifications linked to tests" wording was changed to "requirements with testable acceptance criteria". |
| Three dispositions (captured / not applicable / delegated); metric "not accounted for = 0" | verified: same URL ("Generating Requirements", traceability paragraph). The post does not say who assigns dispositions; the article says exactly that. |
| IBM watsonx Code Assistant for Z: maps applications and dependencies; refactors COBOL and PL/I into modular business services; COBOL to Java with generative AI; auto-generated unit tests "to compare semantic equivalence" | verified: https://www.ibm.com/products/watsonx-code-assistant-z (Features: "Understand your application landscape", "Auto-refactor into modular services", "Convert COBOL to Java in minutes"). IBM says "business logic", not "business rules"; the article attributes rule extraction to AWS only and describes IBM by its own wording. |
| OpenAI published new evaluations for low-resource programming languages, including COBOL migration, on 19 October 2026 | verified (indirect): openai.com returns HTTP 403 to fetch. Confirmed via OpenAI's research index listing as returned by search ("Advancing coding in low-resource programming languages", 19 Oct 2026, "new evaluations for software engineering, SQLite, and COBOL migration") and the OpenAI X post https://x.com/OpenAI/status/2112310345863930168. No figures from the OpenAI page are used in this article; 97.9%, MultiLangBench and the exact-output requirement are left to article A, which links to the primary page. |
| September 2026 preliminary study by Karan, Dhar, Soliman and Vaidhyanathan: model-extracted decisions missed the rationale | verified: https://arxiv.org/abs/2609.03721 as cited and quoted in the published /insights/reverse-engineering-architectural-decisions-research/ page; B restates only the one-line finding |
| Stage 7 support: IBM generates unit tests comparing the new Java service with the original COBOL | verified: IBM product page above ("Convert COBOL to Java in minutes") |
| 97.9%, MultiLangBench 87.4%, expert-review statement, Apache 2.0 harness | cut from B: article A's material; B only links to A. |

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Path-scoped deterministic enforcement of typed rules (pre-write and CI) | SHIPPED (0.10.0), within the native-write-tool and active-typed-rule limits |
| Decision Index with lifecycle, versions, source | SHIPPED (0.10.0) |
| Decision discovery / data engine recovering candidate decisions from legacy systems | CONCEPTUAL (research; a research-only harness exists, no validated results) |
| Distinguishing observed, inferred and approved decisions with provenance | PLANNED design direction (ADR-031 accepted, unreleased) |
| Decision-linked migration evidence, differential testing integration | CONCEPTUAL |
| COBOL or mixed-language parsing / integration | not claimed; there is none |
| Enforcing financial or regulatory business rules | not claimed: Mneme enforces engineering decisions, not arbitrary business-rule execution |

## Positioning constraints

- Mneme does not compete on business-logic extraction. AWS Transform and IBM already do it; say so plainly.
- Name no customer, prospect or partner in connection with modernization.
- No "Mneme governs legacy migration end to end"; no claimed COBOL integration.
- Business-rule execution is not engineering-decision enforcement. Data residency is checked by deployment controls; Mneme can say which decision requires it.

## Non-insight site edits requested

- `use-cases/ai-assisted-software-migrations`: add a short "Before the migration: deciding what must survive" section, labelled as research direction, not shipped extraction. Separate contract; not in the insights PR.
- Topic hub `software-migrations-modernization`: curate the two tracks (during vs before) once A and B ship. That is part of registration.
- No modernization concept page and no new landing page (the chat says so explicitly).

## Open questions

- None blocking A and B. C waits for phase 2. D and E wait for an experiment.
