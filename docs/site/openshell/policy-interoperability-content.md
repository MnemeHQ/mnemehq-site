# OPA + NVIDIA Sentry: separate integration tracks, not generic policy content

**Corrected scope:** 22 October 2026. The intended third deliverable is an **integration layer** connecting Mneme with **Open Policy Agent (OPA)** and **NVIDIA Sentry** as two distinct integration targets. It is **not** a generic policy-engine explainer or one combined `/integrations/policy-engines/` page.

## Integration information architecture

| Target | Proposed site URL | Distinct target outcome | Priority | Current status |
|---|---|---|---|---|
| NVIDIA OpenShell | `/integrations/nvidia-openshell/` | Integrate reviewed decisions at an actual OpenShell tool/gateway mutation seam; correlate evidence | P1 research | Unimplemented |
| **Open Policy Agent (OPA)** | `/integrations/open-policy-agent/` | Map exact, human-approved decision constraints into an operator-approved Rego/OPA policy at an existing admission/API gate; alternatively consume OPA evaluation and versioned decision logs without creating a second decision authority | **P1 research** | Unimplemented |
| **NVIDIA Sentry** | `/integrations/nvidia-sentry/` | Evaluate a supported DOCA Tower/OPA policy input/plugin seam and correlate hardware-isolated telemetry to Mneme decision evidence, where NVIDIA makes those interfaces accessible | **P2 gated research** | Unimplemented; NVIDIA describes Sentry planned availability in early 2027 |

These target distinct artifacts and technical proofs. A Mneme–OPA adapter does **not** establish NVIDIA Sentry compatibility. An OpenShell sandbox configuration is **not** an OPA adapter. NVIDIA Sentry is not the unrelated Sentry.io service.

The detailed research-only page drafts are [OPA integration](./opa-integration-page-draft.md), [NVIDIA Sentry integration](./nvidia-sentry-integration-page-draft.md), and [OpenShell integration](./integration-page-draft.md). The sourced NVIDIA/OpenShell technical architecture is [reference architecture](./reference-architecture.md).

## Proposed layer: decision authority → policy adapters → enforcement surfaces

```text
Human-approved engineering decision
    ↓ Mneme canonical Decision Index
    ↓ scope, lifecycle, precedence, waiver, rule revision
┌───────────────────┬────────────────────────────┐
│ Mneme typed checks│ Policy adapters (research) │
│ code/CI where real│ OPA/Rego projection OR      │
│ seam is supported │ structured OPA evaluation  │
└───────────────────┴────────────────────────────┘
    ↓                             ↓
Coding agent + CI        Existing OPA-consuming gate
                               ↓ if independently supported
                        NVIDIA Sentry/DOCA Tower/OPA
                        (BlueField-4 isolated enforcement)
    ↘ evidence from each actually observed enforcement seam ↙
        decision-linked, revision-pinned, with UNEVALUATED gaps
```

**Important:** This is *proposed architecture*, not an implemented unified pipeline. Mneme remains the decision authority; OPA evaluates structured Rego policies; Sentry enforces security policies in its own trusted hardware domain. Do not automatically generate or activate Rego from ADR text. Authoritative rule identity and policy semantics must be preserved by a human-reviewed, equivalence-tested adapter.

## OPA integration — phase 1 (P1)

1. Pick a pinned OPA version and existing, reproducible policy consumer: a disposable admission/API gate or a small Conftest fixture. Identify which request fields the gate actually receives.
2. Choose one reviewed Mneme decision expressible using those fields; document predicate, scope, explicit exception, expected rule revision and policy freshness requirements.
3. Implement *only a proposed, manually reviewed mapping* to one Rego policy OR an OPA evaluation adapter. Do not claim any current Mneme exporter.
4. Test compliant, violating, benign, wrong target, stale policy, unsupported input, expired waiver and unavailable OPA. Fail closed where the selected host promises enforcement; otherwise classify UNEVALUATED/advisory.
5. Correlate OPA `decision_id`, bundle/revision and masked decision log with Mneme's decision/evidence identity. Respect sensitive input redaction and local execution requirements.

**Promotion:** working adapter with exact supported host, decision/policy equivalence testing, safe upgrade/rollback and evidence chain; otherwise research only.

## NVIDIA Sentry integration — phase 2 (P2, hardware/access gate)

1. Establish actual Sentry release/availability, access to the required BlueField-4/DOCA environment and documented policy/plugin or telemetry extension API.
2. Understand which OPA/Rego policy input Sentry exposes through DOCA Tower and how it relates to OpenShell policies. No assumption that a generic OPA REST endpoint or user-defined plugin is exposed in the same way.
3. Test one reviewed, *access-oriented* architectural decision on a supported external API/tool request and compliant control. Sentry blocks or permits at its hardware enforcement boundary, not at Mneme's source-code write seam.
4. Correlate permitted Sentry event streams and versioned, authorized policy deployment with Mneme enforcement evidence. Include missing metadata, bypass, latency, privacy, policy update/rollback and containment failure modes.
5. No supported integration, certification, partnership, shipped adapter or hardware policy projection claim until real evidence exists.

## Editorial placement and dependencies

- **OPA** and **NVIDIA Sentry** deserve **separate integration pages**, both labeled research/unavailable until proof. The broader "policy interoperability" narrative belongs as an explanatory section on these pages, not as a substitute for the integration targets.
- Crosslink the factual OpenShell architecture/integration with OPA and NVIDIA Sentry once those pages are built. Place all three in an explicitly marked research group, *not* the site's native/validated integrations group.
- Link to the existing [Policy as Code](/concepts/policy-as-code/) concept and [Programmable AI Policy Is Not Enough for Coding Agents](/insights/programmable-ai-policy-executable-architectural-intent/) without creating another conceptual duplicate.
- Implement site template, OG manifest/image, canonical, sitemap, schema, navigation, claim audit and copy gates separately for each public page.
- Technical priority remains real pilots, DG1 convergence and CI1 assurance first; adapter investigations must not become a second Mneme policy authority or displace them.

## External references

- [OPA integration overview](https://www.openpolicyagent.org/docs/integration)
- [OPA REST evaluation API](https://www.openpolicyagent.org/docs/rest-api)
- [OPA policy bundles](https://www.openpolicyagent.org/docs/management-bundles)
- [OPA decision logs](https://www.openpolicyagent.org/docs/management-decision-logs)
- [NVIDIA Sentry / DOCA Tower](https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/)
- [NVIDIA reference architecture](https://nvidianews.nvidia.com/news/openshell-reference-architecture)
- [Private integration research intake](https://github.com/MnemeHQ/mneme-growth-ops/issues/73)
