# Insight content-type audit (2026-10-14)

Two reviewers classified all 179 insights blind (without seeing the current label) against the definitions in
`docs/site/insight-publishing-contract.md`. They agreed with the live label on 110 of the 179. This file records the 69 disagreements and what to do with each.

## Tier 1: clear errors to fix (21)

| Article | Now | Proposed | Why |
|---|---|---|---|
| `prompt-engineering-is-not-governance` | Concept | **Perspective** | argues a distinction; defines no term ('X is not governance' series) |
| `rag-is-not-memory` | Concept | **Perspective** | argues a distinction; defines no term |
| `why-claude-md-stops-scaling` | Concept | **Perspective** | argument about limits, not a definition |
| `why-code-review-cannot-scale-with-ai-output` | Concept | **Perspective** | argument, not a definition |
| `why-prompt-memory-fails-at-scale` | Concept | **Perspective** | argument, not a definition |
| `why-rag-fails-for-architectural-governance` | Concept | **Perspective** | argument, not a definition |
| `llm-wiki-library-not-law` | Concept | **Perspective** | argument, not a definition |
| `architectural-governance-across-heterogeneous-ai-coding-agents` | Concept | **Perspective** | argument about cross-tool seams, not a definition |
| `ai-agent-orchestration-is-not-governance` | Analysis | **Perspective** | 'X is not governance' series; no external anchor |
| `artifacts-are-not-governance` | Analysis | **Perspective** | 'X is not governance' series; no external anchor |
| `runtime-verification-is-not-architectural-verification` | Analysis | **Perspective** | 'X is not governance' series; no external anchor |
| `shared-memory-is-not-shared-intent` | Analysis | **Perspective** | 'X is not governance' series; no external anchor |
| `rule-files-vs-retrieval-memory` | Analysis | **Comparison** | title is an explicit X vs Y comparison |
| `ai-agent-governance-two-markets` | Analysis | **Comparison** | 'Runtime vs. Architectural Control' comparison |
| `prompt-engineering-vs-harness-engineering` | Analysis | **Comparison** | compares two approaches |
| `four-architecture-protection-states` | Analysis | **Concept** | defines the four protection states |
| `beyond-security-by-design-governance-by-design` | Analysis | **Concept** | defines Governance by Design |
| `ai-engineering-roi` | Analysis | **Guide** | 'How to Measure' the reader's ROI |
| `ai-native-sdlc-architecture-layer` | Analysis | **Report Response** | responds to Anthropic's AI-native SDLC playbook |
| `latent-space-agent-communication-governance` | Analysis | **Research** | primary object is research on latent-space multi-agent communication |
| `agentic-infrastructure-attack-surface` | Perspective | **Analysis** | anchored on the npm and dev-tooling compromises |

## Tier 2: Analysis or Perspective? (38)

The contract's Analysis definition includes "an argument the article analyses", which overlaps Perspective ("Mneme's own argument"). That overlap is the root cause of most disagreements. Proposed rule: **Analysis needs a named external anchor** (a launch, product, company move, incident, metric, or a named law or person). **Perspective is Mneme's standalone argument.**

Under that rule, these move to Perspective unless marked *anchored*:

