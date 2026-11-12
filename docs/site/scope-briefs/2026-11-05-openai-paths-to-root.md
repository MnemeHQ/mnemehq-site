# Scope brief: Post-Openai vulnerability fixes Assess research findings

Status: **gathered, not built**

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Openai vulnerability fixes Assess research findings` |
| Created / last updated (UTC) | 2026-11-05 / 2026-11-05 |
| Shape | 3 user turns: assess the research; add to the roadmap; scope an article and capture SEO intent. The last turn proposes an evergreen guide, which the repo check below overturns. |
| Repo check | `/use-cases/ci-governance-for-ai-generated-code/` (overlap 73.8 to 102.7), `ai-coding-agent-verification-tax`, `/concepts/agent-verification/` (52.1) and `claude-code-review-trusted-decision-boundary` already cover verification and CI checks. No page mentions the OpenAI research. |

## Build card

| Field | Value |
|---|---|
| Kind | insight, re-angled to report-anchored |
| Title | OpenAI "A thousand fewer paths to root": A Successful Agent Run Is Not an Authorized One (confirm the post's verbatim title at verification) |
| Slug | `openai-a-thousand-fewer-paths-to-root-agent-verification` |
| Report-anchored (ADR-015) | yes: entity = "A thousand fewer paths to root" (OpenAI Research, 4 Nov 2026); verbatim first in all six title fields, with source and figure in the meta description |
| Topic hub | ai-coding-agents |
| Content type (`--type`) | Report Response |
| OG headline | Right Outcome, Wrong Path (4 words) |
| Editorial gate | pass: named-source entry point (OpenAI research) plus new evidence for the thesis (outcome correctness is not path correctness) |
| Five questions | changed: OpenAI ran agents across vulnerability discovery, exploitation and patching at scale; matters: 20 of 200 early successful escalations used a different vulnerability than assigned; breaks: a passing result stops proving the change followed the intended or approved path; teams should: verify the path and bind evidence to the actual change; governance helps: decisions define the authorized path, an independent check confirms it |
| Cannibalisation | `find_overlap.py` on the chat's evergreen title: use-case page 73.8, `ey-beyond-the-code-ai-software-development` 48.2, `behavioral-equivalence-architectural-compliance-migration` 39.2. Verdict: the evergreen "how to verify AI-generated code" guide is **merge or drop** (the use-case page and verification-tax own the query). **Re-angle** to a report response that uses OpenAI's finding as new evidence, and link the use-case page rather than repeat it. |
| Cross-links | `/use-cases/ci-governance-for-ai-generated-code/`, `ai-coding-agent-verification-tax`, `/concepts/agent-verification/`, `claude-code-review-trusted-decision-boundary` |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | errors: 0; warnings fixed or justified: |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

## Agreed scope

Thesis: a successful result does not prove an agent took the correct or authorized path. Lead with OpenAI's figure, then give a concrete case of an agent passing functional tests while violating an approved architectural boundary, then explain verifying the actual change through decisions, independent checks and evidence. Audience: engineering leaders and security-minded platform teams. Primary conversion: the Architecture Protection Audit.

The chat's limits on the research, to carry into the article: 948 is distinct patch-derived vulnerability counts, not merged fixes; results come from OpenAI's own pipeline, not independent reproduction; the $18.9M to $66.3M bounty value is hypothetical; about 7% of Linux kernel code was examined, chosen for security relevance. State the research shows scalable exploit discovery, not scalable remediation.

## Key facts, figures, sources

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| 2,308 candidate findings; 1,724 reproduced (74.7%); 948 distinct local privilege escalation vulnerabilities | unverified: OpenAI Research, "A thousand fewer paths to root" | unverified |
| 1,169 of 1,238 LPE candidates became working exploits (94.4%) before deduplication | same | unverified |
| About $1.21 million in API credits; about $1,279 per distinct LPE | same | unverified |
| In an earlier run, 20 of 200 successful escalations used a different vulnerability than assigned; independent checks were added | same | unverified |
| Stronger models needed less technique-specific scaffolding | same | unverified |
| A critique noting the gap between generated patches and merged changes ("SXZ.io") | unverified: chat gives no URL; cut if not found | unverified |

Render any chart or table figure from the page, not text extraction alone.

## Mneme claims and maturity

| Claim | SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL |
|---|---|
| Enforcement before a write where supported, plus an independent CI check | to classify at audit; tool hooks alone do not stop alternate mutation paths, and the article must say so |
| Evidence bound to the actual change and governing decision | to classify at audit |
| Mneme is not a vulnerability scanner | keep as a stated boundary |

## Positioning constraints

The research strengthens the thesis; it is not market validation. Do not imply Mneme caught or prevents the OpenAI failure mode. Do not copy the chat's roadmap, issue numbers or internal research tracking into the article or this repo.

## Non-insight site edits requested

None.

## Open questions

None blocking.
