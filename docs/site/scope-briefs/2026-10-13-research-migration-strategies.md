# Scope brief: Post-Research migration strategies

Status: **queued** for the scheduled publisher: 1 on 2026-10-28 (#244); phase 2 queued, 4 (strangler vs big-bang) on 10-31 (#251), 3 (Go translation idioms, retitled as a question) on 11-01 (#252), 5 (when not to rewrite) on 11-02 (#253); 2 merged into the OpenAI brief; 6 merged into 1

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Research migration strategies` |
| Created / last updated (UTC) | 2026-10-13 / 2026-10-13 |
| Shape | 1 user turn: a pasted "languages toward 2030" outlook (Go, Node.js, Java; collapsed behind "Show more", expanded and read 2026-10-20) with a request to research migration patterns, especially migration to Go, for the migration topic. 1 answer: research findings, six case studies, six patterns and a six-article list. |
| Repo check | No page covers language migrations, Go, or the Uber, Grab, Dropbox, Twitch, Stripe or GitHub Copilot Rust accounts. The software-migrations-modernization hub covers architectural drift during migrations (see the [OpenAI brief](2026-10-20-assess-openai-modernization-announcement.md) for the list). |

**Research corrections the article must keep** (the chat's own assessment of the pasted outlook): "Go cuts cloud bills by 10x" is unsupported as a general claim; "Go is ideal for tiny Wasm" is misleading (standard Go Wasm binaries are large; TinyGo fits better); "Node.js is losing backend relevance" is not established; Java virtual threads help I/O-bound concurrency, not CPU-bound speed. Do not repeat the outlook's claims as fact.

**Framing:** not a Go advocacy series. Software is getting cheaper to change; the decisions governing those changes stay consequential.

## Build cards

### 1. Migrating from Node.js to Go (phase 1)

| Field | Value |
|---|---|
| Kind | insight |
| Title | Migrating from Node.js to Go: The Architectural Decisions That Must Survive the Rewrite |
| Slug | `nodejs-to-go-migration-architectural-decisions` |
| Report-anchored (ADR-015) | no (several engineering accounts, none is the spine) |
| Topic hub | software-migrations-modernization |
| Content type (`--type`) | Perspective (verify against the type rule: if Uber and Grab carry the article, Analysis does not apply either, since neither is in the title) |
| OG headline | Rewrite the Code, Keep the Decisions (6 words) |
| Editorial gate | pass: distinct query (Node.js to Go migration), the hub's best search entry point per the chat |
| Five questions | changed: teams rewrite Node.js and Python services in Go for density and platform standardization, and agents make rewrites cheaper; matters: the language choice is itself an architecture decision with scope and lifecycle; breaks: both stacks coexist for months, and new work lands in the wrong one, crosses the approved interface, or cuts over without its acceptance evidence; do: write the migration decision with scope, lifecycle (Node transitional, Go target), precedence and cutover authority; governance: path-scoped rules keep new work on the target and evidence gates the cutover |
| Cannibalisation | `find_overlap.py`: `architectural-drift-cloud-platform-migrations` 37.0, `adrs-for-software-migrations` 36.2, `ai-assisted-software-migrations-architectural-drift` 35.5, `strangler-fig-migrations-architectural-drift` 35.5. Verdict: **clear** (language-migration query; reuses the hub's lifecycle model by linking, not restating). |
| Cross-links | `adrs-for-software-migrations`, `strangler-fig-migrations-architectural-drift`, `ai-assisted-software-migrations-architectural-drift`, `use-cases/ai-assisted-software-migrations` |

Case studies: Uber (Node.js API gateway to Go, partly to align with supported Java/Go platforms; Go tooling and code-generation problems) and Grab (zero-downtime migration with shadow testing, response comparison, endpoint-by-endpoint rollout, instant rollback; percentage-based rollout misled when endpoint volumes differed). Dropbox (Python to Go) as a supporting example if verified.

Illustrative decision (label as illustrative): all new payment-processing functionality uses the Go implementation; existing Node.js endpoints keep serving during the migration; cross-language calls use the approved interface; cutover needs contract-test approval plus latency and error-rate validation.

| Dimension | Example |
|---|---|
| Scope | new Go packages and the payment service boundary |
| Lifecycle | Node.js transitional; Go target |
| Precedence | the approved migration decision overrides older guidance in its scope |
| Authority | architecture owner approves the target; service owner authorizes cutover |
| Enforcement | path-scoped restrictions plus language-aware external checks |
| Evidence | CI results, compatibility tests, performance measurements |

**Merged into 1:** the chat's P1 "How to Govern a Multi-Language Codebase During Modernization" (`find_overlap.py` 49.3 against `codebase-memory-during-migrations`, and `adrs-for-software-migrations` already covers scoped states). Its point, that authority must be tracked across transitional and target implementations, becomes the coexistence section of article 1.

### 2. AI-Assisted Language Migrations: Why Compiling Is Not Enough

**Merged** into the OpenAI brief's article C ("Behavioral Equivalence Is Not Architectural Compliance"), which owns it. Both argue that behavior-preserving verification and decision compliance answer different questions; publishing both would split one query. The GitHub Copilot Rust migration is that article's lead evidence.

### 3. When Agents Translate to Go, They Bring the Source Language With Them (phase 2)

| Field | Value |
|---|---|
| Kind | insight |
| Title | When Agents Translate Code to Go, They Bring the Source Language With Them (re-angle of the chat's "The Hidden Architectural Risks of Migrating Python and Java to Go") |
| Slug | `ai-code-translation-go-source-language-patterns` |
| Topic hub | software-migrations-modernization |
| Content type (`--type`) | Perspective |
| OG headline | Go Syntax, Java Architecture (4 words) |
| Editorial gate | pass: new evidence (Go 2025 developer survey: 33% struggle with idiomatic Go; 53% name non-functional code as a top problem with AI developer tools) |
| Cannibalisation | `find_overlap.py` 38.6 against `barbara-liskov-python-encapsulation-ai-governance` (incidental). Intra-batch: re-angled away from article 1 (that one is about the migration decision; this one is about idiom-level drift: concurrency, error handling, transaction semantics). Relates to `why-ai-coding-agents-copy-legacy-architecture` (architecture-level copying); link, don't restate. Verdict: **re-angle** (as titled). |

The chat frames this as a hypothesis to investigate. The article must present it as a hypothesis, not a finding.

### 4. Strangler vs Big-Bang Migration: How to Choose (phase 2)

| Field | Value |
|---|---|
| Kind | insight |
| Slug | `strangler-vs-big-bang-migration` |
| Topic hub | software-migrations-modernization |
| Content type (`--type`) | Comparison |
| OG headline | Incremental Is Not Always Safer (5 words) |
| Editorial gate | pass: distinct query (big-bang vs incremental migration); new evidence (Stripe's atomic Flow-to-TypeScript conversion vs Grab and Twitch's incremental migrations) |
| Cannibalisation | `find_overlap.py` 31.1 (four migration pages, generic match). `strangler-fig-migrations-architectural-drift` covers how to protect a strangler boundary, not when to choose it. Verdict: **re-angle**: the choice, driven by coupling, tooling and target compatibility. |

### 5. When Not to Rewrite: Modern Java, Node.js and the Economics of Migration (phase 2)

| Field | Value |
|---|---|
| Kind | insight |
| Slug | `when-not-to-rewrite-migration-economics` |
| Topic hub | software-migrations-modernization |
| Content type (`--type`) | Perspective |
| OG headline | Sometimes the Right Migration Is None (6 words) |
| Editorial gate | pass: distinct query; counterexample that keeps the cluster honest (virtual threads, GraalVM native images, Stripe's Sorbet for Ruby) |
| Cannibalisation | `find_overlap.py` 31.1 (generic). Verdict: **clear**. Coordinate with the ROI backlog brief (economics pieces there are still unbuilt). |

### 6. Multi-language codebase governance

**Merged** into article 1 (see above).

## Draft quality gate (filled at build time)

| Check | nodejs-to-go-migration-architectural-decisions |
|---|---|
| stop-slop score (/50, pass >= 35) | 40 |
| `lint_prose.py` (built page) | 0 errors; 0 warnings |
| Cold read: thesis as restated | A Node.js to Go migration is an architecture decision that needs scope, roles, precedence, cutover authority and evidence. Matches. |
| Cold read: unclear terms, and how resolved | Uber leads as the only Node-to-Go case, Grab and Dropbox framed as other moves to Go; 15 terms defined; superlatives softened; built-page pass: PASS. |

**Pre-merge Opus audit (2026-10-20):** 4 blockers and 11 should-fix findings across the batch, all fixed before the PR: shell-write coverage per agent (Claude Code review), typed-rule capability and a misquoted Grab line (Node.js to Go), an invented Kyverno quote (Policy as Code), warn vs strict exit codes (Kubernetes), Codex CLI naming, OpenAI's evaluation order, and the overstated decision-recovery study finding (OpenAI, cornerstone). The audit re-verified every load-bearing figure against the live sources.

## Key facts, figures, sources

All from the chat, none checked. The chat cites the blogs by name; capture the exact URLs at verification.

| Claim | Source | Verified? |
|---|---|---|
| Uber replaced a Node.js API gateway with Go, partly to align with supported Java/Go platforms; hit Go tooling and code-generation problems | Uber engineering blog, API gateway architecture post | unverified |
| Grab: zero-downtime migration toward Go using shadow testing, response comparison, per-endpoint rollout, instant rollback; percentage rollout misled when endpoint volumes varied | Grab Tech blog, zero-downtime Go migration post | unverified |
| Dropbox migrated performance-critical backends from Python to Go, ~200,000 lines in the early effort, and built missing libraries | Dropbox tech blog | unverified |
| Twitch: multi-year move from a monolith to Go microservices via a Go API edge and proxy routing | Twitch engineering blog | unverified |
| GitHub Copilot: TypeScript/Node.js to Rust, 800,000+ lines, 128 merged PRs, ~14.5 weeks, incremental while shipping (September 2026) | GitHub Blog | unverified; feeds OpenAI brief article C |
| Stripe migrated 3.7M+ lines from Flow to TypeScript in one coordinated conversion | Stripe engineering blog | unverified; feeds article 4 |
| Go 2025 developer survey (published January 2026): 1/3+ build cloud infrastructure tooling; 11% work with ML models, tools or agents; 33% find idiomatic Go hard; 53% name non-functional code as a top problem with AI tools | go.dev blog | unverified; feeds article 3 |
| Java virtual threads help I/O-bound concurrency, not CPU-bound code | OpenJDK JEP 444 | unverified |
| Standard Go Wasm binaries are comparatively large; TinyGo targets small binaries | Go wiki / TinyGo docs | unverified; context only |

**Verified record (2026-10-20).** The table above is the scope-time list. Each built article's checked sources follow; anything absent from them was cut, not softened.

### `nodejs-to-go-migration-architectural-decisions`

| Claim (brief) | Verified |
|---|---|
| Uber replaced a Node.js API gateway with Go, partly to align with supported Java/Go platforms | verified, reworded: https://www.uber.com/blog/gatewayuberapi/ ("Designing Edge Gateway, Uber's API Lifecycle Management Platform", Astakhov, Thangavelu, Medisetty, 18 Aug 2020). "Second gen: the all-encompassing gateway" > "Technical challenges": 2,500 npm libraries, 50,000 tests per change, onboarding onto async Node.js patterns, "Golang and Java as the primarily supported languages", gRPC adoption not helped by their Node.js version; 800,000 req/s peak (stats list). "Third gen" > "Edge Gateway": edge layer "replaced by a single standalone Golang service paired with a UI". "Conclusion": improved resource utilization and request/core metrics (no figures); migration "2 years long". Migration section: central team migrated a few high-scale APIs as a pilot; ownership mapped to product teams; automated tracking. The post lists platform alignment as a Node.js challenge, not as a stated reason for choosing Go; article words it as context. |
| Uber hit Go tooling and code-generation problems | cut: not in the post. The only codegen mention is "~20% of mobile build is code generated" from second-gen schemas (Node.js era). |
| Grab: zero-downtime migration toward Go with shadow testing, response comparison, per-endpoint rollout, instant rollback; percentage rollout misled | verified, corrected: https://engineering.grab.com/zero-downtime-migration ("This Rocket Ain't Stopping - Achieving Zero Downtime for Rails to Golang API Migration", Lian Yuanlin, 18 Oct 2016). The source language is **Rails (Ruby), not Node.js**; context: Grab was "transitioning from a Rails + NodeJS stack to a full Golang Service Oriented Architecture". Shadowing in staging and production; JSON tokenizer response comparison, mismatches to statsd/Datadog and Slack; endpoints deployed "one by one"; "all deployments must be instantly rolled back" on unforeseen bugs; percentage lesson: "a single percent of its requests dwarfed the full load of 5 others combined", switched to RPS because "Percentages meant nothing without load context." |
| Dropbox: Python to Go, ~200,000 lines, built missing libraries | verified: https://dropbox.tech/infrastructure/open-sourcing-our-go-libraries ("Open Sourcing Our Go Libraries", Patrick Lee, 1 Jul 2014). "migrate our performance-critical backends from Python to Go", for "better concurrency support and faster execution speed"; "around 200,000 lines of Go code"; small team; built libraries for "the lack of robust libraries". |
| Twitch, GitHub Copilot Rust, Stripe, Go 2025 survey, JEP 444, Go Wasm | not used (other articles' evidence). |
| Outlook claims (Go cuts cloud bills 10x etc.) | not repeated as fact; one sentence says such claims come from language outlooks, not these accounts. |

Mneme-side sources (repo): `site/docs/supported-languages/` (TS/JS Tier 1 operationally supported; Go Tier 2 repo-level; no AST/compiler-aware enforcement), `site/docs/decision-index/` (lifecycle_status active/superseded/deprecated/inactive; no approver identity; same-scope precedence loser stored inactive, import does not report it), `site/docs/how-enforcement-works/`, `site/docs/how-to/adr-to-enforceable-decision/` (FORBID_PATH/REQUIRE_PATH do not change a verdict; FORBID_LITERAL respects include_paths).

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Path-scoped deterministic enforcement keeping new work in the target implementation | SHIPPED (0.10.0), with path selectors on the rule (optional; a rule without them is repo-wide) and native-write-tool limits for pre-write |
| Lifecycle states (transitional, target, superseded) in the Decision Index | SHIPPED as lifecycle on decisions; only active decisions with an active typed rule are enforced |
| Precedence within a scope | SHIPPED (same-scope loser stored inactive); ADR-031 resolution semantics unreleased |
| Cross-language behavioral equivalence, performance validation, automated cutover | not Mneme; integrations or future work |
| Migration decision discovery, migration-aware enforcement, migration assurance dashboard | CONCEPTUAL (research directions from the chat) |
| Language-aware dependency checks for Go | confirm against `/docs/supported-languages/` before claiming |

## Positioning constraints

- Engineering accounts are not controlled comparisons. They show that migrations happened and what they traded off, not that Go will produce the same results elsewhere.
- Do not frame Mneme as making migrations faster; the testable claim is fewer decision violations without blocking legitimate transitional changes, and that claim is unproven.
- No language advocacy.

## Non-insight site edits requested

None beyond hub registration.

## Open questions

- Confirm `--type` for article 1 at build (Perspective vs Analysis).
