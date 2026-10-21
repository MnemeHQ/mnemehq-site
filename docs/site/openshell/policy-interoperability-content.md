# Policy interoperability: content and integration information architecture

**Status:** content specification, 21 October 2026; no implementation or connector claim.

## Existing site coverage (do not duplicate)

- Canonical **concept**: [Policy as Code](/concepts/policy-as-code/) defines machine-evaluable rules.
- Existing **analysis**: [Programmable AI Policy Is Not Enough for Coding Agents](/insights/programmable-ai-policy-executable-architectural-intent/) explains why architectural intent must become enforceable.
- Existing **runtime** analysis: [Agent Runtime Governance](/insights/agent-runtime-governance/).
- There is **no dedicated policy-engine integration entry** in the current `/integrations/` inventory for Open Policy Agent/Rego, Conftest or an external policy-engine adapter. Do not imply otherwise.

## Content architecture decision

A technical **policy interoperability** page adds value, but it should have its own label and not be positioned as a shipped Mneme integration.

**Proposed URL (conditional):** `/integrations/policy-engines/`  
**Proposed title:** Mneme and Policy Engines: Engineering Decisions, OpenShell and OPA  
**Intent:** how an authoritative architectural decision becomes an enforceable check, including a clear separation of decision source, typed evaluation, sandbox permission policy and optional downstream OPA/Rego enforcement.

Avoid prematurely creating separate `/integrations/opa/`, `/integrations/conftest/` or `/integrations/nvidia-sentry/` product cards. Those imply validated integration to a named engine, which we do not have.

### Proposed user-facing outline

1. **What a policy engine answers:** given structured input and a rule/policy, decide whether an operation satisfies it. OPA/Rego may run in an API gateway or Sentry's DOCA Tower.
2. **What Mneme answers:** which source-reviewed engineering decision applies, with scope/authority/precedence/lifecycle/exception, and which verified typed-rule checks are available for a concrete change.
3. **How OpenShell fits:** sandbox YAML filesystem/process/network/middleware policy; its global policy **replaces** per-sandbox policy while active; its effective policy may also include provider permissions. Policy Prover proves access-boundary properties, not software architecture correctness.
4. **How NVIDIA Sentry fits:** optional hardware enforcement using DOCA Flow, DOCA Tower and OPA/Rego plus DOCA Argus context. Distinguish the runtime policy outcome from an architectural decision.
5. **Integration patterns to test:** (a) Mneme governs a code change at a supported coding seam; (b) a reviewed decision authorizes a control-plane change at an explicit gateway interceptor; (c) a narrowly representable reviewed constraint is translated into an OPA/Conftest check, with parity tests and human approval; (d) OCSF/Sentry security event correlation with decision evidence.
6. **The failure modes:** translating natural language ADR text directly to executable Rego; authority drift; unversioned exceptions; provider-contributed effective access; false blocks; policy bypass; fail-open middleware; lack of an interception point; post-commit logs presented as prevention.
7. **Runnable example only after integration evidence:** provide tested configuration, pinned versions, supported host, input, passing and failing cases, exception validity, error behavior and rollback.
8. **FAQ and comparison:** Mneme vs OPA (complementary roles); Mneme vs OpenShell (architectural decisions vs access policy); OpenShell Policy Prover vs Mneme verified rule (different proofs); NVIDIA Sentry vs Sentry.io (different products).

### Relationship to current content

**Do not create a second policy-as-code concept page.** Link from the canonical concept and existing programmable-policy insight *after* the interoperability page passes validation. The new page should target integration architecture and mapping contracts; it does not replace the conceptual definition.

**Internal link path:** Policy as Code concept → policy interoperability explainer → proposed NVIDIA OpenShell integration → Mneme Decision Index/enforcement documentation.

### Classification and proof gates

| Item | Current status | Earliest public claim |
|---|---|---|
| Mneme canonical decision index / verified typed rules | Shipped to the extent in current released support matrix | State exact released version and enforced rule family |
| OpenShell YAML policy and policy prover | NVIDIA-documented external capability | Cite NVIDIA; do not imply Mneme integration |
| NVIDIA Sentry OPA in BlueField-4 | NVIDIA-documented reference architecture | Cite NVIDIA; hardware optional |
| Mneme + OpenShell interceptor | Hypothesis | After pinned mandatory seam, failure tests, version/target binding |
| Mneme + OPA/Conftest exporter | Hypothesis | After equivalence, bypass/false-block and authority tests |
| Combined evidence stream | Hypothesis | After event identity/correlation, local egress and integrity evaluation |

**Release sequence:** first factual OpenShell architecture reference; next research-labeled OpenShell integration page; policy-engine interoperability page after an inspectable mapping example. Do not divert DG1/CI1/partner pilots.

**References:** [OpenShell Policy Schema](https://docs.nvidia.com/openshell/latest/reference/policy-schema), [OpenShell Policy Prover](https://docs.nvidia.com/openshell/latest/how-it-works/policies/prover), [NVIDIA Sentry + OPA](https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/), [Roadmap issue](https://github.com/MnemeHQ/mneme-growth-ops/issues/73).
