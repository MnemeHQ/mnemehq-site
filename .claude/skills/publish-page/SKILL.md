---
name: publish-page
description: Use when adding or substantially changing a non-insight page on mnemehq.com (docs or reference page, how-to guide, setup or install page, integration page, comparison page, /for/ persona page, concept page, supported-language page, tool or landing page), or when asked to "ship", "publish" or "add a page" outside /insights/.
---

# Publish a non-insight page

End to end, from contract to verified live page. Rules live in `AGENTS.md`, `PUBLISHING.md` and
the runbooks it points to; this skill is the order of operations. If this file and those
disagree, those win; fix this file. Insights use `publish-insight` instead.

## Agent orchestration

The main session orchestrates, owns every user confirmation, and never delegates a merge.
Same split as `publish-insight`: judgment and prose to Opus, mechanical steps to Sonnet, every
gate checked by an agent that did not produce what it checks.

| Step | Agent (`model`, `effort`) | Output |
|---|---|---|
| Build | `opus`, `medium` | page, metadata, registration edits, slop score, lint result |
| Register + validate | `sonnet`, `medium` (or inline if a few calls) | OG card, sitemap, llms, nav sync, all checks green |
| Cold read | `sonnet`, `low`, fresh | built page only → what it gets me, followable?, unclear terms, confusing sentences |
| Claim audit | `opus`, `medium`, fresh | `claim-audit` skill → table + `VERDICT` |
| UX score (new layout or interactive piece) | `sonnet` or `opus`, fresh | `site-ux` rubric /50 |

Loop Build ← cold read / audit / UX findings until all pass. Audit agents read branches with
`git diff origin/main...<branch>` or `git show`, never `git checkout` in a shared worktree.

## 1. Pick the contract

| Page | Contract and tooling |
|---|---|
| Concept `/concepts/<slug>/` | `docs/site/concept-publication.md` (hub card, `hasPart`, SVG or `svg-omitted.txt`); `PUBLISHING.md` "Conceptual authority" (1000+ words, contrast claim, terminology lock); `check_concepts.py`, `check_concepts_schema.py` |
| How-to `/docs/how-to/<slug>/` | Source in `templates/howto/<slug>.html`, fixture in `tests/howto/<slug>/`; `build_howto_page.py`; `check_howto.py`; `run_howto_fixtures.py --only <slug>` against the released version |
| Docs / reference `/docs/<slug>/` | Add to `DOCS` in `scripts/sync_docs_nav.py`, run it, then `--check` |
| Integration `/integrations/<slug>/` | `integration-system-v2.css` layout (Claude Code page is the reference); add to `INTEGRATIONS` in `sync_integrations_nav.py` and to the matching numbered layer on `/integrations/`; support level stated literally |
| Comparison `/compare/<slug>/` | In `site/compare/index.html`: hub card, summary row, `hasPart`, `ItemList`, byline counter, sitemap, `comparison` OG record; `check_compare.py` |
| Persona `/for/<role>/` | `PUBLISHING.md` "Persona / buyer pages" (audience primitives, CTO page order and CTA rule); `check_for.py` |
| Supported language | `check_supported_languages.py` |
| Page with first-party figures | `docs/site/evidence-contract.json`; `check_evidence.py` |
| Any CTA | `docs/site/cta-system.md` placement and labels; `check_drift_audit_cta.py`, `check_funnel_wiring.py` |
| Any new layout or interactive piece | `site-ux` skill |

A category or tagline change needs ADR-001/013/014 amendments in `MnemeHQ/mneme` first.

## 2. Build

- Start from the closest published sibling in the same directory (copy its `index.html`), not
  from scratch: `new_article.py` is insights-only. Before choosing a slug, run
  `python scripts/find_overlap.py "<title>" --keywords "<kw1>,<kw2>"` and `ls` the directory;
  extend an existing page rather than publish a near-duplicate.
- Head: `<title>`, meta description, self canonical, `og:*` and `twitter:*` (all six image tags
  from `PUBLISHING.md` "OG images"), `article:published_time` where the cohort uses it.
