# Draft integration page — Open Policy Agent (OPA) + Mneme

**Proposed URL:** `/integrations/open-policy-agent/`  
**Classification:** Policy-engine integration target (P1 research); no shipping adapter.  
**Publishing:** This is draft copy, not a page published under `site/`.

**SEO title:** Mneme + Open Policy Agent (OPA): Architecture Decisions and Rego  
**Meta:** Research into using Mneme's reviewed architectural decisions with Open Policy Agent's Rego evaluation and policy distribution interfaces.

## Hero

# Use engineering decisions alongside OPA policies

OPA is a general-purpose policy engine. Mneme maintains authoritative, applicable architectural decisions and deterministic checks within its verified rule coverage. The integration opportunity is a **bounded bridge between decision authority and a policy evaluation engine**, not a claim that ADR prose can be automatically compiled into Rego.

**Status: Under investigation; no supported Mneme–OPA adapter.**

## The integration seam

An enterprise already uses OPA/Rego for API authorization, admission, deployments or infrastructure changes. The architectural decision governing the change belongs in Mneme; execution may happen in a system already asking OPA for an authorization decision.

Two independently testable approaches:

1. **OPA as a downstream enforcement consumer (preferred feasibility route).** An approved Mneme decision with an exact, expressible predicate and pinned target/version is mapped to a reviewed, versioned Rego rule or data input. OPA enforces through its existing host. Prove that authority, lifecycle, waiver scope, conflict precedence, policy freshness and rule equivalence survive that mapping. A separate operator-approved deployment step publishes the policy; Mneme is not a remote policy override engine.
2. **OPA as an additional evaluator.** An adapter might request a decision using OPA's documented Data API (or embedded OPA) for structured inputs and attach its result as evidence to a Mneme-governed workflow. OPA's verdict must not silently replace Mneme's own typed-rule semantics or become a second source of decision authority.

**Example, hypothetical:** A reviewed decision says production deployments must reuse the approved CPU-only inference profile. A narrow Rego admission predicate could check `resource_profile == "cpu-standard"` if the deployment admission API actually receives that attribute. It cannot enforce an unrelated code import rule from that admission input.

## What is not automatically covered

- Natural-language ADR interpretation; semantic code checks absent from Rego's input.
- OPA bundles distributed through another operator without version/approval governance.
- Authority resolution or cross-repository federation outside Mneme's canonical decision model.
- Automatic policy promotion, arbitrary Rego synthesis, or a guaranteed fail-closed deployment gate.

## Evidence to demonstrate

Pin a sample Rego policy, the OPA version, decision/revision, input schema and consuming host. Compare direct OPA-only policy against an explicitly approved Mneme-derived predicate. Test compliant, forbidden, benign, stale-version, expired-waiver, wrong-resource and policy-unavailable cases. Use OPA's documented decision IDs/logging where appropriate but mask confidential request data. Show authorized rollback and how the consumer refuses unsupported/unevaluated cases.

## Integration status / next step

**Research — no package, export command, adapter or supported host yet.** The initial step is a small OPA/Conftest fixture with one unambiguous, reviewed decision and a manually adjudicated policy mapping. Do not present Conftest support as validated solely because it uses OPA.

## Related

- [OPA integration](https://www.openpolicyagent.org/docs/integration)
- [OPA REST API](https://www.openpolicyagent.org/docs/rest-api)
- [OPA bundles](https://www.openpolicyagent.org/docs/management-bundles)
- [OPA decision logs](https://www.openpolicyagent.org/docs/management-decision-logs)
- Mneme: [Policy as Code](/concepts/policy-as-code/); [Decision Index](/docs/decision-index/); [NVIDIA OpenShell integration — draft](./integration-page-draft.md).

**Publication gates:** Claim audit, no implied shipping, proof of selected host predicate, schema and policy/revision binding, existing site OG/sitemap/index/CTA/analytics checks.
