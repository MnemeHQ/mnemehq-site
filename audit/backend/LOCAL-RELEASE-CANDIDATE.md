# M1.2 local release candidate — 2026-09-04

Status: **READY FOR LINUX/CI + PREVIEW**, subject to the gates below. This is a
local preparation result, not a deployment, promotion, or PR approval.

The release-candidate commit is the merge commit containing this file. Resolve it
with `git rev-parse HEAD` in the clean `fix/m12-release-fixes` worktree. Its parents
are the previous candidate `8ea9aa4e` and locally cached main
`1695bf5be23c0b5d50ae77eb0cdef86772c593d6`. No fetch was performed; newer remote
changes are outside this local verification.

## Reconciliation

- Resolved the sole remaining index conflict, `site/audit/workspace/index.html`,
  by rebuilding from the integrated frontend source. Kept main's production API
  fallback and M1.2's canonical backend contracts, lifecycle, comparison,
  guardrail validation, routing, and mobile fixes. Replaced obsolete bundle
  references with the generated assets; did not select either side wholesale.
- Preserved main's navigation, reader-intent CTA routing, and analytics changes.
  Repaired segmentation to create actual head metadata instead of editing a
  JavaScript example. All 24 routed articles now have the intended segment;
  repeating the sweep and shared-snippet sync makes no further changes.
- Shared-snippet sync leaves the Vite-owned workspace shell alone and no longer
  loads an unused dotenv file.
- Audit remains available before installation. Results, decision details, and
  protection gaps offer **Install Mneme** linking to `/docs/#quickstart`.
  Setup copy distinguishes installation, decision review, integration
  configuration, and explicitly enabling enforcement. Pilot is secondary and
  presented after setup; its existing audit/decision context handoff is retained.
  No automatic guardrail activation or enforcement behavior was added.
- Updated one stale legacy fixture assertion to agree with the existing
  vertical-slice contract: one enforceable, two partial, two guidance decisions.

## Whitespace

The reported trailing-whitespace lines use existing CRLF endings. Their original
space/tab tails and mixed-newline conventions were preserved; they were not
patch corruption. `git -c core.whitespace=cr-at-eol diff --cached --check` passes.

Vite generated one doubled CR from a CRLF HTML input. LF attributes are limited
to the workspace HTML source and generated shell, which were rebuilt cleanly.
The Windows working-tree newline scan also mistook Git checkout conversion for
289 rewrites. The new `--cached` mode checks the actual staged bytes and passes
against cached main (300 existing changed text files). Regression tests prove
that a real staged LF/CRLF rewrite still fails. No broad formatting was applied.

## Local validation

- Frontend: **31 passed**; TypeScript check and Vite production build passed.
- Separate same-origin preview frontend build passed in ignored
  `scratch/m12-preview-workspace`; production endpoint fallback remains in the
  tracked production bundle. No container build or registry access was attempted.
- Backend: **55 passed**, **3 environment-blocked tests deselected** as below.
  Tests use local fixtures and disposable SQLite, not a provisioned database.
- Site/legacy tests: **62 passed**, including four CTA regression tests, two
  staged-newline regression tests, and two legacy pipeline tests.
- Site gates passed: encoding, canonical nav/footer (296 pages), sticky nav,
  insights (160 articles), compare (13 pages), concept schema (33 pages), personas
  (3 pages), supported-language pages (6), evidence (2 blocks), install commands,
  video markup, and insights catalogue synchronization. Existing advisory
  under-meshed article warnings do not fail the insight validator.
- Mneme 0.6.0 preflight passed: compiling staged ADR bytes leaves repository
  memory unchanged; changed paths and 291 site text files passed enforcement
  checks. Staged bytes avoid Windows checkout conversion changing ADR hashes.
- No unmerged entries remain. The candidate commit must leave a clean tracked
  worktree; ignored build scratch is retained as local evidence.

## Environment-blocked tests and mandatory next gate

All three belong to `audit/backend/tests/test_safe_extract.py`:

1. `test_materializes_internal_file_symlink`
2. `test_rejects_symlink_that_escapes_repository`
3. `test_removes_internal_directory_symlink`

The previous Windows run skipped them after Windows denied symlink creation.
This run explicitly deselects those same tests, avoiding another denied action.
No permission changes, emulation, or security bypass was attempted.

The checked-in `.github/workflows/audit-release-check.yml` runs on Ubuntu for
every pull request to main and every push to main. It runs the complete backend
suite with no deselection. The symlink helper fails on non-Windows platforms if
real symlinks cannot be created, so Linux cannot silently skip these tests.
The workflow also runs legacy/site regressions, frontend tests, and both builds.

**Before merge, require that workflow to pass for this exact candidate SHA,
including all three symlink tests.** Workflow execution and remote branch
protection settings were not accessed or verified locally. A real coordinated
preview journey remains a separate release gate under `PREVIEW-CHECKLIST.md` and
requires separate authorization. Local success is not preview E2E evidence.

## Execution provenance

- Change author: agent
- Agent: codex
- Agent model: not-exposed
- Agent session: not-exposed
- Task origin: chatgpt
- Human owner: TheoV823

No cloud commands, credential retrieval, deployment, remote push, or PR #90
mutation were performed during this local preparation.
