# Scope brief: Post-Strategic AI Assessment

Status: **built** (drafted 2026-11-27; claim audit rounds 1 and 2 FAIL with replacements applied, round 3 PASS; PR #347, queued for 2026-12-06)

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Strategic AI Assessment` |
| Created / last updated (UTC) | 2026-11-26 / 2026-11-26 |
| Shape | 18 turns, read in full by the orchestrator; truncation check passed. The chat proposed six article ideas; the owner approved one (this brief) on 2026-11-27. The other five are held (see "Agreed scope"). |
| Repo check | `/insights/ibm-2026-tech-leader-study-agent-governance/` (June 2026, IBM Tech Leader Study, 2,000 tech leaders); `/insights/ibm-winning-agentic-frontier-enterprise-decision-rights/` (Nov 2026, IBM and Microsoft, what enterprises must own); `/concepts/engineering-decision-governance/` (concept page). No existing page covers IBM's CAIO study: `git grep -i -E "chief ai officer|CAIO|1,667" -- site/insights` finds only passing mentions of other IBM studies. |

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | IBM's 2026 CAIO Study: Accountability Without Decision Rights |
| Slug | `ibm-2026-caio-study-decision-rights` |
| Report-anchored (ADR-015) | yes: entity = "IBM's 2026 CAIO Study". IBM's report title is "A template for high-impact AI"; that title is not searchable, so the entity uses the name IBM's report URL (`/report/2026-caio`) and coverage use. The body names the report title verbatim at first mention. |
| Topic hub | architectural-governance |
| Content type (`--type`) | Report Response (primary object is a named industry survey) |
| OG headline | IBM's 2026 CAIO Study on Decision Rights (7 words) |
| Eyebrow | Report Response · Architectural governance · 8 min read |
| Editorial gate | pass: named-source entry point (IBM's CAIO study, Nov 2026) plus new evidence for the engineering decision governance thesis (61% clear decision rights vs 73% defined human oversight) |
| Five questions | Changed: IBM finds only 18% of CAIOs fully control AI investment and 61% report clear, consistently applied AI decision rights. Why it matters: CAIOs answer for AI outcomes that depend on decisions others make, now including the architectural decisions coding agents apply. What breaks: adoption metrics stay green while architecture drifts. What teams should do: separate implementation autonomy from decision authority, measure decisions written, checked, stopped, waived and reconstructable, starting with one repository. How governance helps: checks tied to named decisions give the CAIO evidence instead of policy. |
| Cannibalisation | `find_overlap.py "IBM's 2026 CAIO Study: Accountability Without Decision Rights" --keywords "chief ai officer,caio,decision rights,ai investment,coding agents"`: 119.9 ibm-2026-tech-leader-study-agent-governance; 65.5 ibm-winning-agentic-frontier-enterprise-decision-rights; 42.0 smart-routing-ai-coding-agents; 41.9 using-ibm-bob-with-architectural-guardrails. Scope-stage run: 81.2 tech-leader study, 62.7 concept page. Verdict: **re-angle**. The Tech Leader Study is a different IBM survey (2,000 CIOs/CTOs, June 2026, adoption outpacing governance); the Winning on the Agentic Frontier piece is about what an enterprise must own. This article's angle is the CAIO's accountability/authority gap, applied to the engineering decisions agents follow. It links to both and to the concept page and does not repeat or redefine them. Batch overlap: none with the other drafts in this batch (healthcare, Rust migration). |
| Cross-links | Out: ibm-winning-agentic-frontier-enterprise-decision-rights, ibm-2026-tech-leader-study-agent-governance, dora-metrics-insufficient-for-agentic-development, /concepts/engineering-decision-governance/, /docs/decision-index/, /audit/. Reciprocal in: ibm-2026-tech-leader-study-agent-governance, dora-metrics-insufficient-for-agentic-development, gartner-ai-governance-engineering-governance (all have a `related-list` slot). |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | Revision 3: 37/50 (unchanged; fixes were wording swaps). Revision 2: 37/50 (directness 8, rhythm 7, trust 7, authenticity 7, density 8). Revision 1 was 38/50; the added definitions cost a point of trust (more hand-holding), and two trims restored density. |
| `lint_prose.py` | Revision 3: errors: 0; 1,663 words, avg 15.5 words/sentence, 6% over 30, Flesch 58. Two warnings, both justified: "IBM" and "HQ" not expanded on first use; IBM is a company name and "Mneme HQ" is the publisher's proper name, not acronyms the reader needs expanded. A meta-commentary warning ("The rest of this article") was fixed. CAIO, IBV, ADR, CI and DORA are expanded at first use. |
| Cold read: thesis as restated | Round 1 (Step D): "CAIOs are accountable for AI outcomes without controlling the decisions behind them; for coding agents, engineering must make architectural decisions machine-checkable and report evidence that agents followed them, instead of adoption metrics." Matches the brief. Round 2 cold read pending. |
| Cold read: unclear terms, and how resolved | Round 1 findings, all fixed in revision 2: Mneme now introduced in one plain sentence before the mid-article CTA band; "fails open" defined in its own sentence; Claude Code defined (Anthropic's coding agent, run in a terminal); code-owner review defined via GitHub `CODEOWNERS`; agent instruction files defined with `CLAUDE.md`/`AGENTS.md` examples; high-impact CAIOs defined by IBM's AI success index (PDF p.16); "decision authority" replaced with "decision rights" throughout, tied to IBM's 61% finding; the gloss is ours; "most of the time" removed and the ambiguous "it" replaced with "those decisions"; architecture mapping signposted as our extension of IBM's budget finding; 73% vs 61% now carries IBM's own framing ("CAIOs can accelerate AI by clarifying accountability", heading on PDF p.2) and no unsupported "for a reason"; dropped verb in "fails a pull request that does" fixed; reconstruction-to-owner leap replaced with reconstruction plus the exceptions count. |

## Agreed scope

Thesis: executives accountable for enterprise AI outcomes need evidence that more agent autonomy is not undermining architectural integrity. IBM's CAIO study shows the general shape (accountability for outcomes, authority elsewhere); in software delivery, the decisions in question are architectural, they belong to engineering, and the CAIO needs a way to see whether agents followed them.

Audience: engineering leaders and the CAIOs and CTOs they report to.

Structure as built (1,200-1,500 words target; revision 3 is 1,663, over target because the cold read required definitions of fails open, Claude Code, CODEOWNERS, agent instruction files and high-impact CAIOs): what IBM found (with an associations caveat) → where the gap shows up in software delivery → why adoption metrics miss drift → separate implementation autonomy from decision rights → what executives can ask engineering to measure (framed as team-measurable, not Mneme data) → start with one repository → where Mneme fits. CTA: Architecture Protection Audit (mid band and end).

Title alternatives considered: the chat's "Why Chief AI Officers Need Engineering Decision Governance" (not entity-first, so not ADR-015 compliant); "IBM's 2026 CAIO Study: Who Holds Authority Over Agent-Written Architecture?" (too long for title truncation).

Other article ideas from the chat: five further ideas were proposed in the same chat. Per the scope handoff they are held, not built in this batch; none is merged into this article beyond the outline points it already uses.

The five held ideas (titles as proposed in the chat):
- "Architectural Decisions Are Becoming Enterprise Intellectual Property": off-site, not a site insight.
- "Decision Engineering: The Missing Discipline in Agentic Software Development": merged into the planned Decision Engineering flagship, which waits on the ADR-014/001 terminology amendment.
- "Beyond Context Engineering: Epistemic Governance": held; "epistemic governance" would need its own terminology decision.
- "Can Better Governance Reduce the Cost of Agentic Software Development?": held until experimental evidence exists.
- "From AI Security Guidelines to Enforceable Architectural Decisions": held until an OWASP AI Exchange control mapping exists.

Non-site follow-ups are tracked privately.

## Key facts, figures, sources

All figures were checked on 2026-11-27 against the IBM newsroom release and the report PDF (https://www.ibm.com/downloads/documents/us-en/17f55bd460c4b884, read in the claim audit). No figure in the article comes from a chart.

| Claim | Source URL (no `?utm_source`) | Verified? |
|---|---|---|
| Report title "A template for high-impact AI", originally published 16 November 2026, IBM IBV | https://www.ibm.com/thought-leadership/institute-business-value/en-us/report/2026-caio | verified (report page header) |
| 1,667 senior executives incl. CAIOs, CDAIOs, heads of AI; with Oxford Economics; April to June 2026; 33 geographies, 20 industries | https://newsroom.ibm.com/2026-11-17-ibm-study-chief-ai-officers-see-where-ai-creates-value%2C-but-few-control-investment-decisions | verified (Study Methodology) |
| Only 18% have full control over AI investment decisions | same release | verified (lead paragraph) |
| Foreword (Joanne Wright, SVP Transformation and Operations): outcomes "often depend on decisions made by others" | same release | verified (quoted foreword) |
| 48% say AI agents initiate and execute actions across workflows; 75% say governance, risk or compliance delays AI-driven action | same release | verified ("CAIOs balance greater AI autonomy with stronger control") |
| 73% defined where human oversight is non-negotiable; 61% say AI decision rights clearly defined and consistently applied | same release | verified (same section) |
| High-impact CAIOs nearly four times as likely to say they can quickly pause, adjust or redirect AI systems | same release | verified (same section) |
| High-impact CAIOs scale enterprise-wide in eight months vs 13.5 months for all others | same release | verified (high-impact paragraph) |
| 96% of high-impact CAIOs stop or reduce investment in failing initiatives, even with senior sponsorship, vs 46% of others | same release; also https://www.ibm.com/think/news/chief-ai-officer-authority-ai-roi | verified |
| 73% vs 61% framed under "CAIOs can accelerate AI by clarifying accountability" | report PDF: heading on p.2; figures on p.2 and p.7 | verified (PDF text) |
| High-impact CAIOs: AI success index from three self-reported outcome measures (measurable outcomes, pilot to production, time to scale); eight behaviors linked by OLS regression; methodology says "associated" | report PDF p.16 | verified (Research methodology) |
| CUT: CAIO share rose from 26% to 76% | report PDF p.3 | in the report PDF p.3, citing IBM's 2026 CEO Study (a different study); cut as off-scope |
| RESTORED: just 15% have full authority over AI workforce strategy | report PDF p.2 (key takeaways) and p.5 | verified (PDF p.2 (key takeaways) and p.5); used in revision 2, attributed to the report |
| "Twice as likely to cut funding" | report PDF p.2 | the PDF p.2 says "twice as likely"; the article uses the 96% vs 46% figures from p.14 instead |
| CUT: Forrester outcome-oriented engineering posts | not fetched; not needed for the article | not used |

## Mneme claims and maturity

Checked against `site/docs/decision-index/`, `site/docs/cli/`, `site/docs/how-enforcement-works/`, `site/setup/claude-code/`, `site/audit/` and the scope's 0.11.0 facts.

| Claim | SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL |
|---|---|
| Mneme is an open-source tool that stores a team's architectural decisions in its repository and checks code changes against them | SHIPPED |
| Decision Index: versioned record of the repository's decisions in a file inside the repository | SHIPPED (0.10.0+) |
| Only accepted decisions are active, and an active decision is enforced only when it carries a typed rule (audit fix #4) | SHIPPED |
| The typed rule hooks and CI enforce is an exact piece of text that must not appear in certain files (FORBID_LITERAL) | SHIPPED |
| Claude Code hook blocks an edit (Edit/Write/MultiEdit) that breaks the rule before the write; a single quoted `cat` heredoc is also blocked before the write; most other shell writes are checked at the end of the turn, after the write | SHIPPED |
| GitHub Actions gate fails a pull request that breaks the rule | SHIPPED |
| The JSON verdict from `mneme check --json` names each decision whose rule it evaluated, and which version, including on a pass (audit fix #9; the hook prints nothing on a pass) | SHIPPED |
| Hook fails open by default when the check cannot run | SHIPPED (documented default) |
| Decision Index does not record who approved a decision; approvals belong in code-owner review | SHIPPED (stated limitation) |
| Architecture Protection Audit lists documented decisions and shows which a Mneme check protects | SHIPPED |
| Approvals belong in code-owner review: a `CODEOWNERS` entry for the decision files plus branch protection that requires code-owner review (CODEOWNERS alone only requests review; re-audit fix #B) | external GitHub fact; no Mneme claim |
| Mneme HQ, which publishes the article, maintains Mneme, the open-source tool (re-audit fix #C; the site does not call Mneme HQ a company) | SHIPPED (tool, MIT licensed); publisher name per site JSON-LD |
| Not claimed: compliance, ROI effect, coverage of AI investment or budgets, numeric rules, Kiro | n/a (explicitly excluded) |

The five measures in "What executives can ask engineering to measure" are framed as team-measurable quantities, not Mneme results or data.

## Positioning constraints

- No "Decision Engineering", no "epistemic governance", no "bottleneck", no em dashes.
- No Palantir paper (unverified in the chat).
- "Engineering decision governance" is linked to its concept page, not redefined.
- Never claim compliance.

## Non-insight site edits requested

None.

## Open questions

- Closed: entity string "IBM's 2026 CAIO Study" accepted in claim audit, per Tech Leader Study precedent.
- Closed: report PDF read in the claim audit; all figures confirmed.

## Revision log

- 2026-11-27 rev 1: first draft (1,460 words, slop 38, lint 0 errors).
- 2026-11-27 rev 2: claim audit FAIL fixes #4 (active decisions enforced only with a typed rule) and #9 (JSON verdict, not every verdict, names decisions on a pass) applied verbatim; optional heredoc precision applied. Cold-read fixes applied (see quality gate). Restored the 15% workforce-strategy figure from PDF p.2/p.3; brief source rows and CUT rows corrected per audit; read_time 8 min. 1,660 words, slop 37, lint 0 errors.
- 2026-11-27 rev 3: re-audit FAIL fixes applied verbatim: #A (IBM attribution removed from the decision-rights bullet), #B1/#B2 (CODEOWNERS needs branch protection to require approval), #C1/#C2 (publisher is Mneme HQ, which maintains Mneme). Optional: 61% gloss changed to "who decides what"; typed-rule sentence now says "the files the rule covers". Brief: 15% cited to p.2 and p.5, heading cited to p.2, gloss note corrected, Mneme-claim rows added for #B and #C, held idea wording changed to "off-site, not a site insight".
