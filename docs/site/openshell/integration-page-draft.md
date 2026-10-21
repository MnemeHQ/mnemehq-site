# Page draft: Mneme + NVIDIA OpenShell

**Proposed URL:** `/integrations/nvidia-openshell/`  
**Page type:** Integration — planned/research, not validated.  
**Indexing/publication gate:** Keep as an editorial **draft** until independent source/claim audit and site publication checks pass. If published before an adapter exists, lead with **Integration research — not a shipped connector**, omit install commands and do not group under 'native/validated' on the integrations hub.

**Suggested SEO title:** NVIDIA OpenShell and Mneme: Runtime Policies vs Architecture Decisions  
**Meta description:** Explore how NVIDIA OpenShell sandbox policies and Mneme architectural decisions might work together. Research-stage integration, supported boundaries and evidence still under evaluation.  
**Primary search intent:** NVIDIA OpenShell integration; OpenShell policy governance; AI agent runtime architecture.

## Hero

# Architectural decisions for agents running in NVIDIA OpenShell

OpenShell controls what an AI agent can access. Mneme records which engineering decisions apply to the code and infrastructure that agent changes. Their enforcement boundaries can complement one another, but **a Mneme–OpenShell integration has not yet been validated or released**.

**Status:** Research / planned compatibility test.  
**CTA:** [Explore Mneme's verified enforcement surfaces](/docs/how-enforcement-works/)  
**Secondary:** [NVIDIA OpenShell docs](https://docs.nvidia.com/openshell/latest/).

## What OpenShell already enforces

OpenShell isolates workloads and applies kernel, filesystem and network restrictions outside the agent process. Its gateway manages sandbox state and policy; its policy prover checks modeled access boundaries. Gateway interceptors can approve or deny **selected** configured control-plane API mutations. A separate supervisor middleware interface can operate on permitted HTTP and WebSocket traffic.

These are genuine policy-enforcement capabilities. Mneme is **not** proposing to replace them.

## Where architectural decisions differ

A sandbox might legitimately allow writing to `src/handlers/`. That permission cannot tell you whether an edit violates the project decision to access persistence only through a storage adapter.

Mneme's intended role is to resolve the applicable, reviewed engineering decision, use a verified typed rule at a supported mutation boundary, and link the outcome to the decision and its revision. Merely retrieving an ADR is not enforcement; the relevant rule must be expressible and evaluated against the actual change.

## Integration architecture under investigation

1. The coding agent operates in an OpenShell sandbox, constrained by native OpenShell policy.
2. Mneme's existing agent hook or a future supported host adapter evaluates a code mutation **only where the actual proposed bytes can be intercepted**.
3. A future gateway interceptor may evaluate relevant **allowlisted OpenShell control-plane API writes** against reviewed decisions, without replacing OpenShell authentication or persistence.
4. CI independently checks supported final code artifacts. Evidence relates a decision/rule revision, target, attempted mutation, enforcement seam, verdict and limitations.

This is a **proposed sequence**, not a tested product workflow.

## Three decision boundaries to understand

| Question | Who can answer it? |
| --- | --- |
| Can this process write to the workspace or reach the API? | OpenShell's policy, sandbox and proxy |
| Does the proposed code change respect a reviewed architectural decision? | Mneme typed evaluation, where supported; otherwise UNEVALUATED |
| Does the effective policy or agent behavior justify a hardware-level block? | Optional NVIDIA Sentry on BlueField-4, where deployed and configured |

NVIDIA Sentry (not Sentry.io) can evaluate access via DOCA Tower/OPA and enforce within the BlueField hardware security domain. No direct Mneme → Sentry policy adapter is claimed.

## What we plan to test

Two reviewed decisions in a disposable service: preserve the approved storage adapter, and preserve the existing compute/model profile. Compare an OpenShell-only baseline with OpenShell plus Mneme at **real supported seams**. Report compliant and forbidden edits, false blocks, bypasses, policy and target freshness, and unsupported requests. Confirm whether gateway operation interception is relevant before claiming infrastructure gate coverage.

**Pass condition:** measured additional decision conformance without compromising functional completion or disguising post-hoc detection as pre-action enforcement.

## FAQ

**Does Mneme replace OpenShell policies?** No. OpenShell enforces access to files, processes, network destinations and supported API operations. Mneme supplies application-specific architectural decision authority and its own bounded checks.

**Can Mneme directly enforce all OpenShell tool calls?** No evidence supports that claim. Gateway interceptors apply only to explicitly allowlisted unary mutation RPCs. Coding file writes need a separately validated mutation seam or CI detection.

**Does OpenShell include NVIDIA Sentry?** Sentry is a hardware-isolated optional layer in NVIDIA's reference architecture, running on BlueField-4. The OSS OpenShell runtime is usable without that hardware.

**Is there a ready-to-install Mneme connector?** Not yet. This page describes a proposed integration that needs testing.

**How does this relate to policy-as-code?** Access policies and reviewed architectural decisions are different objects. See [Policy as Code](/concepts/policy-as-code/) and [Programmable AI Policy Is Not Enough for Coding Agents](/insights/programmable-ai-policy-executable-architectural-intent/).

## Sources and related reading

- [NVIDIA Reference Architecture](https://nvidianews.nvidia.com/news/openshell-reference-architecture)
- [OpenShell Gateway Interceptors](https://docs.nvidia.com/openshell/latest/extensibility/gateway-interceptors)
- [OpenShell Sandbox Policies](https://docs.nvidia.com/openshell/latest/how-it-works/policies/overview)
- [NVIDIA Sentry technical explanation](https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/)
- [Mneme enforcement overview](/docs/how-enforcement-works/)
- [Mneme MCP integration](/integrations/mcp/)

## Publishing gates / handoff

- Independently check every claim against current pinned OpenShell documentation and released Mneme support matrix.
- Reproduce one actual supported seam before any 'compatible' or 'supported' label; otherwise maintain research status.
- Apply the site integration-page template, shared header/footer, CTA tagging, canonical URL, accessibility, analytics, schema, localized OG image/manifest, sitemap registration and the correct **research** card in the integrations hub.
- Run the claim audit, stop-slop cold read, prose lint and site CI; **never add this to the 'native and validated' integration group before proof**.
