---
name: claim-audit
description: Use when a draft or page says anything about what Mneme does, supports or will do, or cites an external figure, before it merges or posts - insights, docs, integration, compare, persona and landing pages, LinkedIn posts, bylined editorial articles, release copy. Also use when asked to "audit claims", "fact-check", "check capability claims", "is this overclaiming", or to run the pre-merge Opus audit.
---

# Claim audit

The "is it true?" gate from `PUBLISHING.md`, "Pre-merge review gates (all content)". CI checks
structure, never truth; this audit is the only thing that catches capability inflation and
misread figures. It does not check readability: the comprehension and slop filter does that.

## Who runs it

A **fresh** agent (`opus`, `medium`), read-only, that did not write the text. Give it the text,
the brief and the sources, never the writer's reasoning. It reads branches with
`git diff origin/main...<branch>` or `git show <ref>:<path>`, never `git checkout` (that has
detached HEAD in shared worktrees). It does not edit; it reports.

## 1. Classify every sentence about Mneme

One row per sentence (or clause) that describes Mneme, calibrated to ADR-001's claim levels in
`MnemeHQ/mneme`:

| Class | Meaning |
|---|---|
| SHIPPED | In the released version named in `scripts/core_version.json`, documented on the site |
| VALIDATED EXPERIMENT | Ran in a controlled experiment with published evidence; not a supported product path |
| EXPERIMENTAL | Exists in a branch, draft spec or experiment, not released or supported |
| PLANNED | On the roadmap (`/roadmap/`) or an accepted-but-unreleased ADR |
| CONCEPTUAL | Thesis or category framing; no product behaviour claimed |

Flag a sentence when its wording implies a higher class than the truth. Calibration:

- **Category and vision claims may lead** ("the decision and control layer for agentic software
  development"). Do not flag them, but they must stay on surfaces `PUBLISHING.md` allows
  (thesis "decision layer" wording is insights/concepts/about only).
- **Capability claims** may generalise reasonably from what works today; flag only when
  misleading.
- **Concrete claims stay literal**, and are what the audit hunts: named integrations and their
  status, enforcement paths and timing, rule types, verdicts and exit codes, evidence and
  storage, versions, security/compliance, enterprise features, unshipped flows drawn as shipped
  (diagrams and status pills count).
- Merged to core `main` but under "Unreleased" in the core CHANGELOG is **not** shipped.

Overclaims that past audits caught repeatedly; check each one present:

- Only decisions with an active **typed rule** are enforced, not "accepted decisions".
- Path selectors belong to the rule and are optional; `FORBID_DEPENDENCY` ignores paths.
- "Before a write lands" covers native write tools only; shell writes are checked at end of turn.
- Accepting a proposal is not protection activation (`/docs/decision-proposals/`).
- Claude Code has no automatic context injection; the Agent SDK does.
- Verdicts are PASS / WARN / FAIL (exit 0/1/2); only violations name a decision.
- Mneme enforces encoded constraints; it does not verify whole-system architectural conformance.
- The Decision Index records version history, lifecycle and source, never approver identity.

## 2. Verify concrete claims against the release, not memory

Sources, in order: the site's own docs (`site/docs/`, and for an agent or tool the status pill
on `site/integrations/index.html` plus that integration's page, which states its enforcement
timing), then the released package:

```bash
# v = scripts/core_version.json "minimum_version", or the new release during a core bump
v=$(python -c "import json;print(json.load(open('scripts/core_version.json'))['minimum_version'])")
venv="<scratchpad>/mneme-$v"            # session scratchpad, outside the repo
python -m venv "$venv" && "$venv/Scripts/python" -m pip install -q "mneme-hq[mcp]==$v"
export PATH="$(cygpath -u "$venv/Scripts"):$PATH"   # Git Bash; use $venv/bin on Linux/macOS
mneme --version   # must print $v
```

Never use the global `mneme` on the owner's machine: it is an editable install of core `main`
and shows unreleased behaviour. Reproduce any behaviour claim you cannot find stated in the docs.

## 3. Re-check every figure and citation

- Every external figure, quote, title and ID against the live source; record page or section.
- Chart figures from a **rendered page image**, never text extraction (pdf text has swapped bar
  labels before): `python -c "import fitz; fitz.open('r.pdf')[N].get_pixmap(dpi=150).save('pN.png')"`.
- Internal figures (benchmarks, Audit numbers) against `docs/site/evidence-contract.json` and
  the evidence they cite (`check_evidence.py`).
- Unverifiable claims are cut, not softened.

## 4. Output

```
| # | Location | Sentence (short) | Class | Implied class | Source checked | Finding |
|---|----------|------------------|-------|---------------|----------------|---------|

Figures: | # | Figure | Source + page | Matches? |

Fixes (one per flagged row):
  #N  replace: "<exact current text>"
      with:    "<exact replacement text>"

VERDICT: PASS | FIX
```

`PASS` only when no row is flagged and every figure matches. Every `FIX` row carries exact
replacement text the writer can paste, not advice.

## 5. Re-audit loop

The writer applies the fixes; a fresh audit agent (not the same one) re-runs on the changed
text until `VERDICT: PASS`. Record the final table location and verdict in the PR body
(insights: also the scope brief). For LinkedIn (`linkedin-posting` skill) and editorial
(`editorial-article` skill) drafts, "Location" is the paragraph or slide number, and the verdict
is recorded in the working notes before posting or submitting.
