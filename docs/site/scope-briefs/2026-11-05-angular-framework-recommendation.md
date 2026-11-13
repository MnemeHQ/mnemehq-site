# Scope brief: Post-Angular Framework Recommendation

Status: **built, queued for 2026-11-17** (`angularjs-to-angular-migration-ai`; article PR on its own `site/` branch)

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
| stop-slop score (/50, pass >= 35) | 39 |
| `lint_prose.py` | errors: 0 on the built page; 0 warnings |
| Cold read: thesis as restated | "agents carried the migration, silent failures were caught by tests not diffs; record decisions and check architecture separately" (matches the brief) |
| Cold read: unclear terms, and how resolved | Nx, esbuild, test tools, AGENTS.md, zoneless, standalone, signals: glossed; zoneless vs change-detection strategy disambiguated; heading changed to 233 commits in 25 days |
| Pre-merge Opus claim audit | blockers and should-fix items applied; see the article PR |

## Agreed scope

Article A outline: why AngularJS migrations persist; AngularJS vs modern Angular architecture; where agents accelerate work; incremental vs full replacement; five architectural risks (dependency boundaries, shared services, routing, state ownership, temporary adapters); capturing legacy, target and transitional decisions; enforcing constraints during agent changes; separating behavioral parity from architectural compliance; a migration governance checklist; what Mneme enforces today. 1,500 to 2,000 words. Answer the practical Angular question first, and bring Mneme in only where governance genuinely arises.

Article B outline: upgrade vs architectural modernization; what the Angular CLI and schematics automate; NgModules to standalone; signals and zoneless change detection; where agents help and where they add risk; preserving service, DI, routing and data-access boundaries; verification matrix (build, tests, behavior, architecture, decision evidence); rollout and rollback.

Article C: a small Angular app with a legacy module and a target architecture; four decision tests (no direct HttpClient in components, no legacy-module dependency, data access through approved services, retired adapters stay retired); three variants (no governance, guidance only, enforcement), scored separately for guidance, pre-mutation enforcement and CI. Comparative claims only after the experiment runs.

## Key facts, figures, sources

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| time cockpit's September 2026 AngularJS migration with Claude Code: 233 commits, 25 working days | https://www.timecockpit.com/blog/angularjs-to-angular-migration-claude-code/ ("AngularJS to Angular Migration in a Month with Claude Code", Karin Huber, software architects gmbh, 3 Sep 2026) | differs: 233 commits confirmed ("233 commits across 25 days of work, weekends included, 218 of them co-authored by Claude"). "25 working days" is wrong: the post says 25 days of work including weekends, and never says "working days". Use "25 days, weekends included" (verified 2026-11-12) |
| time cockpit approach: dissolved a hybrid AngularJS/Angular app (run via `@angular/upgrade` since 2018), not a screen-by-screen rewrite; customers define their own models and forms so screens could not be enumerated; 95 named, separately reviewable streams; Angular 21.2 to 22.1.2; Nx dropped, webpack to esbuild, Karma/Jasmine and Jest to Vitest | same URL | verified (approach and sequencing sections, 2026-11-12) |
| time cockpit outcomes: build 373 s (+72 s separate AngularJS toolchain) to 45 s; initial gzipped download 2.17 MB to 1.34 MB (-38%); tests 542 to 1,331 (unit 123 to 626, e2e 419 to 705); decorator inputs/outputs 266 to 7, signal-based 145 to 485; API-equivalent cost about EUR 4,250 (roughly EUR 18 per commit, list-price equivalent, not an invoice) | same URL | verified (results table, 2026-11-12) |
| time cockpit: the Angular 22 upgrade shipped as a pure version change with components pinned to the old change-detection behavior; modernization followed in about eleven batched steps, last pins removed 14 Aug; "Angular 22 changes the default change-detection strategy, a silent, sweeping behavioral change" if accepted as-is | same URL | verified (change-detection section) |
| time cockpit problems caught by tests, not by reading the diff: Excel export in list view silently unwired; start-page redirect lost when the AngularJS redirect was removed. Separately, ESLint had been silently broken before the migration began (pre-existing state, not a migration failure; corrected at the pre-merge audit). Open work left: 16 legacy NgModules, lint backlog, zone-based change detection | same URL | verified (problems and open-work sections) |
| time cockpit human role: "The gap between those two numbers is why the human review step is not optional." Humans chose sequencing, scope and the pin-then-modernize policy; `AGENTS.md` split exploration/planning/review from implementation; "Having the rules written down for agents beforehand was the precondition for 233 commits in a month." 34 of the 233 commits were feature work | same URL | verified (review and rules sections) |
| Angular tooling supports incremental migration to standalone components and signal APIs; v21+ makes zoneless change detection default | https://angular.dev/reference/migrations/standalone ; https://angular.dev/reference/migrations ; https://angular.dev/guide/zoneless | verified. Standalone: `ng generate @angular/core:standalone`, three ordered modes, apps "can optionally and incrementally adopt the new standalone style without any breaking changes"; `path` option migrates sections incrementally. Signals: migrations list input(), output() and signal queries conversions. Zoneless: "Zoneless is the default in Angular v21+ so you do not need to do anything to enable it." (v20 needs `provideZonelessChangeDetection()`) |
| Current Angular major as of Nov 2026 is v22 (Baseline date 2026-05-07; v22 announcement changelog link dated 2026-06-03, inferred from URL) | https://angular.dev/reference/versions | verified: v22 is first in "Actively supported versions" (footer v22.2.6). The release date itself is not stated on the page; do not print a v22 release date |
| AngularJS support ended | https://docs.angularjs.org/misc/version-support-status | verified: "AngularJS support has officially ended as of January 2022." Page does not say "no longer maintained" or give an LTS end date. Secondary (search result, page not fetched, blog returned 403): https://blog.angular.dev/discontinued-long-term-support-for-angularjs-cc066b82e65a reports LTS ended 31 Dec 2021. If citing 31 Dec 2021, cite as "announced end of LTS" and re-check the blog; otherwise use the docs wording |
| Official AngularJS upgrade path: ngUpgrade / UpgradeModule for hybrid apps | https://angular.dev/api/upgrade/static/UpgradeModule | partly verified: API reference exists on angular.dev, status "stable", no deprecation notice, described as "An NgModule, which you import to provide AngularJS core services" and "has an instance method used to bootstrap the hybrid upgrade application". NOT FOUND: a prose upgrade guide on angular.dev (guide/upgrade and guide/upgrade/overview return only the homepage; sitemap shows none). Older guide at v17.angular.io/guide/upgrade could not be read. Do not claim angular.dev documents a step-by-step AngularJS migration guide |
| Zoneless / Zone.js opt-out, v22 release-notes claim that zoneless or OnPush became default in v22 | https://angular.dev/events/v22 | NOT FOUND - cut. v22 page says only that Signal Forms, Asynchronous Signals and Angular Aria are stable; no zoneless statement |

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
