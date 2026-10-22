# Draft integration page — NVIDIA Sentry + Mneme

**Proposed URL:** `/integrations/nvidia-sentry/`  
**Classification:** Hardware-isolated policy enforcement and evidence integration target (P2 exploration, gated on NVIDIA availability and a documented extension contract).  
**Publishing:** Editorial draft, not in `site/` and not a shipped integration. NVIDIA's October 2026 information describes planned Sentry availability in early 2027.

**SEO title:** Mneme + NVIDIA Sentry: Decision Context for Hardware-Enforced Agent Security  
**Meta:** Explore future integration of Mneme engineering decisions with NVIDIA Sentry's BlueField-4, DOCA Tower/OPA and trusted runtime evidence.

## Hero

# Engineering decision context for NVIDIA Sentry

NVIDIA Sentry monitors and enforces AI-agent access from a BlueField-4 hardware-isolated domain. Mneme makes reviewed engineering decisions, their scope, authority, revisions and exceptions explicit. **A direct integration has not been implemented or validated.**

**Status: Future integration research, subject to access and published SDK/DOCA contracts.**

## Where Sentry fits

Sentry is not Sentry.io. It combines DOCA Flow L4 filtering, DOCA Tower application-layer traffic inspection and OPA/Rego access decisions, DOCA Argus runtime/memory context, and independent hardware containment. It is part of NVIDIA's expanded reference architecture and can complement software-only OpenShell sandboxes.

Crucially, **OPA as an independent policy-engine integration** and **Sentry as a downstream protected runtime/hardware surface** are separate integrations. A working Mneme–OPA experiment does not prove Mneme–Sentry support.

## Proposed integration seams

1. **Policy consumption, conditional:** Map one human-approved architectural decision about external API/tool/resource access to an exact OPA-consumable access predicate, only if NVIDIA documents and exposes the requisite DOCA Tower policy/extension contract. Sentry remains responsible for enforcement within BlueField; Mneme owns decision authority upstream. No automatic natural-language-to-Rego conversion.
2. **Runtime context back to Mneme evidence, conditional:** Correlate authorized Sentry/DOCA security events with Mneme's decision/rule revision and target ID. Verify stable correlation fields, privacy, retention, timing and attestation, rather than assuming the streams link by default.
3. **Threat and policy violation feedback:** If legitimate extension interfaces expose detections, differentiate a Sentry threat block from a Mneme architectural conformance block. One is not a substitute for the other.

## Proving the integration

Before claiming any compatibility, confirm Sentry's released hardware/software availability, accessible documented extension interface, DOCA Tower/OPA policy input schema, scope of interception and telemetry API. Then evaluate a toy unauthorized external resource request and a compliant control; test stale revision, unsupported resource, failure mode, waiver scope and policy rollback. Never claim semantic source-code checks inside Sentry unless the necessary artifact contents and rule semantics are actually available.

## Explicit limitations

Sentry cannot be treated as a generic plugin slot for Mneme. DOCA/Envoy extensibility is promising but does not demonstrate a particular safe deployment or enforcement contract. BlueField hardware and security operating privileges are required for a production-representative experiment. Agent file mutation still needs a supported coding seam or separate CI; network-policy blocks do not prove source architecture conformance.

## Related

- [NVIDIA Sentry](https://www.nvidia.com/en-us/networking/products/software/sentry/)
- [NVIDIA Sentry technical deep dive](https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/)
- [NVIDIA OpenShell architecture](https://developer.nvidia.com/blog/how-nvidia-openshell-reference-architecture-secures-and-governs-ai-agent-workloads-at-scale/)
- [OPA integration](https://www.openpolicyagent.org/docs/integration)
- Mneme: [Enforcement overview](/docs/how-enforcement-works/); [Policy as Code](/concepts/policy-as-code/).

**Publication gates:** External-claim review, vendor availability check, technical proof, existing site page registration and claim-level/support-status checks. No NVIDIA partner or certification claim.
