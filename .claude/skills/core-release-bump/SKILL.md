---
name: core-release-bump
description: Use when MnemeHQ/mneme (the mneme-hq package) has shipped a new release, when a `core-release-drift` issue is open, when the agent-discovery or MCP tool catalog check fails on a version mismatch, or when asked to "bump the site to mneme-hq X", "document the new core version" or "update install commands".
---

# Bump the site after a mneme core release

No core release step updates the site. The daily `external-trust` job in
`.github/workflows/agent-discovery-check.yml` compares `scripts/core_version.json` with PyPI, the
core `server.json` and the MCP Registry, and opens one issue labelled `core-release-drift`.
That issue is the start signal. A bump is never only a version string: the release may change
behaviour the docs describe. One PR covers it all.

Reference: the 0.11.0 bump, `git show --stat 5028eb50`, for the file spread.

## 1. Detect and scope

```bash
gh issue list --label core-release-drift --state open
python scripts/check_agent_discovery.py --online   # Registry fetch flakes; re-run before trusting a failure
python scripts/sync_core_version.py --check
python scripts/check_mneme_version_parity.py       # audit backend floor; needs audit/backend reqs installed
```

Read the core CHANGELOG entry for the new version (`gh release list -R MnemeHQ/mneme`, then
`gh release view <tag> -R MnemeHQ/mneme`)
and list every behaviour change. Only released entries count; "Unreleased" is not shipped.

Make a scratch venv with the **new** version (`claim-audit` skill, step 2, with `v=<new>`;
`core_version.json` still names the old one until step 2 below). Never use the global `mneme`:
it is core `main`.

`check_mneme_version_parity.py` checks that the audit backend floor is satisfiable; it keeps
passing when the floor is left at the old version, so it is a sanity check, not a bump signal.
If no drift issue exists yet (the daily job has not run), work without one and say so in the PR.

## 2. Update versions and generated artifacts

On a `site/` branch (for example `site/mneme-hq-<new>`):

1. `python scripts/sync_core_version.py <new>`: manifest, every active install command in site
   HTML and `README.md`. Historical release notes are left alone on purpose.
2. Hard-coded versions the sync misses:
   `git grep -n -E "<old-version>|mneme-hq(\[mcp\])?==" -- site templates tests README.md`.
   Expect hits in `site/docs/`, `site/integrations/`, `site/demo/`, `site/compare/`, `site/qa-glossary/`,
   `site/llms.txt`, `site/llms-full.txt`, how-to templates and fixtures (including the pin in
   `tests/howto/fail-pull-request-that-breaks-adr/.github/workflows/mneme-decisions.yml`). Change "current version" statements; keep "added in <old>" history.
3. MCP catalog, from the venv: `python scripts/export_mcp_tool_catalog.py`, then `--check`.
4. Agent skill: hand-edit pins in `site/.well-known/agent-skills/mneme-decision-mcp/SKILL.md`,
   then recompute `digest` in `site/.well-known/agent-skills/index.json`:
   `python -c "import hashlib,pathlib;print('sha256:'+hashlib.sha256(pathlib.Path('site/.well-known/agent-skills/mneme-decision-mcp/SKILL.md').read_bytes()).hexdigest())"`.
5. How-to fixtures, with the venv first on PATH: `python scripts/run_howto_fixtures.py --update`,
   review every changed `expected/` file, then `python scripts/build_howto_page.py` and
   `python scripts/check_howto.py`.
6. Audit backend floor in `audit/backend/requirements.txt` only if the owner wants the Audit on
   the new engine; its production lock and Cloud Run deploy are a separate, owner-approved step.

## 3. Rewrite changed behaviour

For each CHANGELOG change, find the prose that describes the old behaviour (`git grep` the
command, flag, rule type or error) across `site/docs`, `site/integrations`, `site/qa-glossary`
and how-to templates. Rewrite it from the venv's real output, not from the CHANGELOG wording.
Update capability and status statements that the release moves (an integration from
experimental to shipped changes its `/integrations/` pill and `llms.txt` line too).
`check_stale_mcp_claims.py` guards the 0.10.0 MCP storage change; add a pattern there if this
release retires another phrase.

## 4. Validate and gate

```bash
python scripts/sync_core_version.py --check
python scripts/check_install_command.py
python scripts/check_stale_mcp_claims.py
python scripts/check_agent_discovery.py
python scripts/export_mcp_tool_catalog.py --check
python scripts/check_howto.py
python scripts/check_nav_footer.py
python scripts/check_line_endings.py
python scripts/check_encoding.py site scripts
```

Then the gates: `claim-audit` on every changed claim (fresh agent, the new version's venv);
rewritten paragraphs also get `stop-slop` >= 35, `lint_prose.py` zero errors, and a cold read
(`PUBLISHING.md`, "Pre-merge review gates").

## 5. Ship

One PR, purpose-prefixed branch, Execution provenance block, `Closes #<drift issue>` when one
exists. Merge on
the user's go-ahead (squash), then deployment evidence and live check exactly as in
`publish-page` step 6. The drift issue closes only when the next `external-trust` run passes.