- JSON-LD: the cohort's graph (concept: BreadcrumbList + TechArticle + DefinedTerm + FAQPage;
  compare and persona: BreadcrumbList + Article + FAQPage). Breadcrumb depth mirrors URL depth,
  visible and in JSON-LD; every parent segment has an `index.html`.
- Nav and footer come from `site/_snippets/`: run `python scripts/sync_shared.py`, never
  hand-edit them.
- Prose follows the house voice: terminology lock, no "bottleneck", no connective em dashes,
  domain `mnemehq.com`.
- Working drafts stay outside `site/`.

## 3. Register

1. OG: add a record for the page path to `site/og/cards.yaml` (family derives from the path;
   headline 4-7 words; copy budgets in `AGENTS.md`). Render with
   `python scripts/render_og.py --strict --out site --only <path>/`. Changing an existing card:
   next free `card: og-vN.png`, then `python scripts/sync_og_meta.py`, update JSON-LD `image`,
   revert unrelated pages it touched.
2. `site/sitemap.xml`: add the `<url>`.
3. `site/llms.txt` (and `llms-full.txt` if the section is listed there): add a line under the
   section that lists its siblings ("Compare pages", "Integration pages"...). An integration
   line states its status (shipped, validated, experimental, planned, research) literally.
4. Hub registration from the contract table, plus at least one incoming internal link.

## 4. Validate

Run the cohort's checks named in the step 1 table (`check_compare.py`, `check_for.py`,
`check_concepts.py` + `check_concepts_schema.py`, `check_howto.py`, `sync_docs_nav.py --check`,
`sync_integrations_nav.py --check`, `check_supported_languages.py`, `check_evidence.py`),
then the site-wide set:

```bash
python scripts/render_og.py --strict --dry-run
python scripts/check_og_coverage.py
python scripts/lint_og_voice.py
python scripts/check_og_render_unique.py
python scripts/check_nav_footer.py
python scripts/check_sticky_nav.py
python scripts/check_install_command.py
python scripts/check_stale_mcp_claims.py
python scripts/sync_core_version.py --check
python scripts/check_agent_discovery.py
python scripts/check_line_endings.py
python scripts/check_encoding.py site scripts
python scripts/seo_check.py --only <section>   # warn-only; class hygiene and word floors are review items
```

Edit site files in binary mode from Python, not `sed -i` in Git Bash (flips CRLF/LF).

## 5. Gates (PUBLISHING.md "Pre-merge review gates")

1. `stop-slop` score at least 35/50.
2. `python scripts/lint_prose.py <built page>`: zero errors; fix or justify every warning.
3. Cold read by a fresh agent given only the built page.
4. `claim-audit` skill: `VERDICT: PASS`.
5. `site-ux` rubric at least 40/50, no criterion below 3, when layout or interaction changed.

Record every result in the PR body's Validation section.

## 6. PR, merge, deploy

1. Branch with a purpose prefix (`site/`, `feat/`, `fix/`), never `claude/`. Confirm
   `git branch --show-current` before each commit.
2. PR body from `.github/PULL_REQUEST_TEMPLATE.md`, with the Execution provenance block
   (`AGENTS.md`). `check_pr_provenance.py` runs in CI.
3. Merge only on the user's go-ahead, squash, after CI is green.
4. Deployed means all of: a successful `Deploy site to mnemehq.com` run for the exact `main`
   SHA (merge SHA from `gh pr view <n> --json mergeCommit`; the run from
   `gh run list --workflow deploy-site.yml --commit <sha>`, wait with `gh run watch <id>`), and `git ls-remote --tags origin
   site-deployed` resolving to that SHA (not a local tag, which goes stale).
5. Live verification: `curl` the URL with a cache-busting query, then open it in the browser
   with one too. Check status 200, canonical, `og:image` returns the card.
6. Report authorship, merge, deployment and live check as separate facts. If something stopped
   short, say which step is left.
