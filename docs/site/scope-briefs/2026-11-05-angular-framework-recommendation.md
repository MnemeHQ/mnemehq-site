# Scope brief: Post-Angular Framework Recommendation

Status: **gathered, not built**

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Angular Framework Recommendation` |
| Created / last updated (UTC) | 2026-11-05 / 2026-11-05 |
| Shape | 1 user turn ("Scope articles"), 1 assistant turn; read in full, no truncation. Scopes three articles; the third is evidence-gated. |
| Repo check | Migration cluster exists: `ai-assisted-software-migrations-architectural-drift`, `ai-legacy-modernization-what-must-survive`, `migration-guardrails-for-ai-coding-agents`, `behavioral-equivalence-architectural-compliance-migration`, `nodejs-to-go-migration-architectural-decisions`, `/use-cases/ai-assisted-software-migrations/`. Nothing on Angular or AngularJS. |

## Build card

| Field | Value |
|---|---|
| Kind | insight cluster: A now, B after A, C evidence-gated |
| Title | A: AngularJS to Angular Migration with AI: How to Preserve Architecture. B: Angular Modernization with AI Agents: What ng update Cannot Verify. C: Can AI Migrate Angular Without Breaking Architectural Decisions? |
| Slug | A `angularjs-to-angular-migration-ai`; B `angular-modernization-ai-agents`; C `angular-ai-migration-architecture-experiment` |
| Report-anchored (ADR-015) | no (A uses the time cockpit case study as a research anchor, not as the title entity) |
| Topic hub | software-migrations-modernization |
| Content type (`--type`) | A Guide; B Guide; C Research |
| OG headline | A: Migrating AngularJS With AI Agents (5 words); B: What ng update Cannot Verify (5 words) |
| Editorial gate | A: pass, distinct query (AngularJS migration AI). B: conditional, see Cannibalisation. C: **fails** until a reproducible experiment exists |
| Five questions (A) | changed: agents now carry real AngularJS migrations (time cockpit, 233 commits, 25 days); matters: a build that passes can still break service, routing and state boundaries; breaks: legacy dependencies and temporary adapters return; teams should: record legacy, target and transitional decisions before the agent starts; governance helps: enforce those decisions on each change, verify behavior and architecture separately |
| Cannibalisation | `find_overlap.py`: A tops at 46.4 (unrelated Claude Code pages); B tops at 41.7 (`ai-legacy-modernization-what-must-survive`). Verdict: A **clear** on query, but must link the cluster and add only Angular-specific content. B **re-angle or hold**: framework-version content (`ng update`, standalone, signals, zoneless) is new, but the governance half repeats the cluster, so build B only after A shows search interest, as the chat itself advises. C **drop for now** (evidence-gated). |
| Cross-links | `ai-assisted-software-migrations-architectural-drift`, `ai-legacy-modernization-what-must-survive`, `behavioral-equivalence-architectural-compliance-migration`, `/use-cases/ai-assisted-software-migrations/` |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | errors: 0; warnings fixed or justified: |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

## Agreed scope

Article A outline: why AngularJS migrations persist; AngularJS vs modern Angular architecture; where agents accelerate work; incremental vs full replacement; five architectural risks (dependency boundaries, shared services, routing, state ownership, temporary adapters); capturing legacy, target and transitional decisions; enforcing constraints during agent changes; separating behavioral parity from architectural compliance; a migration governance checklist; what Mneme enforces today. 1,500 to 2,000 words. Answer the practical Angular question first, and bring Mneme in only where governance genuinely arises.

Article B outline: upgrade vs architectural modernization; what the Angular CLI and schematics automate; NgModules to standalone; signals and zoneless change detection; where agents help and where they add risk; preserving service, DI, routing and data-access boundaries; verification matrix (build, tests, behavior, architecture, decision evidence); rollout and rollback.

Article C: a small Angular app with a legacy module and a target architecture; four decision tests (no direct HttpClient in components, no legacy-module dependency, data access through approved services, retired adapters stay retired); three variants (no governance, guidance only, enforcement), scored separately for guidance, pre-mutation enforcement and CI. Comparative claims only after the experiment runs.

## Key facts, figures, sources

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| time cockpit's September 2026 AngularJS migration with Claude Code: 233 commits, 25 working days | unverified: find the time cockpit write-up | unverified |
| Angular tooling supports incremental migration to standalone components and signal APIs; v21+ makes zoneless change detection default | unverified: verify against angular.dev migration guides and the version actually current | unverified |

## Mneme claims and maturity

| Claim | SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL |
|---|---|
| Forbidden-import and dependency-boundary rules enforce the four Angular decisions | to classify at audit; the chat says some rules need custom static checks, so state only what current docs support |
| Migration governance checklist | guidance, not a product claim |

## Positioning constraints

No comparative performance claim for Mneme on Angular. Separate official Angular tooling facts from Mneme claims.

## Non-insight site edits requested

None. The CTA path (Architecture Audit, then migration guide) uses existing pages.

## Open questions

Owner: build A only now, or A and B? C waits for a reproducible repo.
