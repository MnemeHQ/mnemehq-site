# Scope brief: Post-Assess Claude Feature

Status: **built** (drafted 2026-11-23; cold read FIX fixed; claim audit FIX (2), FIX (3), then PASS at round 3; PR #334, queued for 2026-11-29)

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Assess Claude Feature` |
| Created / last updated (UTC) | 2026-11-23 / 2026-11-23 |
| Shape | 2 user turns; the second ("Repost with thoughts") got no text reply, so the first answer is the agreed scope. Captured complete by step A. |
| Repo check | No page mentions Claude Ship, Claude Approvals or PR Steward (`git grep` over `site/`). Closest: `claude-code-review-trusted-decision-boundary` (2026-10-25), `autonomous-code-remediation-requires-architectural-governance` (2026-05-13). |

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | Claude Ship: Who Checks the Architecture Behind AI-Approved Code? |
| Slug | `claude-ship-architecture-ai-approved-code` |
| Report-anchored (ADR-015) | yes: entity = "Claude Ship" (named vendor system); entity leads title, H1, OG |
| Topic hub | architectural-governance |
| Content type (`--type`) | Analysis |
| OG headline | Claude Ship approves. Who checks architecture? (6 words) |
| Editorial gate | pass: named-source entry point (Claude Ship, announced 2026-11-23, no existing page) and distinct query ("Claude Approvals CI", "Claude Ship governance"); also supports the CI setup and Claude Code setup pages through internal links |
| Five questions | Changed: a model can now be a counted PR approver (Claude Approvals) and an agent fixes failing checks (PR Steward). Matters: approval answers "who approved", not "does it respect our decisions". Breaks: a correct, tested, approved change can still break an architecture decision; a remediation agent with workflow write and unprotected check config. Do: keep CI separate and required, CODEOWNERS plus Approvals rules on workflow and decision files, bypass list, stale approvals, observe mode. Governance: an independent required decision check beside the Approvals check, plus the agent-side hook before the PR. |
| Cannibalisation | `find_overlap.py "Claude Ship and Claude Approvals: who verifies the architecture behind AI-approved code" --keywords "claude ship,claude approvals,pr steward,ai code approval,required check,architectural governance"`: 61.0 `architectural-governance-across-heterogeneous-ai-coding-agents`; 43.5 `claude-code-self-hosted-environments-architectural-governance`; 43.3 `how-ai-coding-agents-use-adrs`; 40.9 `ai-coding-agents-life-sciences-governance`; 40.4 `why-architectural-governance-needs-precedence-semantics`. All read at title/H2 level: none covers Claude Ship, approval policies or CI-as-separate-check. Body grep for "Code Review"/"approval" surfaced `claude-code-review-trusted-decision-boundary`, which owns the "PR must not rewrite the rules that judge it" argument (four trust boundaries, five checks). **Verdict: clear** (new named-vendor entry point), with a re-angle discipline: this article is about the approval layer, Approvals' blindness to CI and the remediation agent; it links to the Code Review article for trust boundaries and does not restate them. No other brief in this batch overlaps (single-article run). |
| Cross-links | `claude-code-review-trusted-decision-boundary` (linked twice in body); `/setup/claude-code/`, `/setup/ci/`; reciprocal from `autonomous-code-remediation-requires-architectural-governance` |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 37/50 after audit and cold-read fixes (directness 8, rhythm 7, trust 8, authenticity 7, density 7; was 38). One revision pass: removed a rhetorical setup ("one line that matters more than the rest"), a "what's missing" closer, a negative-contrast paragraph, "real limits", "usually", and a pull-quote sign-off. |
| `lint_prose.py` | errors: 0; warnings: 0 (1,892 words, avg 16.0 words/sentence, 12% over 30, Flesch 65, after fixes). Two verbatim Anthropic quotes carry `voice-ok` markers (not needed by lint, kept for the audit). |
| Cold read: thesis as restated | "Claude Approvals counts approvals but cannot see CI or architecture decisions, so keep separate required checks and protect the files that define them." Matches. |
| Cold read: unclear terms, and how resolved | FIX applied: seat, machine user, classifier, required status check, bypass list, memory file defined at first use; Mneme paragraph split; "!pr/authors" explained in plain words. Defined at first use: PR, CI, ADR, classifier, required status check, active typed rule, fail open. |

## Agreed scope

Thesis: Claude Approvals decides whether a change may be approved under team policy; it cannot read CI, and Anthropic says to keep CI as its own required check. A deterministic architecture-decision check is that kind of independent required check, and the Claude Code hook covers the agent side before the PR exists. Complementary, not antagonistic. Address the remediation risk honestly: PR Steward can be granted workflow write; the docs do not describe a guardrail against editing check configuration, so teams configure CODEOWNERS / branch rules / Approvals rules on those files. Audience: engineering leaders and platform owners turning on Claude Ship. Structure: what shipped; what Approvals decides and cannot see; an approved change can still break a decision (labelled hypothetical); PR Steward and the files that define checks; where Mneme fits; five settings. Title alternatives considered: the scope's "Claude Ship and Architectural Governance: Who Verifies the Decisions Behind AI-Approved Code?" (too long for truncation, entity buried after "and"); chosen title keeps entity first at 65 chars.

Other follow-ups from the chat are tracked privately and are not recorded in this public repository.

## Key facts, figures, sources

All checked 2026-11-23 against the live pages (step B extracts re-fetched with WebFetch where noted).

| Claim | Source URL | Verified? |
|---|---|---|
| Announced Nov 23, 2026; "can review PRs, fix them, and decide what's ready to merge based on policies each team sets"; Team and Enterprise, GitHub; Code Review GA, PR Steward and Approvals beta; PR Steward designed not to approve or merge; Approvals policy is a file in the repo | https://claude.com/resources/articles/introducing-claude-ship | verified (article body, step B extract; date header) |
| Approvals: policy `.claude/approvals.yml`; conditions read PR facts and classifier answers; "A condition can't read CI results, so keep CI as its own required check in GitHub."; check blocks merge only where required, normally not in observe mode; author can fill a seat; Claude's approval can count as the GitHub approval | https://code.claude.com/docs/en/approvals | verified (re-fetched: "Example policy"; "Merges without human review") |
| Merge-without-review cases (seats: 1, machine users, uncovered files, classifier answers a PR's text can steer); check blocks only where required; stale-approval settings | https://code.claude.com/docs/en/approvals-github-rules | verified (re-fetched: intro; "Merges without human review"; "Required reviews and CODEOWNERS"; "Who can change or loosen a policy") |
| Provided classifiers `claude/code_review`, `claude/diff`; custom classifiers; default-branch definition runs, PR's copy doesn't | https://code.claude.com/docs/en/approvals-classifiers | verified (step B extract: "Classifiers Anthropic provides"; "How a run behaves") |
| Protected files list (policy/classifier files, REVIEW.md, Git files, CODEOWNERS); "Don't rely on other files being protected"; names `.github/`; the one person can be the author; `"!pr/authors"`; `mode: observe` | https://code.claude.com/docs/en/approvals-policy | verified (re-fetched: "Protected files"; "Whether a pull request's author counts"; "Top-level keys") |
| PR Steward fixes failing checks "when the cause is in code that the pull request touches", merge conflicts, review feedback | https://code.claude.com/docs/en/pr-steward | verified (step B extract: "What PR Steward fixes") |
| PR Steward permissions incl. workflows write on github.com, "which lets PR Steward push changes to workflow files"; service refuses approving, branch protection/rulesets/statuses changes, check runs, branch deletion, tags; merge/force-push left to GitHub; keep app off bypass list; instruction files from default branch. No guardrail against editing check configuration described | https://code.claude.com/docs/en/pr-steward-security | verified (re-fetched in full: "PR Steward's GitHub access"; "Limits on approvals and merges") |
| Code Review "focuses on correctness: bugs that would break production"; reads diff without building/running; no findings "doesn't mean your code is error-free or secure"; doesn't approve or block by itself | https://code.claude.com/docs/en/code-review | verified (step B extract: intro; "How reviews work") |
| CODEOWNERS: owners auto-requested; "Require review from Code Owners" in branch protection or rulesets; own the CODEOWNERS file itself | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners | verified (fetched 2026-11-23) |
| Required status checks must pass before merging; admins bypass unless restricted | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches | verified (fetched 2026-11-23: "Require status checks before merging") |

Cut as unverifiable or out of scope: "PR Steward remediates failing external checks" as a quoted Anthropic claim (no explicit statement on third-party checks found); credits offer and Code Review levels (not needed).

## Mneme claims and maturity

Checked against `/setup/claude-code/` and `/setup/ci/` (both "Tested with mneme-hq 0.11.0"; `scripts/core_version.json` = 0.11.0) and `/docs/how-to/fail-pull-request-that-breaks-adr/`.

| Claim | Class |
|---|---|
| Mneme is an open-source tool that checks code changes against a team's recorded architecture decisions | SHIPPED |
| Keeps recorded decisions in one memory file in the repository | SHIPPED |
| Enforces only decisions with an active typed rule; a decision with no active rule blocks nothing | SHIPPED |
| A `## Constraints` rule in an ADR is active as soon as the ADR is imported | SHIPPED |
| Claude Code plugin hook refuses Edit/Write/MultiEdit that breaks an active rule before the file changes | SHIPPED |
| Most other shell writes are checked when the agent ends its turn, after the write; agent sent back to fix | SHIPPED |
| Hook fails open by default; repository can opt in to refusing direct edits when the check can't run | SHIPPED |
| CI job runs `mneme check` on every text file a PR adds or modifies and fails on a broken active rule; verdict names the decision | SHIPPED |
| Not covered: deleted files, binary files, pushes that skip PRs | SHIPPED (stated limitation) |
| Blocks a merge only where made a required check | SHIPPED (GitHub behaviour; stated on /setup/ci/) |
| Refund example: an exact-text rule forbidding billing's internal module path in the orders service fails the PR whoever wrote it | SHIPPED (FORBID_LITERAL with optional path selector; hypothetical scenario labelled) |
| Mneme has not been run alongside Claude Ship; requiring both checks is documented GitHub configuration, not a tested integration | statement of fact (no claim of interoperability) |
| Mneme enforces encoded rules, not whole-system architectural conformance | SHIPPED (limitation) |
| CI job reads the memory file and ADRs from the PR's checkout, so an agent that can edit them or the workflow can change what is enforced; protect with owner review | SHIPPED (limitation, per /setup/ci/ "The check can be weakened") |

Not claimed anywhere: PR Steward consuming Mneme findings, measured results, MCP server, Decision Index, protected-state corpus resolution.

## Positioning constraints

Complementary to Claude Ship, never antagonistic. No implication of tested interoperability: Mneme has not been run alongside Claude Ship, and the article says so.

## Non-insight site edits requested

None.

## Open questions

- If integration testing is done later, decide whether to add a dated "What we tested" note or a separate results article.
