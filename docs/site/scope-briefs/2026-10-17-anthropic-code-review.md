# Scope brief: Post-Anthropic code review

Status: **queued** for the scheduled publisher (one article per day from 2026-10-23; PRs #239-#244) (batch 4, phase 1)

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Anthropic code review` |
| Created / last updated (UTC) | 2026-10-17 / 2026-10-17 |
| Shape | 4 user turns: assess the article, add learnings to the roadmap, draft a LinkedIn comment, scope an article. The last turn is the scope; it narrows the earlier "who decides what the code must respect" title to the trust-boundary angle. Read in full 2026-10-20; no collapsed turns. |
| Repo check | No page mentions `REVIEW.md` or the Anthropic post. Review-scale pages exist: `ai-code-review-does-not-scale-linearly` (2026-05-07), `why-code-review-cannot-scale-with-ai-output` (2026-05-05), `use-cases/ci-governance-for-ai-generated-code`. |

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | How the Claude Code Team Does Code Review: The Rule a Pull Request Must Not Rewrite (confirm the post's verbatim title at verification; the chat's concept-first alternative is "AI Code Review Needs a Trusted Decision Boundary") |
| Slug | `claude-code-review-trusted-decision-boundary` |
| Report-anchored (ADR-015) | yes: entity = the Anthropic engineering post's verbatim title (chat renders it as "How the Claude Code team does code review"; URL slug `solving-code-review-at-anthropic`) |
| Topic hub | architectural-governance (card also fits ai-coding-agents) |
| Content type (`--type`) | Analysis (named external development in the title) |
| OG headline | A Pull Request Cannot Rewrite Its Rules (7 words) |
| Editorial gate | pass: named-source entry point (Anthropic engineering post) plus a distinct query (AI code review governance, review policy integrity) |
| Five questions | changed: Anthropic reads review rules from the protected base branch, not from the PR under review; matters: once agents write the PR, they can also edit the policy file that judges it; breaks: a correct evaluator gives an untrustworthy verdict when the change under evaluation controls its inputs; do: check where your agents' and CI's rules come from, who can change them, and whether verdicts bind to the exact commit; governance: decisions resolved from a trusted, versioned state, independent of the change |
| Cannibalisation | `find_overlap.py`: `ai-code-review-does-not-scale-linearly` 61.0, `github-copilot-usage-based-billing-review-economics` 52.5, `why-code-review-cannot-scale-with-ai-output` 50.0, `use-cases/ci-governance-for-ai-generated-code` 45.5. All four argue volume or cost of review; none covers who controls the rules a review applies. Verdict: **re-angle, clear on that angle**: policy-input integrity, not review scale. Do not restate the volume argument; link to it. |
| Cross-links | `ai-code-review-does-not-scale-linearly`, `why-code-review-cannot-scale-with-ai-output`, `use-cases/ci-governance-for-ai-generated-code`, `concepts/engineering-decision-governance`, `from-decision-records-to-decision-governance` |

## Draft quality gate (filled at build time)

| Check | claude-code-review-trusted-decision-boundary |
|---|---|
| stop-slop score (/50, pass >= 35) | 41 (8/8/8/8/9) |
| `lint_prose.py` (built page) | 0 errors; 1 warning kept: CLI is part of the product name Codex CLI |
| Cold read: thesis as restated | An AI review gate is only trustworthy if the change it judges cannot edit the rules, checker or approval that judge it. Matches. |
| Cold read: unclear terms, and how resolved | First pass: Code Review product vs internal process, CLAUDE.md, typed rule, decision corpus, native write tools, governed waivers; all defined. Built-page pass: lede now credits the base-branch rule to Code Review, FAQ 'proves nothing' softened, risk-tier approval explained. |

**Pre-merge Opus audit (2026-10-20):** 4 blockers and 11 should-fix findings across the batch, all fixed before the PR: shell-write coverage per agent (Claude Code review), typed-rule capability and a misquoted Grab line (Node.js to Go), an invented Kyverno quote (Policy as Code), warn vs strict exit codes (Kubernetes), Codex CLI naming, OpenAI's evaluation order, and the overstated decision-recovery study finding (OpenAI, cornerstone). The audit re-verified every load-bearing figure against the live sources.

## Agreed scope

- **Central argument:** automated review can find violations, but it is not trustworthy governance if the change under review can also modify the decisions, policies or evaluator used to approve it.
- **Sentence to build on:** a system cannot claim a change complied with engineering decisions unless it can prove which decisions were authoritative when the change was evaluated.
- **Structure (from the chat):**
  1. Anthropic's most important review decision is not about AI: `REVIEW.md` and project rules come from the protected base branch; human approvals are commit-specific.
  2. When a pull request can rewrite its own rules: a hypothetical PR adds a forbidden direct database dependency and edits the local policy file to drop the prohibition; CI reads the policy from the same PR. Label it clearly as illustrative.
  3. Four trust boundaries: trusted policy origin, evaluator integrity, revision identity, independent approval authority. Turning on strict mode in CI does not establish them.
  4. Resolving a review comment is not authorizing an exception: a false-positive dismissal versus a waiver, which needs decision identity, approver, scope, reason and expiry.
  5. The same decisions must govern generation, review and merge: pre-action enforcement and CI consume the same approved decisions.
  6. Five questions to ask before trusting an AI review gate (close).
- **Corrected flow to draw:** trusted approved decisions → pinned evaluator → proposed change → revision-bound verdict → independent merge control.
- Length 1,400-1,700 words. Not a criticism of Anthropic: their system is substantial evidence of the workflow change. Not an Anthropic-vs-Mneme comparison.
- Also from the assessment turn (usable as context, must be verified): the review system combines agent reviews, security checks, CI, risk-based human approvals, merge queues, gradual release and rollback; one PR went through 50+ review/fix rounds, after which they added round limits, deduplication and changed-diff review. Human judgment moves to architecture that sets future patterns, whether to build something, and ownership of outcomes.

## Key facts, figures, sources

| Claim | Source URL | Verified? |
|---|---|---|
| Anthropic engineering post on how the Claude Code team does code review, published 2026-10-15 | https://claude.dev/blog/solving-code-review-at-anthropic/ | unverified |
| Merged PR volume more than doubled; reverted-PR share fell 40%+ (June-September) | same | unverified; observational, not causal; say so |
| ~12x increase in daily monorepo changes (May-September) | same | unverified |
| One PR passed 50+ agent review/fix iterations; round limits, dedup and changed-diff review followed | same | unverified |
| `REVIEW.md` read from the protected base/default branch, not the PR | Claude Code docs (code review page; URL to capture) | unverified |
| Path-scoped `CLAUDE.md` instructions can be checked by the reviewer | Claude Code docs | unverified |
| The public Code Review product posts findings; it does not approve or block PRs itself; runs on Anthropic-managed infrastructure | Claude Code docs | unverified; do not conflate the internal merge system with the GA product |
| "Three review rounds before reconsidering the approach" | same post | unverified |

**Verified record (2026-10-20).** The table above is the scope-time list. Each built article's checked sources follow; anything absent from them was cut, not softened.

### `claude-code-review-trusted-decision-boundary`

| Claim | Verified |
|---|---|
| Post title, date, authors | verified: https://claude.dev/blog/solving-code-review-at-anthropic/ (H1 "How the Claude Code team does code review"; 15 Oct 2026; Addy Osmani, Morgan Westlee Lunt, Qing Wang). Title uses the verbatim words in title case. |
| Merged PRs more than doubled; reverted share fell by more than 40% (June-September) | verified: same URL (introduction). The post gives no causal analysis; body says so ("before-and-after figures, not a controlled comparison"). |
| ~12x increase in daily monorepo changes (May-September) | cut: the post states "about 2,500 in May to more than 30,000 in September"; 12x is derived arithmetic and the figure is the monorepo, not Claude Code's repo. Not needed for the thesis. |
| One PR passed 50+ review/fix rounds; round cap, diff-only re-review, no repeats followed | verified: same URL ("Review has to converge": "One CLI PR went through more than fifty rounds of review and fixes overnight before its author stopped it.") |
| "Three review rounds before reconsidering the approach" | verified: same URL ("Review has to converge": "After three rounds, the reviewer asks the author to step back and reconsider the approach.") |
| Minimum human review time that doesn't raise reverts or incidents | verified: same URL (introduction) |
| Claude writes about 90% of Claude Code's code | verified: same URL (introduction, "about 90 percent"); body says "most" |
| Layers: CI, AI review verified by agents, blocking security review, risk-based approval, merge queue re-running checks against main, flags and gradual release | verified: same URL ("Layer by layer" sections 1-6) |
| Approval covers one specific commit; re-approval after agent push or hand-resolved merge | verified: same URL ("5. Human approval, scaled by risk") |
| Some paths always need a person: owner-listed sensitive paths and any CI workflow file | verified: same URL ("5. Human approval, scaled by risk", "The change sets the tier, not the author.") |
| PR can't merge with an open bug/security finding; close thread with short reason to clear a false positive | verified: same URL ("3. Security review that can block") |
| Humans keep architecture that sets a pattern others will copy | verified: same URL ("Where humans stay in the loop") |
| REVIEW.md read from base or default branch, never from the PR's own changes; merge first | verified: https://code.claude.com/docs/en/code-review-customize ("Which branch REVIEW.md is read from") and https://code.claude.com/docs/en/code-review ("Who controls a review") |
| Severity lowering / path exclusion / nit caps honored only on protected default branch | verified: https://code.claude.com/docs/en/code-review-customize ("Which branch REVIEW.md is read from") |
| If Code Review can't confirm branch protection settings, it reads no REVIEW.md | verified: https://code.claude.com/docs/en/code-review-customize ("What a review reads for each branch setup", last row: Copy read None, Files read None) |
| Path-scoped CLAUDE.md read (root plus parent directories of changed files) and violations flagged | verified: https://code.claude.com/docs/en/code-review-customize ("Use CLAUDE.md for project-wide rules"). The docs do not say which branch CLAUDE.md is read from, so the article makes no branch claim about CLAUDE.md. |
| Code Review never approves or blocks; check run doesn't conclude as failure; runs on Anthropic infrastructure; Team and Enterprise plans | verified: https://code.claude.com/docs/en/code-review (intro, "How reviews work", "What a review can access", "Availability"). The page does not say "GA", so the article says "the Code Review service for Team and Enterprise plans" instead. The internal blocking security review and the product are kept separate (FAQ 2). |

## Mneme claims and maturity

| Claim | Class |
|---|---|
| Deterministic enforcement of typed rules in CI (`mneme check`, GitHub Actions / GitLab) | SHIPPED (0.10.0); only decisions with an active typed rule are enforced |
| Pre-write enforcement through native write tools of supported agents | SHIPPED, scoped to native write tools (Claude Code Edit/Write/MultiEdit, Codex apply_patch, Kiro v3); shell writes are end-of-turn |
| Decision Index with versions, lifecycle and source | SHIPPED (0.10.0); records no approver identity |
| Decisions resolved from a trusted snapshot independent of the PR (protected-input CI) | PLANNED / under investigation; the current check is advisory and a strict-mode merge-blocking experiment is not complete |
| Governed waivers with approver, scope and expiry | PLANNED (no approver identity is stored today) |
| ADR-031 effective resolution and evidence identity | accepted design, unreleased: design direction only |
| Generating `REVIEW.md` / `CLAUDE.md` guidance from the Decision Index | CONCEPTUAL |

## Positioning constraints

- Do not claim conventional AI review is unaware of architectural rules: Anthropic's docs show path-scoped instructions are checked.
- Do not describe the hypothetical as an exploit seen in production.
- Deterministic rules cannot judge every architecture decision; some need human review. The trust boundary is about who decides, not about automating every judgment.
- The CTA is the Decision Index and enforcement docs, with the Architecture Audit as secondary.

## Non-insight site edits requested

None. (The chat's roadmap and LinkedIn-comment turns are tracked outside this repo.)

## Open questions

- **Owner decision:** the chat proposes citing Mneme's own CI investigation (a PR can supply its own decision memory, evaluator and workflow definition) as an "inspectable" finding. Publish it, name it generally, or omit? Default if unanswered: describe it in general terms as a gap Mneme is closing, with no internal workstream names.
