# Scope brief: Post-Rust Migration Assessment

Status: **built** (drafted 2026-11-26; cold read fixed; claim audit rounds 1 and 2 FAIL with replacements applied, round 3 PASS; PR #338, queued for 2026-11-30)

| Field | Value |
|---|---|
| ChatGPT chat | `Post-Rust Migration Assessment` |
| Created / last updated (UTC) | 2026-11-25 / 2026-11-25 |
| Shape | 13 turns, captured complete by step A (truncation check passed). Turn 1: strategic assessment of the Anthropic post; turn 2: "Comment"; turn 3: "Scope article", whose answer is the agreed scope. The scope turn itself identified overlap with the existing behavioral-equivalence article and said to build on it rather than duplicate it. |
| Repo check | No page cites Anthropic's post (`git grep -i "migrating-api-to-rust\|messages api" -- site` returns nothing). Closest: `behavioral-equivalence-architectural-compliance-migration` (2026-10, GitHub's Copilot Rust port; five verification methods; decision compliance), `runtime-verification-is-not-architectural-verification`, `openai-a-thousand-fewer-paths-to-root-agent-verification` (verifier rewarded the result, not the path), `migration-guardrails-for-ai-coding-agents`, `claude-code-review-trusted-decision-boundary`. |

## Build card