| Article | Reviewer's reason | Proposed |
|---|---|---|
| `agent-first-ides-need-architectural-invariants` | General argument about agent-first IDEs needing invariants | **Perspective** |
| `agent-governance-in-the-sdlc` | Argument that orchestration shifts problem to governance; no specific anchor | **Perspective** |
| `ai-coding-agent-verification-tax` | Argument on verification cost; Glean index cited as support | **Perspective** |
| `ai-coding-agents-financial-services-audit-trail` | Vertical argument on audit trails in finance | **Perspective** |
| `ai-coding-agents-life-sciences-governance` | Vertical argument on governance in life sciences | **Perspective** |
| `ai-coding-governance-should-be-reviewable` | Mneme viewpoint on reviewable repo-native governance | **Perspective** |
| `ai-governance-for-regulated-industries` | Cross-vertical argument for governance in regulated industries | **Perspective** |
| `ai-infrastructure-governance-category` | Category argument; no external anchor | **Perspective** |
| `ai-race-wont-be-won-on-infrastructure-alone` | Argues against a general consensus thesis, no specific anchor | **Perspective** |
| `ai-stack-determinism-probabilistic-models` | Standalone thesis on rebuilding determinism | **Perspective** |
| `architectural-drift-cloud-platform-migrations` | Argument on drift across platform migrations | **Perspective** |
| `are-your-adrs-enforceable` | Argument about the enforceable subset of ADRs | **Perspective** |
| `autonomous-code-remediation-requires-architectural-governance` | Standalone argument on remediation loops | **Perspective** |
| `barbara-liskov-python-encapsulation-ai-governance` | Uses Liskov's critique as lens for Mneme argument | Analysis (anchored on a named law, person, metric or event) |
| `brooks-law-ai-coding-agents` | Applies Brooks's Law to AI agents | Analysis (anchored on a named law, person, metric or event) |
| `cloud-agents-need-architectural-governance` | General argument about cloud agents; no specific anchor | **Perspective** |
| `codebase-memory-during-migrations` | Argument why memory goes stale in migrations | **Perspective** |
| `conways-law-ai-coding-agents` | Applies Conway's Law to AI agents | Analysis (anchored on a named law, person, metric or event) |
| `coordination-governance-multi-agent-systems` | Thesis on coordination governance; Lovable only a signal | Analysis (anchored on a named law, person, metric or event) |
| `dora-metrics-insufficient-for-agentic-development` | Argument on DORA limits under agentic development | Analysis (anchored on a named law, person, metric or event) |
| `fde-coding-agents` | Argument on FDEs with coding agents | **Perspective** |
| `forward-deployed-architects-need-a-decision-layer` | Argument for decision layer for FD architects | **Perspective** |
| `forward-deployed-engineering-ai-sdlc` | Argument on FDE context gap in AI SDLC | **Perspective** |
| `forward-deployed-engineering-architecture` | Argument on hidden architecture problem for FDEs | **Perspective** |
| `forward-deployed-engineers-enterprise-ai` | Argument why FDE role is structural | **Perspective** |
| `governance-perimeter-is-moving-to-the-endpoint` | Argument about on-device agents; explicitly not about Gemma | Analysis (anchored on a named law, person, metric or event) |
| `harness-engineering-verification-layer` | Standalone argument that verification is the missing layer | **Perspective** |
| `html-is-not-the-point-structure-is` | Argument about structured outputs; trend, no specific anchor | **Perspective** |
| `long-context-windows-governance-infrastructure` | Argument about long context and RAG, no specific anchor | **Perspective** |
| `loop-engineering-is-not-new` | Historical argument reframing loop engineering | Analysis (anchored on a named law, person, metric or event) |
| `machine-readable-pull-requests-agentic-development` | Mneme argument for machine-readable PRs | **Perspective** |
| `smart-routing-ai-coding-agents` | Argument about routing limits, no specific anchor | **Perspective** |
| `sovereign-ai-needs-sovereign-engineering` | Argument about sovereign AI, no specific anchor | **Perspective** |
| `spec-driven-development-still-needs-governance` | Argument about spec-driven development's gap | **Perspective** |
| `verification-starts-before-generation` | Standalone argument for pre-generation verification | **Perspective** |
| `when-ai-agents-degrade-architectural-intent-should-not` | Proposes intent-preserving degradation principle | **Perspective** |
| `why-ai-coding-agents-copy-legacy-architecture` | Explanatory argument about migration failure mode | **Perspective** |
| `why-context-alone-doesnt-prevent-architectural-drift` | Argument context is not governance | **Perspective** |

## Reviewed and kept

| Article | Reviewer suggested | Decision |
|---|---|---|
| `enforce-engineering-standards-across-ai-assisted-teams` | Guide | kept as Analysis per the owner's #205 decision (not actionable enough for Guide) |
| `adrs-for-software-migrations` | Concept | Guide: it tells a team how to structure migration ADRs |
| `package-hallucinations-pre-action-governance` | Research | Analysis: the study is supporting evidence; the argument about pre-action control is the object |
| `runtime-harnesses-for-ai-agents` | Research | Analysis: 'a growing body of research', no single paper as the object |
| `agentic-workforce-visibility-crisis` | Analysis | Perspective (reviewer low confidence) |
| `review-is-not-governance` | Comparison | Perspective, consistent with the 'X is not governance' series |
| `ai-coding-agent-architecture` | Concept | Analysis (reference-frame explainer; Concept is arguable) |
| `generative-ai-software-engineering-stack` | Concept | Analysis (reference-frame explainer; Concept is arguable) |
| `enterprise-ai-guardrails-five-layers` | Concept | Analysis: extends IBM's framework |
| `loop-engineering-ai-coding-agents` | Concept | Analysis: anchored on the loop-engineering trend |
