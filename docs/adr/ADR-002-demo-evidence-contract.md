---
id: ADR-002
title: "Demo claims must match their executable path"
status: accepted
priority: foundational
date: 2026-08-20
scope: site.demo_evidence
---

# ADR-002: Demo claims must match their executable path

## Status

Accepted — 2026-08-20

## Context

A UX audit of `/demo/` in August 2026 found four defects that share one root
cause: the website's narrative had drifted away from the product's executable
state. These were not styling problems. They were evidence-chain problems.

1. The homepage advertised `python demo.py --dry-run` printing
   `BLOCKED · decision rule-001`. That script is a context-injection
   before/after comparison. It skips alignment evaluation entirely in
   `--dry-run`, and the string `rule-001` does not exist anywhere in the
   product. The surrounding card labelled the experience "Reproducible".
2. The ADR-005 centerpiece asserted three different severities for one
   scenario: prose said "blocks", the animation rendered `FAIL`, and the
   page's own expected-output block said `Result: WARN`.
3. `/demo/agent-sdk-governance/` told visitors to run
   `cd mneme/examples/agent-sdk-governance && python run.py` and claimed
   "the repo ships a Python script". That directory does not exist.
4. `/demo/` cited "117 passing benchmark scenarios". 117 was a stale test
   count from a May 2026 planning document; the benchmark suite has 7
   scenarios, and the test suite had grown to 447.

A governance product cannot afford demos whose claims drift from their
source. Fixing the four instances without fixing the mechanism would let an
equivalent set accumulate again.

## Decision

Every severity or capability claim on a demo surface must correspond to an
executable path that produces it, or be explicitly marked illustrative.

### Canonical evidence contract — ADR-005 centerpiece

| Field | Value |
| --- | --- |
| Scenario | ADR-005 brand-vs-package namespace rule |
| Canonical command | `python examples/demo-adr-import.py` |
| Actual verdict | `WARN [ADR-005] constraint "no MnemeHQ" -- trigger: mnemehq` |
| Actual capability | Deterministically detects the violation before the compliant retry |
| Claims allowed | detects, flags, warns, catches |
| Claims not allowed | blocks, prevents, stops execution |

The homepage, the `/demo/` hub, the flagship page, and the runnable command
all derive their story from this contract. Changing the verdict requires
changing the contract first.

### Illustrative examples

A surface may show a `BLOCK` or `FAIL` verdict that no shipped command
produces **only** when it is scoped to the reader's own hypothetical
repository and names no clonable path. The homepage typed-rule example
(`IF path = frontend/** AND dependency = @google-cloud/bigquery THEN BLOCK`)
and its `ADR-017` verdict qualify. They describe the enforcement model, not a
reproducible run.

This ADR does not narrow Mneme's positioning. Genuine deterministic block
paths may be claimed wherever they are demonstrably true. What is forbidden is
claim-to-evidence mismatch on a surface that invites the reader to reproduce it.

### Badging

`Runnable` may be applied only to a command that exists in the published
repository and whose on-page output matches the real run. Anything else is
`Walkthrough` or `On the roadmap`.

## Constraints

- REQUIRE_PATH: site/demo/**

### What Mneme does and does not enforce here

An earlier draft carried `FORBID_DEPENDENCY: rule-001` and claimed the
fabricated identifier could not re-enter the site without the preflight
firing. Testing that claim produced three findings, recorded here rather than
quietly fixed, because this ADR exists to stop exactly that kind of
unverified assertion.

1. Wrong directive. `FORBID_DEPENDENCY` tokenises its value, so `rule-001`
   reduced to the trigger `rule` and fired on any page containing the word --
   235 files here, including this repository's own governance copy.
2. Wrong input. The preflight ran `mneme check` against
   `.mneme/changed-paths.txt`, a file listing changed *path names*. No content
   directive can fire against a list of paths. A second CI step now feeds the
   contents of changed `site/` files, so content decisions become evaluable.
3. The right directive is not released yet. `FORBID_LITERAL` matches an exact
   string and takes `include_paths`; verified locally, it returns
   `FAIL [ADR-002] FORBID_LITERAL "rule-001"` on the literal and `PASS` on
   "typed rules compile into enforceable constraints". But it landed after the
   `v0.5.1` tag and PyPI's newest release is 0.5.1, so the published
   distribution silently drops the rule. This repository installs
   `mneme-hq>=0.5.0` from PyPI on purpose, to exercise the same path
   documented for users, so pinning CI to a git ref to gain the directive
   would defeat the point of dogfooding.

So `rule-001` is **not** machine-enforced today. Add the `FORBID_LITERAL`
directive to the Constraints section above once a release containing it ships,
and re-run `mneme adr import` to compile it.

What decision constraints cannot express at any version is a byte-level
property. Newline convention and character encoding are not text tokens, so
they stay with repository checks:

- `scripts/check_encoding.py` -- mojibake and stray BOMs.
- `scripts/check_line_endings.py` -- a change that rewrites a file's newline
  convention.

## Consequences

- Reintroducing `rule-001` still passes CI. That regression depends on review
  attention until a `mneme-hq` release carries `FORBID_LITERAL`; the CI step
  that feeds file contents is already in place to evaluate it when it does.
- Demo severity language is now derivable from one table instead of being
  restated independently on each page.
- Shipping a real blocking path for ADR-005, or a genuine
  `examples/agent-sdk-governance`, is a contract change followed by a copy
  change — in that order.