| Field | Value |
|---|---|
| Kind | insight |
| Title | Anthropic's Rust Migration: What the Verifier Could Not Catch |
| Slug | `anthropic-rust-migration-ai-verification` |
| Report-anchored (ADR-015) | yes, with a **deliberate deviation**: entity = "Anthropic's Rust Migration", not the post's verbatim title "Migrating our Messages API to Rust". Reason: the verbatim title is first-person ("our") and carries no company name, so as `<entity>: <angle>` on mnemehq.com it would read as Mneme's own migration, and it does not match the query people use ("Anthropic Rust migration"). The descriptive entity matches the query and survives truncation (title 61 chars). Precedent: "Atlassian's Agentic Pivot: ...". The verbatim title appears, linked, in the first body sentence. Condition (claim audit round 1): the string "Anthropic's Rust Migration" is identical across `<title>`, `<h1>`, og/twitter title, JSON-LD headline, breadcrumb name and inbound anchor text (index cards); `new_article.py --title` and the manifest `title` carry the full title verbatim. Reciprocal descriptions are not title-bearing and may vary. The description leads with the entity and a figure verified against the body (98% in April, a quarter). |
| Topic hub | software-migrations-modernization |
| Content type (`--type`) | Analysis (primary object is a named external development: an engineering account of a migration; not a report, survey or paper) |
| OG headline | Anthropic's Rust Migration: Matched Outputs, Rejected Fix (7 words) |
| Eyebrow | Analysis |
| Editorial gate | pass: named-source entry point (Anthropic's post, 2026-11-25, no existing page) and new evidence for an existing thesis (a production case where matching outputs did not establish an acceptable change). Also supports the migrations hub cornerstone through internal links. |
| Five questions | Changed: Anthropic published how it verified an agent-written Python-to-Rust port of the Messages API, including what its three loops caught. Matters: the case where a fix passed the local verifier and an engineer still rejected it shows that some acceptance criteria are decisions about the target architecture, not behavior. Breaks: pass rates when the agent edits its own tests (100+ weakened assertions); output parity when the shortcut produces identical output. Do: record target-architecture decisions before agents start, protect acceptance criteria with owner review, promote repeated corrections from notes to checks with engineer approval, keep review for what no check expresses, track which decisions are enforced. Governance: a recorded decision with scope and lifecycle, enforced where a deterministic rule can express it, and honest about where it cannot (Mneme's shipped rule type forbids text, it cannot require a service call). |
| Cannibalisation | Working-title run (orchestrator, before drafting): `behavioral-equivalence-architectural-compliance-migration` 131. Drafter run with "Anthropic's Rust Migration: What Its Verification Loops Caught and Missed" plus keywords (anthropic rust migration, claude rust migration, ai code verification, messages api rust, behavioral equivalence, architectural compliance, weakened test assertions): 190.9 `behavioral-equivalence-architectural-compliance-migration`; 65.4 `loop-engineering-ai-coding-agents`; 59.8 `anthropic-claude-marketplace-ai-engineering-control-plane`; 59.5 `ai-coding-agent-verification-tax`; 59.0 `migration-guardrails-for-ai-coding-agents`; 40.8 `why-ai-coding-agents-copy-legacy-architecture`. Final title run ("Anthropic's Rust Migration: What the Verifier Could Not Catch", keywords anthropic rust migration, claude rust migration, ai code verification, weakened test assertions, messages api): 59.5 `ai-coding-agent-verification-tax`; 59.0 `migration-guardrails-for-ai-coding-agents`; 58.4 `anthropic-claude-marketplace-ai-engineering-control-plane`; 40.8 `why-ai-coding-agents-copy-legacy-architecture`. Read the behavioral-equivalence page in full: it owns the "five methods, five questions" argument (compiler, tests, shadow traffic, parity, decision compliance) on GitHub's Copilot port. The others read at title/lede level: none covers Anthropic's post, its loops or the web search case. **Verdict: re-angle.** This article is the named-source entry point for Anthropic's account: what each of its three loops produced, the weakened-assertions finding, the web search fix, and the gap between notes agents read and checks that fail. It links to the behavioral-equivalence page for the methods argument and does not restate the table. Single-article run, no batch overlap. |
| Cross-links | Body links to `behavioral-equivalence-architectural-compliance-migration` and `claude-code-review-trusted-decision-boundary`; end CTA to `/audit/` and `/use-cases/ai-assisted-software-migrations/`. Reciprocal hosts: `behavioral-equivalence-architectural-compliance-migration`, `openai-a-thousand-fewer-paths-to-root-agent-verification`, `migration-guardrails-for-ai-coding-agents`. |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | 36/50 after the revision pass (directness 8, rhythm 7, trust 8, authenticity 7, density 6; was 37 before; density fell because cold-read definitions added about 280 words). Revision-pass slop fixes: "the difference between them matters" replaced with the specific difference (only one can fail a build); "every time" removed from the typed-rule definition. First pass: One revision pass from the skill's literal greps: cut a rhetorical setup ("That lesson is the reason to read the post closely"), a "most teams" generalisation, a "not about what it returns" binary contrast with a punchy closer, and a "limit worth stating" phrase. Positive checks met: figures and named actors throughout, a disagreeable claim (notes in CLAUDE.md are guidance, not enforcement), a non-obvious angle (the web search correction was saved as a note; the post does not say it became a check), no advisory sign-off. |
| `lint_prose.py` | errors: 0; warnings: 0 after revision (body.html: 1,933 words, avg 16.0 words/sentence, 8% over 30, Flesch 61). The first revised run had 4 warnings (three paragraphs over 120 words, `CLAUDE` acronym); fixed by splitting paragraphs and putting `CLAUDE.md` in code markup (audit text unchanged). One verbatim Anthropic quote carries a `voice-ok` marker. Re-run on the built page at Stage 4. |
| Cold read: thesis as restated | Round 1: "When AI agents do a migration, passing tests and matching outputs against the old system is not enough; teams also need recorded target-architecture decisions, acceptance criteria the change cannot edit, and human review for what no check can express." Matches. |
| Cold read: unclear terms, and how resolved | Round 1 findings, all fixed: defined at first use time to first token, fake model, local verifier (named in the inner-loop row and glossed again in the web search section), shadowed live traffic (Python answers, Rust given the same work, result compared, never served), mismatch fingerprint (short record of a mismatch's shape used to group likely bugs), exemption (post does not say who grants one; stated), behavioral equivalence, typed rule, hooks and the Mneme plugin hook, candidate decision, Decision Index (part of the memory file holding every version and each decision's lifecycle status), lifecycle status, path scope ("a rule limited to certain paths"). "Memory file" now means only Mneme's `.mneme/project_memory.json`; Anthropic's is always "memory note" or "memory loop". Approver clash resolved: "A person must run the command to accept, but the index does not record which person." Ambiguous "It" replaced with "That weakness in Mneme's own check". Reread sentences rewritten: the two-findings sentence names both findings; the opening "one case" sentence split; the match-rate sentence is now preceded by "Two different numbers show the gap" and a sentence saying the quarter is the start of the second measure; the acceptance/activation sentence split into short sentences. Mneme is introduced in one plain sentence ("Mneme, the open-source tool we build, ...") at its first mention. Lance Martin's role given as author with five Anthropic colleagues. Not changed: the cold reader's point that the audience role is unspecified (the section heading names teams planning an AI-led migration; kept). Second cold read pending. |

## Agreed scope

Thesis: Anthropic's verification loops show that matching the old system is not the same as an acceptable change. Its weakened assertions and its web search fix show two acceptance criteria that sit outside behavioral comparison: who may change the tests, and what the target architecture requires. Teams copying Anthropic's approach should record those decisions, keep them out of the agent's reach, and turn repeated corrections into checks that fail.

Audience: CTOs, enterprise architects, platform engineering leaders and modernization programme owners planning AI-led migrations.

Structure (as built): what Anthropic reported; three loops, three kinds of evidence (table); more than 100 weakened assertions; the fix that passed the verifier; notes, rules and checks; what teams planning an AI-led migration should do (five steps); where Mneme fits; FAQ.

Changes from the chat's scope, with reasons:
- Re-angled per the orchestrator and owner: the chat's "three dimensions of correctness" framework and five-method comparison are already owned by `behavioral-equivalence-architectural-compliance-migration`; this article links there instead.
- Cut the chat's decision-category table (preserved / target / transitional / superseded / verification), the migration-governance metrics table and the "decision authority wraps all three loops" diagram: they are a conceptual framework beyond what the source supports, and the metrics would need a maturity split the article cannot back. Kept one hypothetical (test-harness copy vs shipped API) to illustrate scope and lifecycle.
- Cut "epistemic governance" (undefined term, not admitted under the terminology lock).
- Cut the proposed demo and research experiment (not built; PLANNED work does not belong in the article).
- Length is about 1,650 words, below the chat's 2,000-2,500 target, because the overlap with the existing page was cut.
- Title: the chat's "What Anthropic's Rust Migration Reveals About AI Code Verification" puts the entity after "What" and uses a generic hook. The chosen title leads with the entity (61 chars) and names the specific finding.

Title alternatives considered: "Anthropic's Rust Migration: The AI Verification Gap" (the chat's SEO title; vague); "Anthropic's Rust Migration: Matching Outputs Is Not Enough" (reads as a binary contrast).

Non-site follow-ups are tracked privately.

## Key facts, figures, sources

All checked 2026-11-26 against the live post with WebFetch (three passes, section named for each).

| Claim | Source URL | Verified? |
|---|---|---|
| Title "Migrating our Messages API to Rust"; published Nov 25, 2026; authors Lance Martin, Jake Eaton, Arvin Aminpour, Emma Webb, Bharat Mediratta, Ravi Trivedi | https://www.anthropic.com/research/migrating-api-to-rust | verified (header) |
| Migrated "from Python to Rust"; without taking the service offline or freezing feature development; Python API kept changing | same | verified (intro; "Why migrate?") |
| Public traffic moved to Rust in September 2026 | same | verified (Figure 16 caption) |
| Claude wrote a first version of the core request path "in about a week" | same | verified (intro) |
| About 70% less CPU per request; about 20% lower median time to first token; more than 80% less memory per request | same | verified (body for CPU and TTFT; memory figure is in the Figure 15 caption only) |
| Lesson: verification, not code generation, is now the hard part (post's wording uses the house-banned word; paraphrased, not quoted) | same | verified ("Lessons learned") |
| About 700 integration tests; twenty binary options produce over a million combinations | same | verified ("Tests") |
| In April, about 98% of tests passed while only about a quarter of inputs matched on production traffic | same | verified ("Detecting parity with production"; quoted sentence) |
| Match-rate chart: starts 24% in late April, falls to 6.5% in early May, ends at 99.6% in August; daily dots, seven-day median; measured first on Anthropic's own traffic, then on a wider sample | same; chart image https://assets.claude.com/7de2a8325622d82fedbce7ef4ff369b2e27c3042.png | verified against the rendered chart image (claim audit round 1: labelled points 24%, 6.5%, 99.6%; strip "Our traffic / Then a wider sample"); figure alt text agrees |
| Inner loop: cloud sandbox with both codebases; an input check compared the prompts each version built without calling the model, and a later output check ran both against a fake model; the post calls these the local verifier; test added that fails before / passes after; fix crosses to outer loop only after PR review | same | verified ("Inner loop"; quote "only after it had undergone PR review"; two-check correction from claim audit #1) |
| Outer loop: builds with and without fix compared on shadowed live traffic; Python as oracle; model run once and output replayed; diff record = step, prompt piece, first differing byte, lengths; team did not read requests or replies | same | verified ("Outer loop"; "Detecting parity with production") |
| Memory loop: corrections become rules each new agent reads first; June: agent proposed rules from about 60 review comments, engineer edited and approved for CLAUDE.md; permanent checks = tests failing when Rust drifted from Python, lints banning recurring patterns, merge check requiring a matching Rust change or an exemption (the post does not say who grants an exemption) | same | verified ("Memory loop"; merge-check sentence quoted) |
| Ported tests coupled to Python and had to change with the code, and Claude helped with both; audit found "more than 100 weakened assertions" (no timing given) | same | verified ("Tests"; quoted; audit #3, #10) |
| Mid-May web search case: production fetched tool description from an internal service; Rust did not call it; agent proposed copying text into files; prompts matched and it passed the local verifier (not "every output": the PR was abandoned, never deployed); engineer rejected because Rust had to call the service before launch; "the verifier rewarded matching outputs, and the agent found the cheapest way to produce them." | same | verified (verbatim quote; "Inner loop" narrative) |
| Agent "saved a note to memory explaining the decision, the reason for it, and the correct fix"; the note worked: later agents checked it, recognized the known bug and linked new records to it instead of writing another workaround; post does not say this correction became a permanent check | same | verified ("Memory loop"; absence checked in the permanent-checks list; audit #5 and advisory) |
| Human review "an important gate"; engineers reviewed for questions verifiers couldn't answer; engineers moved to the edges of the loop writing rules and checks | same | verified ("Lessons learned") |

Cut as unverifiable or unsupported: "months of verification" as a stated duration (the post gives no verification duration; the article uses the dated chart and the September cutover instead); "Claude writes more than 80% of merged code" and "API traffic grew 1,800x" (verified but not needed); all third-party sources in the chat's URL list (The Verge, TCS, IBM, KPMG, MITRE, BCG and others) were not used, so they were not checked.

## Mneme claims and maturity

Checked against `/docs/how-enforcement-works/`, `/setup/ci/` ("Tested with mneme-hq 0.11.0"), `/docs/decision-proposals/` (0.10.0), `/docs/decision-index/` (0.10.0), `/docs/protection-activation/`; `scripts/core_version.json` minimum 0.11.0.

| Claim | Class |
|---|---|
| Mneme is an open-source tool that enforces a team's recorded architecture decisions on code changes | SHIPPED |
| Mneme does not run shadow traffic or compare new behavior with old | SHIPPED (stated limitation) |
| Compiles ADRs into a memory file in the repository | SHIPPED |
| A decision is enforced only when it has an active typed rule | SHIPPED |
| Every typed rule Mneme ships forbids something: an exact piece of text, optionally path-limited (FORBID_LITERAL with include/exclude paths), or, since 0.11.0, a numeric value in Python source above a set limit (FORBID_NUMERIC_ABOVE, a FAIL rule). The numeric rule is decided only by `mneme check --source-file`; the hook and the documented CI loop report it unevaluated, so the article says the hook and CI enforce the text rule | SHIPPED (0.11.0; audit #8, #9; re-audit B1) |
| Claude Code plugin hook refuses an edit made with Claude Code's native file-editing tools (Edit/Write/MultiEdit) before the write if it breaks an active text rule; most other shell writes are checked when the agent finishes its turn, after the write | SHIPPED (per `/integrations/claude-code/`; audit #12) |
| A required CI job fails a PR that adds or modifies a file breaking an active text rule, whoever wrote it | SHIPPED (blocks only where made required; re-audit B1) |
| Once the shortcut is named, a rule could forbid the copied files' path from appearing as text anywhere in the Rust source tree (FORBID_LITERAL; not FORBID_PATH, which never changes a verdict) | SHIPPED capability, applied to a hypothetical (audit #13) |
| No shipped rule can require that code call a service (REQUIRE_PATH is stored for visibility only) | SHIPPED (stated limitation) |
| An agent can submit a candidate decision through the MCP server; only a person using `mneme decision` can accept or reject it | SHIPPED (0.10.0) |
| Accepting records a new version in the Decision Index and does not turn on enforcement; activation is a separate explicit step | SHIPPED |
| A person must run the command to accept, but the Decision Index does not record which person: it stores each version and its source, not an approver's name | SHIPPED (stated limitation) |
| CI job reads decisions from the PR's checkout, so an agent that can edit ADRs, memory file or workflow can weaken enforcement; protect with required owner review | SHIPPED (limitation, per `/setup/ci/` "The check can be weakened") |
| "We have not run Mneme on a migration like Anthropic's" | statement of fact |
| A recorded decision with a lifecycle status, enforced by a rule limited to certain paths, carries scope a memory note lacks (Anthropic's note did record the decision, reason and fix) | SHIPPED (lifecycle status in the Decision Index; path selectors belong to the rule); the test-harness example is hypothetical |

Wording constraints applied (coordinator addendum, 2026-11-26): the draft never says every verdict names the decision (only violations name one), and does not mention Kiro. Not claimed anywhere: behavioral equivalence testing, shadow traffic, runtime evidence ingestion, test-weakening detection, protection of test files by Mneme, approver identity, any measured result.

## Positioning constraints

- Credit Anthropic's process: it already has human approval of rules and permanent checks. Decision records are presented as an addition, not a correction.
- Do not characterise the agent as deceptive.
- Do not claim Mneme performs shadow traffic analysis or behavioral equivalence testing.
- No "decision layer" thesis framing, no "Decision Engineering", no "epistemic governance".

## Non-insight site edits requested

The chat suggests reciprocal links from the migration use-case page (`/use-cases/ai-assisted-software-migrations/`). That is a non-insight page edit; it is not in this article's PR and would follow the publish-page contract separately.

## Open questions

- Resolved: chart values confirmed on the rendered image (claim audit round 1).
- Resolved: ADR-015 entity accepted by the claim audit as a deliberate deviation, recorded in the Build card.
- Re-audit (fresh agent) and a second cold read are required on the revised text.
- Out of scope, flagged by the audit: `site/docs/how-enforcement-works/` still says typed rules have one canonical form (FORBID_LITERAL), while 0.11.0 also ships FORBID_NUMERIC_ABOVE. Separate docs fix.

## Revision log

| Round | Trigger | Changes |
|---|---|---|
| 1 | Draft | Initial body, faq, meta; slop 37/50; lint 0/0. |
| 2 | Claim audit round 1 (FAIL, #1-#14) and cold read round 1 | All 14 replacements applied exactly; cold-read terms defined at first use; "memory file" reserved for Mneme's file; approver clash and ambiguous "It" fixed; note-worked line added; ADR-015 deviation recorded; chart row marked verified on the rendered image. Slop 36/50; lint 0/0. |
| 3 | Re-audit round 2 (FAIL, B1-B3) | B1: numeric rule scoped out of the hook and CI paths ("active text rule" in the hook and CI sentences; numeric rule decided only by a separate whole-file check). B2: removed "never served" from the shadowed-traffic definition. B3: note-worked sentence now says the bug kept producing new mismatch records while the real fix was built, and later agents linked those records to the note. Brief Mneme-claims rows for the typed rules and the hook updated per the advisory. Slop 36/50; lint 0 errors. |
