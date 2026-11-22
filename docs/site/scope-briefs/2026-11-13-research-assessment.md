# Scope brief: Post-Research assessment

Status: **gathered, not built** (two articles drafted in scratch; cold read and claim audit pending; third article held)

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Research assessment` |
| Created / last updated (UTC) | 2026-11-13 / 2026-11-13 |
| Shape | 6 turns (3 user, 3 assistant); truncation check passed, no "Show more" marker remained. Turn 1 assesses a pasted newsletter of enterprise AI research (attachment content not exposed). Turn 2 is internal planning, tracked privately. Turn 3 scopes three articles: two P1 (Teleport Beams; IBM and Microsoft "Winning on the agentic frontier") and one P2 pilot checklist held for evidence. Earlier editorial briefs: site issues #304, #305, #306. |
| Repo check | No page mentions Teleport, Beams or the IBM/Microsoft report. Runtime-versus-architecture pages exist: `runtime-verification-is-not-architectural-verification`, `microsoft-execution-containers-ai-agent-runtime-governance`, `agent-runtime-governance`, `zero-trust-for-ai-agents-architectural-governance`, `/integrations/nvidia-openshell/`. IBM pages exist for a different study: `ibm-2026-tech-leader-study-agent-governance` (June 2026, 2,000 tech leaders, 77%), plus `enterprise-ai-guardrails-five-layers` and `using-ibm-bob-with-architectural-guardrails`. |

The chat yields **two articles now** (A, B) and **one held** (C). Other follow-ups from the chat are tracked privately.

## Build card A: Teleport Beams

| Field | Value |
|---|---|
| Kind | insight |
| Title | Teleport Beams: An Approved Plan Is Not an Approved Design |
| Slug | `teleport-beams-agent-runtime-architectural-decisions` |
| Report-anchored (ADR-015) | yes: entity = "Teleport Beams" (named system); first in all six title fields; meta description leads with entity, GA date and the seven built-in classifiers, all in the body |
| Topic hub | agent-infrastructure |
| Content type (`--type`) | Analysis (named vendor launch) |
| OG headline | Teleport Beams Approves Plans, Not Designs (6 words) |
| Editorial gate | pass: named-source entry point (new GA launch, no site coverage) plus new evidence for the runtime-versus-decision thesis: Beams' plan approval and objective classifiers move runtime security toward intent, and the article shows where they still stop |
| Five questions | changed: Teleport made Beams GA (Nov 9, announced Nov 10, 2026) with delegated identity, plan approval by a human or LLM judge, objective classifiers, micro-VMs; matters: plan approval and objective classifiers look like design review; breaks: an agent with an approved plan and valid roles writes a forbidden direct database import, every runtime control passes; teams should: keep runtime controls, stop counting plan approval as design review, keep each decision in one place, require a decision check on the PR; governance helps: a check that holds the decision and reads the change, in the agent's write path and in CI |
| Cannibalisation | `find_overlap.py` (scope title + keywords "Teleport Beams, agent runtime security, execution plan approval, architectural decision check"): `microsoft-execution-containers-ai-agent-runtime-governance` 58.3, `agent-runtime-governance` 52.2, `runtime-verification-is-not-architectural-verification` 41.7, `runtime-harnesses-for-ai-agents` 37.8. Final title: `beyond-security-by-design-governance-by-design` 61.5 (matches on "design" only; concept piece, different intent), MXC 57.6, `agent-runtime-governance` 51.5. Body grep for teleport, beams.run, micro-vm: no hits. Read all 40+ pages. Verdict: **re-angle**. Runtime isolation is not architectural governance is already argued (MXC, OpenShell, runtime-verification). This piece is narrower: it covers what plan approval, LLM-judge review and customer-defined objective classifiers can and cannot answer, using a shipped worked example. It does not restate the sandbox argument; it links to those pages instead. |
| Cross-links | out: `/docs/how-to/stop-agent-crossing-architectural-boundary/`, `/docs/decision-index/`, `/docs/how-enforcement-works/`, `/audit/`; reciprocal: `runtime-verification-is-not-architectural-verification`, `microsoft-execution-containers-ai-agent-runtime-governance`, `zero-trust-for-ai-agents-architectural-governance` |

## Build card B: IBM and Microsoft, Winning on the agentic frontier

| Field | Value |
|---|---|
| Kind | insight |
| Title | IBM's Winning on the Agentic Frontier: What Enterprises Must Own |
| Slug | `ibm-winning-agentic-frontier-enterprise-decision-rights` |
| Report-anchored (ADR-015) | yes: entity = "Winning on the Agentic Frontier" (report title is sentence case, "Winning on the agentic frontier"; title case used for search display), with "IBM's" for the publisher; meta description leads with the entity and the 22% figure, both in the body |
| Topic hub | architectural-governance |
| Content type (`--type`) | Report Response |
| OG headline | Winning on the Agentic Frontier: Own Decisions (7 words) |
| Editorial gate | pass: named-source entry point (new IBM/Microsoft report, no site coverage) plus cornerstone support for decision governance via the report's own "define what the enterprise must own" list |
| Five questions | changed: IBM IBV and Microsoft surveyed 1,000 executives; only 22% have meaningful governance and controls, none cover the full agent lifecycle; matters: the report names decision rights, policies, evidence and escalation authority as things to keep in-house; breaks: decisions kept inside one agent or runtime are lost when the tool changes; teams should: inventory decisions, count which are machine-checked, name owners, test verdict reconstruction, list what lives only in the current tool; governance helps: a versioned decision record in the repository plus checks with recorded verdicts (Mneme covers decisions and evidence; not decision rights) |
| Cannibalisation | `find_overlap.py` (title + keywords "Winning on the agentic frontier, agentic AI decision rights, enterprise AI governance controls, IBM Microsoft agentic"), 12 pages at 40+, all read: `microsoft-agentic-transformation-playbook-ai-agent-governance` 97.6 (Microsoft playbook, operating-model framing), `microsoft-ai-decision-brief-architectural-intent` 71.6 (where intent lives), `claude-frontier-academy-frontier-deployed-engineers` 68.8, `gartner-ai-governance-engineering-governance` 59.8, `using-ibm-bob-with-architectural-guardrails` 53.6, `ibm-2026-tech-leader-study-agent-governance` 53.0 (different IBM study, 77% framing, policy documents are not controls), `microsoft-agent-platform-governance-layer` 50.4, `enterprise-ai-guardrails-five-layers` 48.5, `microsoft-project-solara-post-app-governance` 47.5, `microsoft-execution-containers-ai-agent-runtime-governance` 46.9, `bcg-four-pillars-agentic-ai-need-architectural-intent` 42.5, `governance-control-plane-after-agent-frameworks` 41.5. Body grep for "agentic frontier", "Oxford Economics", "13x", "Institute for Business Value", "decision rights": only the Tech Leader article (different report) and one Microsoft brief quote on decision rights. Verdict: **clear** (named-source entry point; no page covers this report). The article names the Tech Leader Study as a different study and links it. |
| Batch overlap | The `Post-Databricks AI Assessment` chat in this batch scopes an article on governance surviving changes of model, agent and runtime. Article B touches portability only in one table row and one worked example, links `/concepts/model-independent-governance/` for the full argument, and centers on IBM's ownership list (decisions, rights, evidence). The orchestrator should check that the Databricks draft does not lead with the same vendor-switch example. Article A and B do not overlap: A is runtime controls against decision checks, B is enterprise ownership. |
| Cross-links | out: `/insights/ibm-2026-tech-leader-study-agent-governance/`, `/concepts/model-independent-governance/`, `/docs/decision-index/`, `/audit/`; reciprocal: `ibm-2026-tech-leader-study-agent-governance`, `microsoft-ai-decision-brief-architectural-intent`, `from-decision-records-to-decision-governance` |

## Held: C, AI agent pilot checklist

`ai-agent-pilot-production-readiness-checklist` (Guide, agent-infrastructure). The chat itself holds it as P2 until a reproducible public or synthetic worked example with permitted and forbidden changes, and an exact support matrix, exist. **Held for evidence; not drafted.** Overlap screen for the record: `microsoft-agentic-transformation-playbook-ai-agent-governance` 57.8, `bcg-four-pillars-agentic-ai-need-architectural-intent` 41.2, `/pilot/` 40.4. Re-run the overlap check and editorial gate when the evidence exists.

## Draft quality gate (filled at build time)

| Check | A: Teleport Beams | B: Winning on the Agentic Frontier |
|---|---|---|
| stop-slop score (/50, pass >= 35) | 40 after revision 1 (directness 8, rhythm 8, trust 8, authenticity 8, density 8) | 39 after revision 1 (directness 8, rhythm 8, trust 8, authenticity 7, density 8) |
| `lint_prose.py` (draft body) | errors: 0; warnings: 0 (revision 1) | errors: 0; 1 warning (revision 1), justified: acronym "IBM" is the publisher's name, not an abbreviation a reader needs expanded |
| Cold read: thesis as restated | matched: runtime security checks access and behavior, not whether code respects the team's decisions, so a separate decision check is needed | matched: models and tools are rentable, so enterprises should keep architectural decisions, who can change them, and check evidence in their own repository, not inside a vendor's tool |
| Cold read: unclear terms, and how resolved | "the swarm" glossed as Teleport's label for agent behavior; "blast radius" replaced with plain words; Mneme introduced before its terms; "Decision Index", "typed rule", "hook" and "turn" defined at first use; six-row controls table replaced by two short paragraphs; classifier section shortened and headed "Untested"; hook and shell-write paragraph rewritten as five numbered steps | Oxford Economics described as the research firm that ran the fieldwork; "decision rights" glossed at first use (lede and body); "harnesses" removed; Mneme introduced before its terms; "Decision Index", "typed rule" and "hook" defined at first use; table cell and the version-record sentence rewritten in plain steps; mid CTA band made concrete and tied to the CTO question list |

Thesis to match at cold read. A: runtime controls such as Beams decide what an agent may reach and do; they do not check the code it writes against the team's decisions, so teams need a decision check on the change as well. B: IBM tells enterprises to own decision rights, policies, evidence and escalation; for software teams that means owning architectural decisions, who may change them, and proof of what each change was checked against, outside any single vendor's tool.

## Revision 1 (A: Teleport Beams), 2026-11-22

Claim audit verdict FIX, six items. Applied verbatim: 1 (invented backstory sentence deleted), 2 (kill switch attributed to the press release, not the blog), 3 (sandbox comparison now uses Teleport's own "traditional sandboxes" wording), 6 (literal-match limit now names `import app.db.client as db`). Items 4 and 5 applied in substance: the cold read asked for the controls table to be cut, so the table no longer exists. The replacement prose carries both fixes. It names the three public built-in rules as examples ("such as"), not as the full set. It opens with "We have not run this inside Beams. Walk the controls as Teleport describes them". It also uses the audit's sentence "As Teleport describes them, each runtime control would give the correct answer to its own question." No audit item was declined.

## Revision 1 (B: Winning on the Agentic Frontier), 2026-11-22

Claim audit verdict FIX, four items, all applied verbatim: 1 (date "On November 6, 2026" and "in partnership with Microsoft"), 2 (foreword paraphrase), 3 ("real operating conditions"), 4 ("Active decisions with a typed rule are enforced"). The FAQ's report answer was also changed to the November 6 date to stay consistent. No audit item was declined.

## Agreed scope

A. Teleport Beams. Final scope from turn 3: technical analysis, 1,250 to 1,600 words, for platform, security and architecture leads. Core argument: an agent can have valid credentials, an approved execution plan and an isolated environment and still make a change that breaks an authoritative architectural decision. Structure: what Beams provides; why authorization to modify a service does not imply architectural correctness; a worked example with a forbidden direct database dependency; how a decision check complements runtime permissions; how the two combine, without claiming an integration. The piece must earn its place through Beams' own mechanisms (custom classifiers, approved execution plans). Never claim Teleport cannot express any architectural policy. Primary call to action: Architecture Audit.

B. IBM. Final scope: report response, 1,450 to 1,850 words, for CTOs, VPs Engineering and architects. Core argument: enterprises can replace models, agents and infrastructure providers; they should not lose control of the approved decisions, policies, evidence and authority that govern their systems. Structure: what the study found; why governance and evidence must survive vendor changes; what to rent, buy and own (marked as Mneme's analysis, not IBM's); how a decision record preserves engineering decisions across agents; questions for CTOs. The 13x figure is observational and self-reported and must be stated as such. Call to action: Architecture Audit, then Decision Index docs.

Draft lengths: A body 1,205 words of prose (1,722 with FAQ and markup text); B 1,322 (1,695). B is below the chat's 1,450 floor; it covers every planned section, and adding length would only restate them.

## Key facts, figures, sources

Source files are in the batch scratch directory; page numbers are the IBM PDF's printed numbers.

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| Teleport announced Beams GA on November 10, 2026; GA as of November 9, 2026; public beta since March 2026 | https://goteleport.com/about/newsroom/press-releases/teleport-beams-trusted-runtime-ai-agents-general-availability/ | verified (press release dateline and "Availability" section) |
| Four layers: delegated identity; zero standing privileges; execution plans reviewed by "a human or an LLM judge"; separate runtime executes with only approved roles; access to cloud accounts, Kubernetes, PostgreSQL, MCP servers without secrets; session scoring against MITRE ATT&CK; classifiers flag behavior that departs from the agent's objective; ephemeral micro-VMs | same | verified ("Four layers of control"). Article names MITRE ATT&CK only as "a public framework of attacker techniques" to keep the prose free of unexpanded acronyms |
| Seven pre-built classifier rules including "secrets exposed inline", "destructive actions", "privilege escalation"; customer-defined rules supported; natural-language classifiers | same | verified ("Differentiated Control") |
| Kill switch ends the agent's activity and connections to production infrastructure | same | verified ("Differentiated Control") |
| "Beams doesn't try to guarantee what a model decides" and the limits list | same | verified ("Limiting the blast radius"); the only direct quotation in A |
| Micro-VMs expire in 11 hours | https://goteleport.com/blog/teleport-beams-secure-ai-agents-production/ | verified (blog, "Cloud isolated runtime environment", published Nov 10, 2026) |
| Teleport GA material does not describe checking changes against recorded architectural decisions, nor classifiers blocking a file write | press release and blog | verified as absence only; the article says "does not describe", never "cannot" |
| Report identity: "Winning on the agentic frontier: How enterprises build intelligence competitors can't buy", IBM Institute for Business Value with Microsoft, 36-page PDF | https://www.ibm.com/downloads/documents/us-en/187b1233b0643d46 ; landing page https://www.ibm.com/thought-leadership/institute-business-value/en-us/report/agentic-ai-learning | verified (PDF cover; landing page fetched 2026-11-22, HTTP 200) |
| Publication date | same | verified: PDF footer "November 2026"; landing page says "Originally published 06 November 2026". Article says "November 2026" (see Open questions) |
| 1,000 C-suite executives, Aug to Sep 2026, Oxford Economics fieldwork, 17 geographies, 19 industries, revenues or budgets US$500 million to US$126.5 billion, unweighted | PDF | verified (p.28 Research methodology) |
| Only 22% have meaningful governance design and operational controls; none of more than 900 report controls across the whole lifecycle (identity, permissions and access, traceability, shutdown) | PDF | verified (p.3 key takeaways; p.20) |
| Only 20% have fully implemented a formal agent registry; registry is "the foundation for these controls" | PDF | verified (p.20) |
| 66% use at least one open agent protocol; only 17% pursue standards convergence | PDF | verified (p.21 text and Figure 6, rendered page read by Step B) |
| 58% rate lack of a governed enterprise orchestration layer as a barrier; highest bar in Figure 5 (others 57% to 55%) | PDF | verified (Figure 5, p.19, rendered page read by Step B) |
| 44% high deployment and strong foundations, 40% low deployment and weak foundations; first group reports agentic AI ROI 13x higher | PDF | verified (Figure 3, p.9, rendered page read by Step B) |
| 13x uses raw, unadjusted, self-reported ROI over 12 months, not audited; findings are associations, not causation | PDF | verified (p.29 profiles paragraph; p.30 Interpretation) |
| Foundations = governance and accountability, operational agent controls, operating model | PDF | verified (p.29) |
| Six capabilities: ecosystem strategy and design, governance and accountability, controls, work design and workforce readiness, execution, learning | PDF | verified (p.8 Figure 2) |
| Action guide: "Define what the enterprise must own": business alignment, proprietary data, workflow orchestration, decision rights, policies, evidence, escalation authority; specify where to depend on providers without surrendering strategic control | PDF | verified (p.27) |
| Governance action guide: translate responsibility into enforceable controls; set explicit boundaries for autonomous action (independent / human review / prohibited); test governance and confirm teams can reconstruct decisions | PDF | verified (p.22) |
| Foreword: what cannot be rented is the intelligence an enterprise accumulates from its own experience | PDF | verified (p.2); paraphrased, not quoted |
| IBM 2026 Tech Leader Study: 2,000 technology leaders, early 2026, 77% say adoption outpaces governance | existing page `/insights/ibm-2026-tech-leader-study-agent-governance/` | site's own published, audited page; used only to distinguish the two studies |
| Not used (cut or out of scope): McKinsey channel research (supports held article C only); Anthropic Fable 5.2 and Artificial Analysis ranking (assessment turn only); Deloitte management research (not verified, cut); pasted newsletter items (unreachable) | | n/a |

## Mneme claims and maturity

Checked against `/docs/how-enforcement-works/`, `/docs/decision-index/`, `/docs/mcp/`, `/docs/how-to/stop-agent-crossing-architectural-boundary/` (tested with mneme-hq 0.11.0), `/docs/how-to/fail-pull-request-that-breaks-adr/`, `/integrations/github-actions/`, and `scripts/core_version.json` (0.11.0).

| Claim (article) | Class |
|---|---|
| A: Mneme is an open-source tool that stores a team's architectural decisions in the repository and checks code changes against them | SHIPPED |
| A: Mneme is not a runtime, identity provider or sandbox; it has no integration with Teleport Beams and has not been run inside a Beam | SHIPPED (true negative) |
| A: ADR-012 example with a typed rule forbidding the literal `from app.db.client import` under `app/handlers/` | SHIPPED (how-to, 0.11.0) |
| A: in Claude Code the hook checks a file edit before it lands, blocks this write and returns the broken decision to the agent | SHIPPED |
| A: shell writes it cannot check in advance are caught when the agent finishes its turn | SHIPPED (Claude Code Stop audit) |
| A: the GitHub Actions gate checks the pull request and fails it; make it a required status check | SHIPPED |
| A, B: each result records the rule that matched, the triggering text (A only) and the path it applied to | SHIPPED |
| A: literal matching misses unusual import forms; a decision without a typed rule guides but is not enforced | SHIPPED (stated limit) |
| A, B: Decision Index is Mneme's persisted, versioned record of a repository's decisions | SHIPPED (0.10.0+) |
| B: each version immutable, records content hash and, for ADR imports, the ADR file and its hash; a re-imported changed ADR becomes a new version pointing to its predecessor; superseded decisions kept but not enforced | SHIPPED |
| B: the same file feeds CLI checks, agent hooks, CI gate and an MCP server that lets agents read the decisions that apply to a change | SHIPPED (MCP is local stdio only; article does not claim remote access) |
| B: Mneme covers decisions and evidence, not decision rights; does not record approvers; does not route exceptions; docs recommend code-owner review on ADR and decision files | SHIPPED (stated limit and documented guidance) |
| B: Mneme has not measured its effect on ROI | true statement, no capability claimed |
| B: rent / buy / own table | CONCEPTUAL (labelled in the article as Mneme's analysis, not IBM's) |
| A: "two checks at two points" table and the four recommendations | CONCEPTUAL (practice guidance; Beams column restates Teleport's GA material) |
| A: a customer-defined Beams classifier might flag the import | CONCEPTUAL, untested; the article says so |

No VALIDATED EXPERIMENT or PLANNED claims are made. No partnership, customer, adoption or ROI claim for Mneme.

## Positioning constraints

- Beams is described from Teleport's own material, fairly; it is not framed as a competitor or as deficient. Never say Teleport cannot express architectural policy.
- IBM's report is about agentic AI across the enterprise, not software architecture. The article says so and marks the engineering translation as Mneme's.
- The 13x is association, raw and self-reported. It is never a promise of return from governance or from Mneme.
- "Decision Index" is capitalised, defined at first use, and never said to record approvers.
- "Decision layer" thesis framing is not used.

## Non-insight site edits requested

None.

## Open questions

1. **IBM publication date.** Resolved in revision 1: the audit confirmed the landing page's "Originally published 06 November 2026", and the body and FAQ now say November 6, 2026.
2. **Title case of the report name.** Resolved: title case "Winning on the Agentic Frontier" kept in all six fields (auditor confirmed).
3. **Article C.** Stays held until the evidence in the chat's publication gate exists.
