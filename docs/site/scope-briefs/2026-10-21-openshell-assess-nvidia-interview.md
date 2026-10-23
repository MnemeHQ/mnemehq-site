# Scope brief: Post- OpenShell Assess NVIDIA Interview

Status: **published 2026-10-22** in [#238](https://github.com/MnemeHQ/mnemehq-site/pull/238) as `/insights/nvidia-openshell-reference-architecture-agent-policy/`; deployed at `c6c1ed46`

| Field | Value |
|---|---|
| ChatGPT chat | `Post- OpenShell Assess NVIDIA Interview` (space after the hyphen) |
| Created / last updated (UTC) | 2026-10-21 / 2026-10-22 |
| Shape | 4 user turns: assess an AI Magazine interview with NVIDIA CTO Michael Kagan; update the roadmap; document the NVIDIA OpenShell architecture and an integration page; then a correction that OPA and NVIDIA Sentry are integration targets in their own right. Read in full 2026-10-22; no collapsed turns (completeness check passed). The first answer proposed two insights; the later turns moved the integration work into [#232](https://github.com/MnemeHQ/mnemehq-site/pull/232) (drafts under `docs/site/openshell/`) and [#233](https://github.com/MnemeHQ/mnemehq-site/issues/233) (publishing three integration pages). |
| Repo check | No insight covers OpenShell, Landlock, the policy prover, BlueField or NVIDIA Sentry. The runtime-vs-architecture thesis is already argued in `ai-agent-governance-two-markets` (2026-05-30), `zero-trust-for-ai-agents-architectural-governance` (2026-06-01), `agent-runtime-governance` (2026-05-28) and `beyond-security-by-design-governance-by-design`. `nvidia-nemo-agent-toolkit-engineering-governance` (2026-06-30) is the existing NVIDIA entry point. |

## Decisions (2026-10-22, TheoV823)

- **Build one insight, re-angled** onto the OpenShell reference architecture as a named-source entry point, instead of the chat's generic "AI Agent Security Is Not the Same as Architecture Governance". That generic thesis is shipped; this article contributes the specifics of what OpenShell's policy model does and does not cover.
- **Drop** "Who Governs the AI Factory?": it scores 88.7 against `software-factory-governance-layer` and 60.0 against `nvidia-nemo-agent-toolkit-engineering-governance`. The chat itself warns that NVIDIA's "AI factory" (producing inference) and a software factory (producing software) are different markets.
- **Integration pages stay in #232/#233** (OpenShell, OPA, NVIDIA Sentry; integrations contract). The insight does not pre-empt them: no link to `/integrations/nvidia-openshell/` unless that page has shipped by build time.

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | NVIDIA OpenShell Reference Architecture: Agent Access Policy Is Not Architecture Governance (confirm NVIDIA's verbatim name at verification) |
| Slug | `nvidia-openshell-reference-architecture-agent-policy` |
| Report-anchored (ADR-015) | yes: entity = "NVIDIA OpenShell Reference Architecture" (announced 2026-10-21), verbatim |
| Topic hub | agent-infrastructure |
| Content type (`--type`) | Analysis (named launch in the title) |
| OG headline | NVIDIA OpenShell: Access Is Not Architecture (6 words; leads with the entity) |
| Editorial gate | pass: named-source entry point (NVIDIA OpenShell reference architecture, a timely launch with ecosystem partners) plus new evidence for the runtime-vs-architecture thesis (a concrete, documented policy model to compare against) |
| Five questions | changed: NVIDIA shipped a reference architecture that combines a sandboxed agent runtime, a policy prover and optional hardware enforcement (NVIDIA Sentry on BlueField-4), and positions it as agent governance; matters: platform teams will treat "the agent runs in OpenShell under a proven policy" as governed; breaks: an agent allowed to write `src/handlers/` can still add a direct database dependency the architecture forbids, because access policy says what may be touched, not what a change must respect; do: use runtime policy for access, keep architectural decisions separate with their own authority and enforcement, and test which boundary catches which violation; governance: decision-aware checks at the code-change and CI boundaries complement runtime access control, and OpenShell's extension points (gateway interceptors, supervisor middleware, OCSF export) are where the two could meet |
| Cannibalisation | `find_overlap.py`: `nvidia-nemo-agent-toolkit-engineering-governance` 53.7 (different NVIDIA product, workflow optimization, not runtime policy), `programmable-ai-policy-executable-architectural-intent` 29.7, `policy-as-code-engineering-decisions` 25.5 (batch 4). Body grep: no page mentions OpenShell's components. Verdict: **re-angle, clear on that angle**: the specific OpenShell policy model (filesystem, process, network, API; global policy replacing sandbox policy; prover over modeled access) set against architectural decisions. Link `ai-agent-governance-two-markets` and the zero-trust piece for the general argument; do not restate them. |
| Cross-links | `ai-agent-governance-two-markets`, `zero-trust-for-ai-agents-architectural-governance`, `nvidia-nemo-agent-toolkit-engineering-governance`, `policy-as-code-engineering-decisions`, `concepts/runtime-governance` |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 37 (8/7/7/7/8) |
| `lint_prose.py` (built page) | 0 errors; 3 warnings kept: NVIDIA, IBM and GTC are company and event names |
| Cold read: thesis as restated | OpenShell's sandbox, supervisor and prover control what an agent can access, not whether an allowed change breaks an architectural decision, so that check belongs at the write step and in CI. Matches. |
| Cold read: unclear terms, and how resolved | First pass: GTC, providers, gRPC/interceptor jargon, typed rule, FORBID_LITERAL, strict mode, agent names, Mneme introduced late; all defined or cut; superlatives and "draws the line itself" corrected. Built-page pass: PASS; Architecture Audit CTA glossed. |

**Pre-merge Opus audit (2026-10-22):** 2 blockers and 3 should-fix, all fixed: the Kiro gloss now names Kiro CLI 3.0 native write tools (the IDE is unvalidated); "every write" replaced with "each supported agent write"; the OpenShell + OpenCode work described as draft design documents with nothing implemented (no prototype mention); the meta description no longer says the architecture "proves" access across "policy areas"; "early next year" pinned to early 2027. Every NVIDIA fact and the Kagan quote re-verified against the live sources.

## Agreed scope

- **Thesis:** security platforms control what an agent can access; architectural decisions govern what its changes must respect. OpenShell makes the first rigorous (default-deny egress, a supervisor outside the agent process, an SMT-based prover over modeled access), and that rigor does not reach the second.
- **Structure (proposed):**
  1. What NVIDIA announced: the reference architecture (gateway, sandbox, supervisor and policy proxy, policy prover, optional NVIDIA Sentry on BlueField-4), the partner list (with the caveat that being named is not production adoption), and the Kagan interview's framing as context.
  2. What OpenShell policy actually governs: filesystem, process identity, network destinations, protocol-level API permissions. Which settings are static at sandbox creation and which update live. A gateway-wide global policy replaces sandbox policy rather than bounding it. What the prover proves (modeled access permissions) and what it does not (application architecture, business logic).
  3. The gap, shown with one example: the sandbox permits writing `src/handlers/`; the decision "handlers use the approved storage adapter" is violated by an allowed write. A second example: an unauthorized resource allocation through an otherwise permitted deployment API; say which OpenShell policy or middleware could catch it, and where it could not.
  4. Where the two could meet: gateway interceptors (allowlisted unary write RPCs only; `post_commit` cannot deny), supervisor middleware (HTTP/WebSocket, after the access policy), OCSF event export for evidence. None of these is a universal file-write seam.
  5. What platform teams should do: keep access policy and architectural decisions as separate artifacts with separate owners; map which boundary enforces which decision; test violations at each boundary before assuming coverage.
  6. Where Mneme fits: shipped code-change and CI enforcement of typed rules; any OpenShell, OPA or Sentry adapter is research, not shipped.
- **Testable principle from the chat (usable):** faster AI development needs verification and enforcement that scale with the rate of change. Present Kagan's "speed makes AI safer" view as his opinion; do not argue with it at length.
- **NVIDIA Sentry is not Sentry.io.** Say so once if Sentry is mentioned.
- About 1,400-1,700 words.

## Key facts, figures, sources

Candidate URLs come from the chat and the #232 draft (`docs/site/openshell/reference-architecture.md`, reviewed by its author on 2026-10-21). None is verified for this article yet.

| Claim | Source URL | Verified? |
|---|---|---|
| NVIDIA announced the OpenShell Reference Architecture on 2026-10-21 | https://nvidianews.nvidia.com/news/openshell-reference-architecture | unverified |
| Components: gateway, sandbox, supervisor/policy proxy, policy prover; optional NVIDIA Sentry on BlueField-4 | https://developer.nvidia.com/blog/how-nvidia-openshell-reference-architecture-secures-and-governs-ai-agent-workloads-at-scale/ | unverified |
| Organizations named as working with the architecture include Anthropic, IBM, Microsoft, Siemens, OpenAI and cybersecurity vendors | NVIDIA newsroom (same) | unverified; state as "named by NVIDIA", not adoption |
| Sandbox policy (YAML version 1): filesystem, Landlock, process, network, middleware; filesystem/Landlock/process static at creation, network/middleware dynamic; default-deny egress | https://docs.nvidia.com/openshell/latest/how-it-works/policies/overview , https://docs.nvidia.com/openshell/latest/reference/policy-schema | unverified |
| A gateway-wide global policy replaces sandbox policies while active (as of v0.1.5) | same | unverified; pin the version |
| Policy prover: SMT-based proof over modeled access permissions | https://docs.nvidia.com/openshell/latest/how-it-works/policies/prover | unverified |
| Gateway interceptors: external gRPC extension for allowlisted unary write RPCs; `modify_operation`, `validate`, observational `post_commit` | https://docs.nvidia.com/openshell/latest/extensibility/gateway-interceptors | unverified |
| Supervisor middleware (HTTP/WebSocket) and OCSF event export | https://docs.nvidia.com/openshell/latest/extensibility/overview | unverified |
| NVIDIA Sentry: BlueField-4, DOCA Tower (Envoy-based, uses OPA/Rego), DOCA Argus | https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/ | unverified |
| Kagan interview, AI Magazine, 2026-10-15 (AI factories as infrastructure; open and proprietary models; on-premises inference; agents need sandbox guardrails; accelerating AI makes it safer) | https://aimagazine.com/interviews/the-ai-interview-michael-kagan-cto-at-nvidia | unverified |

**Verified record (2026-10-22).** The table above is the scope-time list; the built article's checked sources follow.

| Claim | Source URL | Verified? |
|---|---|---|
| NVIDIA announced the "NVIDIA OpenShell Reference Architecture" on 2026-10-21 | https://nvidianews.nvidia.com/news/openshell-reference-architecture | verified: https://nvidianews.nvidia.com/news/openshell-reference-architecture (headline "NVIDIA Launches OpenShell Reference Architecture for Safe AI Agents", dateline GTC Berlin, October 21, 2026; verbatim entity "NVIDIA OpenShell Reference Architecture") |
| Components: gateway, sandbox, supervisor, policy prover; Sentry on BlueField-4 optional | developer blog | verified: https://developer.nvidia.com/blog/how-nvidia-openshell-reference-architecture-secures-and-governs-ai-agent-workloads-at-scale/ (section "OpenShell provides deterministic governance outside of the agent's reach"; "optional hardware safeguard" in "NVIDIA BlueField and NVIDIA Sentry for hardware-enforced protection"). Changed from brief: NVIDIA lists "Supervisor", not "supervisor/policy proxy"; article uses "supervisor". Press release also lists Vera CPUs and Vera Rubin. |
| Organizations named: Anthropic, IBM, Microsoft, Siemens, OpenAI, cybersecurity vendors | newsroom | verified: newsroom page ("are among those working with the OpenShell Reference Architecture"; cybersecurity vendors "are integrating support"). Stated as NVIDIA's list, not adoption. |
| Sandbox policy version 1: five sections; filesystem/landlock/process static, network_policies/network_middlewares dynamic; default-deny egress | policies overview, policy schema | verified: https://docs.nvidia.com/openshell/latest/how-it-works/policies/overview (v0.1.5; section table and "OpenShell denies every outbound connection ... unless a rule in network_policies allows it"). Policy-schema page not separately fetched; the overview carried every fact used. |
| Global policy replaces sandbox policies while active; precedence; providers add rules to effective policy | same | verified: same page (v0.1.5; global policy, precedence list, providers). Pinned to v0.1.5 in body and FAQ. |
| Base vs effective policy commands (`openshell policy get <sandbox> --base` / `--full`; both show the global policy while one is active) | manage policies | verified: https://docs.nvidia.com/openshell/latest/how-it-works/policies/manage-policies ("Inspect the Current Policy"; latest = v0.1.5 default). Added at cold read. |
| Policy prover: SMT-based, checks modeled access against boundary | prover page | verified: https://docs.nvidia.com/openshell/latest/how-it-works/policies/prover (v0.1.5; "uses an SMT solver"; five modeled parts; unsupported for GraphQL/MCP; pass does not mean narrowest, safe for a task, or enforced). Changed from brief: the page does not mention "business logic" or "application architecture"; the article attributes only the stated limits to NVIDIA and makes the architecture point in its own voice. |
| Gateway interceptors: allowlisted unary mutation RPCs; modify_operation, validate, post_commit (cannot deny) | interceptors page | verified: https://docs.nvidia.com/openshell/latest/extensibility/gateway-interceptors (v0.1.5; "Only explicitly allowlisted unary mutation RPCs are interceptable"; post_commit cannot deny or modify a committed operation). Specific RPC names not used (not confirmed on page text returned). |
| Supervisor middleware (HTTP/WebSocket, after policy, before credentials) | extensibility overview | verified: https://docs.nvidia.com/openshell/latest/extensibility/overview (v0.1.5; four extension points). |
| OCSF event export | extensibility overview | verified on a different page: https://docs.nvidia.com/openshell/latest/observability/logging (v0.1.5; "maps sandbox events to OCSF v1.8.0 event classes"; ocsf_json_enabled JSONL export for SIEM). The extensibility overview does not mention OCSF. |
| NVIDIA Sentry: BlueField-4, DOCA Tower (Envoy, OPA/Rego), DOCA Argus; availability | Sentry blog | verified: https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/ (Oct 21, 2026; Tower on Envoy with OPA/Rego; "planned availability early next year"). Article uses Tower/OPA and timing only; Argus/Flow not needed. |
| Kagan interview, AI Magazine, 2026-10-15 | AI Magazine | verified: https://aimagazine.com/interviews/the-ai-interview-michael-kagan-cto-at-nvidia (dated October 15, 2026, by Tom Chapman; section "The AI safety debate"; quote "You need to accelerate AI development to make it safe."; OpenShell described as a sandbox where you specify what is and is not allowed). WebFetch returned 403; read via curl with a browser user agent. |
| Mneme OpenShell + OpenCode reference integration (coordinator correction) | MnemeHQ/mneme #609, #610 | verified: `gh pr view` both draft, open, docs-only; #609 says OpenShell not marked shipped; #610 records prototype evidence on an unpushed experiment branch. Classed PLANNED; no results cited. |

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Typed-rule enforcement at supported agents' built-in write tools and in CI | SHIPPED (0.10.0), with the per-agent shell-write limits found in the batch 4 audit (Claude Code and Codex CLI check shell writes at end of turn; other agents rely on CI) |
| Decision Index: versions, lifecycle, source; no approver identity | SHIPPED (0.10.0) |
| Mneme evaluator behind an OpenShell gateway interceptor or supervisor middleware | CONCEPTUAL (research; no adapter implemented) |
| OpenShell + OpenCode file-write example integration | PLANNED: proposed in draft design documents in the open-source repository; nothing implemented or supported |
| Mapping OpenShell OCSF events to Mneme enforcement evidence | CONCEPTUAL |
| Mneme to OPA/Rego, or to NVIDIA Sentry, policy translation | CONCEPTUAL (an unvalidated research hypothesis, per the #232 draft) |
| Mneme running inside an OpenShell sandbox | not claimed (untested) |

## Positioning constraints

- Not a takedown. Credit OpenShell's rigor, and do not claim it cannot gain architectural decision features: the boundary is current documented scope, not a permanent limit.
- Do not merge "AI factory" with "software factory".
- No partnership, design-partner, investor or roadmap-issue references. The chat's roadmap items and experiment plans are tracked privately.
- Keep "decision layer" in its 2026-09-11 thesis sense, and "engineering decision governance" linked, not redefined.
- Coordinate with #232/#233: the insight argues the distinction; the integration pages document the research. Neither claims a working integration.

## Non-insight site edits requested

All in [#232](https://github.com/MnemeHQ/mnemehq-site/pull/232) / [#233](https://github.com/MnemeHQ/mnemehq-site/issues/233): OpenShell reference-architecture documentation, `/integrations/nvidia-openshell/`, `/integrations/open-policy-agent/`, `/integrations/nvidia-sentry/` (all research-status pages). Not part of the insights batch.

## Open questions

- Ship the insight before or after the integration pages? Default: insight first, with no integration-page links; add reciprocal links when #233 publishes.
- Close-out: the chat can be marked `***` once this insight deploys (owner decision 2026-10-22 to mark chats even with other open items; #232/#233 carry the rest).
