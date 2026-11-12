# Scope brief: Post-Openai vulnerability fixes Assess research findings

Status: **built, queued for 2026-11-15** (`openai-a-thousand-fewer-paths-to-root-agent-verification`; article PR on its own `site/` branch)

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
| Title | OpenAI "A thousand fewer paths to root": A Successful Agent Run Is Not an Authorized One (post's verbatim title confirmed 2026-11-12: "A thousand fewer paths to root", published 4 Nov 2026) |
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
| stop-slop score (/50, pass >= 35) | 41 |
| `lint_prose.py` | errors: 0 on the built page; 1 acronym warning (GPT, a model product name) |
| Cold read: thesis as restated | "checking the result is not enough; verify the path the agent took" (matches the brief) |
| Cold read: unclear terms, and how resolved | 0-day, root shell, scout agents, 10-day scan, GPT-5.5/5.6 Cyber, shell-write handling: defined; the $1,279 unit was corrected to total / 948 |
| Pre-merge Opus claim audit | blockers and should-fix items applied; see the article PR |

## Agreed scope

Thesis: a successful result does not prove an agent took the correct or authorized path. Lead with OpenAI's figure, then give a concrete case of an agent passing functional tests while violating an approved architectural boundary, then explain verifying the actual change through decisions, independent checks and evidence. Audience: engineering leaders and security-minded platform teams. Primary conversion: the Architecture Protection Audit.

The chat's limits on the research, to carry into the article: 948 is distinct patch-derived vulnerability counts, not merged fixes; results come from OpenAI's own pipeline, not independent reproduction; the $18.9M to $66.3M bounty value is hypothetical; about 7% of Linux kernel code was examined, chosen for security relevance. State the research shows scalable exploit discovery, not scalable remediation.

## Key facts, figures, sources

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| 2,308 candidate findings; 1,724 reproduced (74.7%); 948 distinct local privilege escalation vulnerabilities | https://openai.com/index/a-thousand-fewer-paths-to-root/ | verified (Summary; Vulnerability validation: "Within 30 hours, our system reproduced 1724 vulnerabilities, ~74.7% of the 2,308 candidate findings"). 948 is counted by patches, not by exploits: "We performed variant analysis and developed 948 distinct patches for the vulnerabilities behind those exploits. We use that number to determine the overall number of unique LPEs" (Exploitability assessment). The 2,308 is "after deduplication" (Analyst agents). |
| 1,169 of 1,238 LPE candidates became working exploits (94.4%) before deduplication | https://openai.com/index/a-thousand-fewer-paths-to-root/ | verified (Exploitability assessment): screening narrowed to 313 information leak and 1,238 LPE candidates; ExploitDev produced "1,169 working local privilege escalation exploits" and 291 information leak PoCs. The 94.4% and "before deduplication" are our arithmetic and reading, not the post's words. |
| About $1.21 million in API credits; about $1,279 per distinct LPE | https://openai.com/index/a-thousand-fewer-paths-to-root/ | differs: post says "$1,213,430 in API credits, or $1,279 per LPE exploit" (Findings; the headline says "$1.2 million"). Say "per LPE exploit", not "per distinct LPE". Average cost of a successful exploit-development attempt is a separate figure: $359 (Exploitability assessment). |
| In an earlier run, 20 of 200 successful escalations used a different vulnerability than assigned; independent checks were added | https://openai.com/index/a-thousand-fewer-paths-to-root/ | verified ("Using the wrong 0-day"): in an early run the exploitation stage reported 200 successful LPE exploits; after human review 20 "had achieved root privileges through a different 0-day vulnerability than the one assigned". Fix: "tightened the task constraints and added an independent check confirming that each final exploit used its assigned vulnerability". Takeaway: "verify the path to a result in addition to verifying the result itself". |
| Stronger models needed less technique-specific scaffolding | https://openai.com/index/a-thousand-fewer-paths-to-root/ | verified ("More capable models can require lighter orchestration"): GPT-5.5 Cyber with 103 techniques added went from 76.2% to 88.9% success across 63 candidates; GPT-5.6 Cyber with the layer removed outperformed the scaffolded 5.5 workflow, and adding it back gave +1.5 points. |
| About 7% of Linux kernel code examined | https://openai.com/index/a-thousand-fewer-paths-to-root/ | verified (Scout agents): 5,034 audit targets, about 2.8 million lines, "roughly 7% of the whole Linux kernel code base"; chosen for reachability by low-privileged users and security relevance. |
| Hypothetical bounty value $18.9M to $66.3M | https://openai.com/index/a-thousand-fewer-paths-to-root/ | verified (Findings; "What defenders can learn from exploit costs"): historic Pwn2Own $20,000 and TyphoonPWN $70,000 per Linux kernel LPE applied to 948 exploits gives "a hypothetical valuation of $18.9M-$66.3M, approximately 16x to 55x our pipeline's cost". |
| Patches merged upstream | https://openai.com/index/a-thousand-fewer-paths-to-root/ | NOT STATED as a count of OpenAI's patches - cut any such claim. The post says only that when the 10-day scan finished "61 LPEs had already been patched upstream, 43 had staging patches, and 299 were being reported and discussed publicly" (Findings; "Maintainers are moving quickly"), and that this counts fixes from other contributors too (Reflections: "patched or had staging patches from other contributors"). It also says "hundreds of reports and patches" were sent (Patch generation), not how many were merged. |
| A critique noting the gap between generated patches and merged changes ("SXZ.io") | none found | NOT FOUND - cut. Searches for sxz.io returned nothing; secondary coverage makes the same point, but none was verified as the critique the chat meant. |

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
