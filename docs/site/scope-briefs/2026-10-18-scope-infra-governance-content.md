# Scope brief: Post-Scope infra governance content

Status: **queued** for the scheduled publisher (one article per day from 2026-10-23; PRs #239-#244) (1 and 2: batch 4, phase 1; 6: phase 2; 4: evidence-gated; concept page: owner decision, separate contract)

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Scope infra governance content` |
| Created / last updated (UTC) | 2026-10-18 / 2026-10-18 |
| Shape | 2 user turns. The first carries a long strategy answer (hidden behind "Show more"; expanded and read 2026-10-20) and a "scope the content" request answered with a six-piece cluster. The second asks whether to add an infrastructure governance concept page (answer: yes, `/concepts/infrastructure-governance/`). The strategy answer's market sizing, competitor assessment and validation plan are private and tracked outside this repo. |
| Repo check | `concepts/policy-as-code`, `concepts/governance-infrastructure` (a different concept despite the reversed name), `concepts/architecture-as-code`, `supported-languages/terraform-governance` (2026-06-02), `when-agents-launch-the-database` (2026-06-05), `ai-infrastructure-governance-category` (2026-05-28). No page mentions Kyverno, Sentinel, HPA or connection budgets. **`/platforms/` FAQ says Mneme "does not provision cloud resources, manage IAM, or enforce infrastructure policy"**: that stays true and the cluster must not contradict it. |

Cluster thesis (from the chat): failures increasingly happen between independently managed layers. The application, database, Kubernetes cluster and infrastructure deployment can each pass their own checks while the system as a whole breaks an engineering decision. The articles show where a cross-layer decision has to apply and which tool enforces each part. They do not claim Mneme enforces infrastructure.

**Common example for every piece:** the application must reach PostgreSQL through its approved data adapter, and the deployment must respect a database connection budget. Application control: detect a forbidden direct database import (a Mneme rule today). Infrastructure control: check replica and pool limits against the budget (an external check or a future extension). Evidence: which decision, which version, which rule, which artifact, which verdict.

## Build cards

### 1. When Kubernetes Works but the Application Still Fails (phase 1)

| Field | Value |
|---|---|
| Kind | insight |
| Title | When Kubernetes Works but the Application Still Fails |
| Slug | `kubernetes-scaling-database-connection-budget` |
| Report-anchored (ADR-015) | no |
| Topic hub | architectural-governance |
| Content type (`--type`) | Perspective (no single external anchor; Kubernetes and PostgreSQL docs are supporting citations) |
| OG headline | Every Layer Passed. The System Failed. (6 words) |
| Editorial gate | pass: distinct query (Kubernetes database connection limits, autoscaling) and a new audience (SRE, platform) for the decision thesis |
| Five questions | changed: autoscaling and agent-written config make replica counts and pool sizes change faster than anyone re-checks them; matters: HPA can scale pods past what the database accepts; breaks: Kubernetes and PostgreSQL each behave correctly while the service runs out of connections; do: write the connection budget down as an architecture decision and say where it applies (pool config, HPA max, deployment review, monitoring); governance: one recorded decision feeds several enforcement points, each tool checking its own part |
| Cannibalisation | `find_overlap.py`: `when-agents-launch-the-database` 38.7, `openclaw-and-the-limits-of-autonomous-coding` 29.9, `why-prompt-memory-fails-at-scale` 28.6 (all incidental). Verdict: **clear**. |
| Cross-links | `concepts/policy-as-code`, `concepts/architecture-as-code`, `when-agents-launch-the-database`, `supported-languages/terraform-governance`, article 2 |

**Merged into 1:** the chat's P1 "Database Connection Budgets Are Architecture Decisions" targets the same query and the same example. Its worked calculation becomes a section of article 1: 12 max replicas × 12 pool connections = 144 potential connections against a limit of 100 (hypothetical, before other clients or reserved connections; a pooler such as PgBouncer changes the result). A reproducible guide with config files and pass/fail output waits for a fixture (phase 3).

Outline: the incident shape; why it is cross-layer rather than a Kubernetes defect; what Kubernetes and PostgreSQL each validate; the connection budget as a decision; where it must apply; which controls are static and deterministic and which need runtime measurement; how one decision links the enforcement points. 1,500-1,900 words.

### 2. Policy as Code Enforces Rules. Who Governs the Decisions Behind Them? (phase 1)

| Field | Value |
|---|---|
| Kind | insight |
| Title | Policy as Code Enforces Rules. Who Governs the Decisions Behind Them? |
| Slug | `policy-as-code-engineering-decisions` |
| Report-anchored (ADR-015) | no |
| Topic hub | architectural-governance |
| Content type (`--type`) | Perspective |
| OG headline | The Rule Outlived Its Decision (5 words) |
| Editorial gate | pass: distinct query (policy governance, OPA/Kyverno policy lifecycle) and an integration argument the concept page does not make |
| Five questions | changed: OPA, Kyverno and Sentinel are standard in platform teams, and agents now write the code they evaluate; matters: a policy is only as current as the decision behind it; breaks: a rule keeps passing or blocking after the decision it encoded was superseded, and nobody can say who owns it; do: track each policy back to a decision with an owner, scope, precedence and lifecycle; governance: the decision record supplies context to existing engines rather than replacing them |
| Cannibalisation | `find_overlap.py`: `concepts/policy-as-code` **58.9**, `reverse-engineering-architectural-decisions-research` 45.8, `programmable-ai-policy-executable-architectural-intent` 31.6. The concept page already defines Policy as Code, PDP/PEP and "where Mneme fits". Verdict: **re-angle**: this article is about policy lifecycle and authority (a correct rule that no longer represents an approved decision), told through OPA/Kyverno/Sentinel. It links to the concept for definitions and does not repeat them. |
| Cross-links | `concepts/policy-as-code`, `programmable-ai-policy-executable-architectural-intent`, `concepts/engineering-decision-governance`, `concepts/precedence-semantics`, article 1 |

Outline: what OPA, Kyverno and Terraform policy tools already do (OPA evaluates Terraform plans; Kyverno has scoped exceptions and policy reports); a concrete rule that works but no longer reflects an approved decision; policy evaluation vs governing the source decision; ownership, applicability, precedence, lifecycle, exceptions; how a decision model could give existing engines context; traceability across policy changes; Mneme's complementary role. An integration argument, not a takedown. 1,600-2,000 words.

### 6. The Missing Link Between Platform Engineering and Enterprise Architecture (phase 2)

| Field | Value |
|---|---|
| Kind | insight |
| Title | The Missing Link Between Platform Engineering and Enterprise Architecture |
| Slug | `platform-engineering-enterprise-architecture-decisions` |
| Report-anchored (ADR-015) | no |
| Topic hub | architectural-governance |
| Content type (`--type`) | Perspective |
| OG headline | Architects Decide. Platforms Enforce. Who Connects Them? (7 words) |
| Editorial gate | pass: distinct query (platform engineering governance, enterprise architecture governance); the chat puts it after the technical pieces so they give it substance |
| Five questions | to be completed at phase 2 rebrief |
| Cannibalisation | `find_overlap.py`: `palantir-agentic-governance-engineering-governance` 45.4, `platforms` 38.1, `microsoft-agent-platform-governance-layer` 38.1. Verdict: **clear** (provisional; rerun at phase 2). |
| Cross-links | articles 1 and 2, `/platforms/`, `/for/platform/` |

### 4. From Architecture Decision to Infrastructure Guardrail (evidence-gated)

**Deferred.** The chat calls it a reference architecture and experiment, not shipped enforcement. It also overlaps `supported-languages/terraform-governance` (53.7) and the concept page's "From architectural decision to enforced agent action" section. Rebrief when a cross-layer experiment has results.

### Concept page: Infrastructure Governance (owner decision; separate contract)

The chat's final turn recommends `/concepts/infrastructure-governance/`, "Infrastructure Governance: Policies, Decisions and Enforcement", as an explainer of the established discipline (Azure Policy and landing zones, HashiCorp). It would sit after article 1 and before any commercial page. It also scoped a second concept, "Application & Infrastructure Decision Governance". My recommendation is **one concept page, not two**, built under `docs/site/concept-publication.md` in its own PR, because:

- "Infrastructure decision governance" is a new term. The terminology lock requires a PUBLISHING.md amendment, and ADR-001 forbids "governance" as the category name, so it can only be a concept term.
- The page must be explicitly distinguished from `concepts/governance-infrastructure` (the platform layer that runs governance).
- It must stay consistent with the `/platforms/` FAQ (Mneme does not enforce infrastructure policy today).
- SEO caveat from the chat: the phrase also draws public-sector and physical-infrastructure searches (OECD). Target cloud and software infrastructure explicitly.

## Draft quality gate (filled at build time)

| Check | kubernetes-scaling-database-connection-budget | policy-as-code-engineering-decisions |
|---|---|---|
| stop-slop score (/50, pass >= 35) | 39 | 39 |
| `lint_prose.py` (built page) | 0 errors; 0 warnings (121-word paragraph split after the audit) | 0 errors; 0 warnings (OPA expanded in the lede after the audit) |
| Cold read: thesis as restated | Autoscaling and PostgreSQL each work as documented, but nobody owns the connection budget; record it as a decision and enforce each part with the right tool. Matches. | Policy engines evaluate rules reliably, but nothing ties a rule to the decision behind it, so policies go stale when decisions change. Matches. |
| Cold read: unclear terms, and how resolved | Mneme and Kyverno introduced at first mention; rendered manifests, data adapter, typed rule, FAIL defined; FAQ figures aligned to 97; built-page pass: PASS. | Rego, typed rule, inactive status, CTA defined; overstatements softened; replica cap aligned with the Kubernetes article (6 with surge); built-page pass: PASS. |

**Pre-merge Opus audit (2026-10-20):** 4 blockers and 11 should-fix findings across the batch, all fixed before the PR: shell-write coverage per agent (Claude Code review), typed-rule capability and a misquoted Grab line (Node.js to Go), an invented Kyverno quote (Policy as Code), warn vs strict exit codes (Kubernetes), Codex CLI naming, OpenAI's evaluation order, and the overstated decision-recovery study finding (OpenAI, cornerstone). The audit re-verified every load-bearing figure against the live sources.

## Key facts, figures, sources

| Claim | Source URL | Verified? |
|---|---|---|
| HPA scales the number of Pods based on observed metrics | Kubernetes docs, Horizontal Pod Autoscaling (to capture) | unverified |
| PostgreSQL limits concurrent connections (`max_connections`; reserved superuser connections) | PostgreSQL docs, connection settings (to capture) | unverified |
| OPA can evaluate Terraform plans | OPA docs, Terraform (to capture) | unverified |
| Kyverno supports policy exceptions and policy reports | Kyverno docs (to capture) | unverified |
| HashiCorp Sentinel has enforcement levels (advisory, soft-mandatory, hard-mandatory) and overrides | HashiCorp docs (to capture) | unverified |
| 82% of container users run Kubernetes in production (CNCF 2025) | CNCF survey (to capture) | unverified; optional context |
| Gartner: 80% of large software engineering orgs will have platform teams by 2026 | Gartner (to capture) | unverified; optional; Gartner figures need the original citation |
| Azure Policy / landing zones as infrastructure governance | Microsoft Learn (to capture) | unverified; concept page only |

**Verified record (2026-10-20).** The table above is the scope-time list. Each built article's checked sources follow; anything absent from them was cut, not softened.

### `kubernetes-scaling-database-connection-budget`

| Claim | Verified |
|---|---|
| HPA automatically updates a workload resource to scale capacity to match demand; horizontal scaling deploys more Pods | verified: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ (intro; "How does a HorizontalPodAutoscaler work?") |
| HPA control loop default interval 15 seconds (`--horizontal-pod-autoscaler-sync-period`) | verified: same page ("How does a HorizontalPodAutoscaler work?") |
| desiredReplicas = ceil(currentReplicas x currentMetricValue / desiredMetricValue) | verified: same page ("Algorithm details") |
| HPA does not exceed the configured maximum | verified: same page ("Scaling on multiple metrics": "provided that this isn't larger than the overall maximum that you configured") |
| Scale-up has no stabilization window by default; up to 4 pods or 100% every 15 s, whichever allows more | verified (rechecked after cold read): same page, "Default behavior" scaleUp block `stabilizationWindowSeconds: 0`, policies Percent 100 / Pods 4, periodSeconds 15, `selectPolicy: Max`; text: "4 pods or a 100% of the currently running replicas may at most be added every 15 seconds"; "Scaling policies": the policy allowing the highest amount of change is selected by default |
| Deployment maxSurge default 25%, rounded up | verified: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ ("Max Surge") |
| max_connections typically 100, set only at server start (PostgreSQL 18 = current) | verified: https://www.postgresql.org/docs/current/runtime-config-connection.html (max_connections) |
| superuser_reserved_connections default 3; reserved_connections default 0; pg_use_reserved_connections; only those roles admitted as slots run low | verified: same page (reserved_connections, superuser_reserved_connections) |
| pg_stat_activity: one row per server process | verified: https://www.postgresql.org/docs/current/monitoring-stats.html (27.2.3 pg_stat_activity, Table 27.1) |
| PgBouncer transaction pooling: server connection assigned only during a transaction | verified: https://www.pgbouncer.org/features.html (pooling modes) |
| Transaction mode does not support SET/RESET, LISTEN, session-level advisory locks | verified: same page (feature map) |
| default_pool_size 20 per user/database pair; max_db_connections default 0 (unlimited); max_client_conn default 100; pool_mode default session | verified: https://www.pgbouncer.org/config.html |
| Kyverno runs as a dynamic admission controller; CLI applies policies to clusters or resource files | verified: https://kyverno.io/docs/introduction/how-kyverno-works/ |
| Gatekeeper is a validating and mutating webhook that enforces CRD-based policies executed by OPA | verified: https://open-policy-agent.github.io/gatekeeper/website/docs/ ("What is Gatekeeper") |
| PostgreSQL "sorry, too many clients already" error text | cut: not found on a postgresql.org primary page; article says "refusing new connections" instead |
| OPA evaluates Terraform plans; Kyverno exceptions/reports; Sentinel levels; CNCF 82%; Gartner 80% | not used in this article (belong to article 2 / optional context) |

Hypothetical figures (labelled in body): 12 max replicas x 12 pool = 144 vs max_connections 100; 97 after 3 superuser-reserved slots; 15 pods / 180 connections during a 25% surge rollout; 8 replicas = 96 fit (consistent with article 2); with surge HPA max 6; pool 8 gives cap 9 including surge (9 + 3 surge = 12 pods = 96). FAQ now compares 144 against 97 available, matching the body. PgBouncer: 3 instances x pool 20 (one user/db pair) = 60 server connections.

### `policy-as-code-engineering-decisions`

| Claim | Verified |
|---|---|
| OPA can evaluate Terraform plans (plan to JSON via `terraform show -json`, passed as input; checks changes before Terraform makes them; some values unknown at plan time) | verified: https://www.openpolicyagent.org/docs/terraform ("Terraform" intro; "2. Convert the Terraform plan into JSON"; "4. Evaluate the OPA policy on the Terraform plan"; "Policy Limitations with Terraform Plans") |
| Kyverno PolicyException lets resources past a given policy and rule; disabled by default; admins set which namespaces may hold exceptions | verified: https://kyverno.io/docs/exceptions/ (intro; "PolicyExceptions for CEL Policies"; enablement flags `enablePolicyException`, `exceptionNamespace`) |
| Kyverno policy reports record pass/fail/warn/error/skip; wg-policy (Kubernetes Policy working group) open format; exception-covered resources report skip, "an applicable PolicyException exists" | verified: https://kyverno.io/docs/policy-reports/ ("Report result logic"; "Scenarios for Skip results"; intro on the Kubernetes Policy working group format) |
| Sentinel enforcement levels advisory / soft-mandatory / hard-mandatory, separate from policy logic; soft-mandatory override provides non-repudiation | verified: https://developer.hashicorp.com/sentinel/docs/concepts/enforcement-levels (Enforcement Levels; Soft Mandatory) |
| HCP Terraform: overriding failed policies requires Manage Policy Overrides permission | verified: https://developer.hashicorp.com/terraform/cloud-docs/workspaces/policy-enforcement/manage-policy-sets (OPA enforcement levels: "any user with Manage Policy Overrides permission can override these failures") |
| OPA metadata annotations include authors, related_resources ("A list of URLs pointing to related resources/documentation"), custom | verified: https://www.openpolicyagent.org/docs/policy-language#annotations (Metadata > Annotations). Added; not in brief. |
| HPA scales pods; PostgreSQL max_connections | not cited directly here; owned by article 1. The 100-connection / pool-of-12 / max-8-replica example is hypothetical and stated as the team's decision. |
| CNCF 82% / Gartner 80% | cut: optional context, not needed for this angle and not verified |
| Azure Policy / landing zones | cut: concept page only per brief |

Aligned with article 1: 100 connections minus 3 superuser slots = 97 usable; 8 pods x 12 = 96 fit; default 25% maxSurge takes 8 to 10 during a rollout, so the policy caps HPA max at 6. Full arithmetic linked to /insights/kubernetes-scaling-database-connection-budget/.

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Forbid a direct database import or dependency in application code (FORBID_DEPENDENCY and path-scoped rules) | SHIPPED (0.10.0). FORBID_DEPENDENCY ignores paths and is repo-wide WARN; confirm the exact rule type and verdict before writing the example |
| Repo-native rules on Terraform / IaC files | SHIPPED only as far as `supported-languages/terraform-governance` documents it; re-verify against that page and the docs before reuse |
| Checking replica × pool counts against a connection budget | CONCEPTUAL (no such rule type) |
| Deployment admission or runtime enforcement | not claimed; that is the job of Kyverno, OPA, Sentinel and similar tools |
| Decision record supplying context to existing policy engines | CONCEPTUAL |
| Decision-linked evidence across layers (which decision, version, rule, verdict) | partly SHIPPED: violations name the rule's decision; cross-layer linkage is CONCEPTUAL |

## Positioning constraints

- Never claim OPA cannot enforce cross-layer constraints or that Kyverno lacks exceptions or evidence.
- Infrastructure and database-migration enforcement are future extensions on the current site; keep them that way.
- "Application and infrastructure governance" is a use case and a research track, not a new category.
- Name no partner, prospect or platform vendor relationship. The strategy answer's market and competitor material stays private.
- Defer any `/solutions/application-infrastructure-governance/` page until a cross-layer experiment is verified (the chat's own gate).

## Non-insight site edits requested

- `concepts/engineering-decision-governance`: a short section on decisions that span applications and infrastructure (concept contract; after phase 1).
- `concepts/policy-as-code`: link to article 2; keep its definition.
- `concepts/architecture-as-code`: link to the implementation piece when it exists.
- `/for/platform/`: expand buyer language only after the technical case is validated.
- The concept page above.

## Open questions

- **Owner decision:** build the infrastructure governance concept page (one page, separate PR, terminology amendment first)? Default if unanswered: hold it until phase 1 ships.
