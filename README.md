# mnemehq.com — website source

Source and tooling for the public Mneme HQ website, [mnemehq.com](https://mnemehq.com).

The Mneme product itself — the engineering-governance package (`mneme-hq`), CLI,
enforcement engine, benchmarks and agent integrations — lives in
[MnemeHQ/mneme](https://github.com/MnemeHQ/mneme). This repository holds only
the website and its deployment/validation tooling, extracted from that
repository with filtered history.

## Publishing governance

[`PUBLISHING.md`](PUBLISHING.md) is the canonical source of publishing and deployment
governance for mnemehq.com: the current rules for insights, concepts, persona pages, OG
images, deployment, and asset conventions. Step-by-step operational runbooks live under
[`docs/site/`](docs/site/).

## Layout

```
site/                   the static site exactly as deployed
  _snippets/            shared nav/footer/head sources (inlined into pages by sync_shared.py)
  assets/               css, js, self-hosted fonts (+ fonts/licenses/), OG sources
scripts/                deploy, validation and asset tooling
.github/workflows/      PR validators + the manual deploy workflow
```

## Checks (stdlib-only)

```
python scripts/check_encoding.py site scripts
python scripts/check_nav_footer.py
python scripts/check_sticky_nav.py
python scripts/check_insights.py
python scripts/check_compare.py
python scripts/check_concepts_schema.py
python scripts/check_for.py
python scripts/check_supported_languages.py
python scripts/test_deploy_verify.py
```

Each check runs as a path-filtered PR workflow. GitHub Actions is enabled on
this repository and the applicable workflows run on every relevant PR.

## Mneme dogfooding

This repository uses Mneme to govern its own changes. The active decisions in
[`docs/adr/`](docs/adr/) compile into the tracked
[`project_memory.json`](.mneme/project_memory.json); detailed publishing rules
remain canonical in [`PUBLISHING.md`](PUBLISHING.md). The seven original
website ADRs are mirrored unchanged under [`docs/adr/history/`](docs/adr/history/)
for local provenance and remain superseded, so they are not compiled. The
**Mneme governance preflight** workflow installs the published `mneme-hq`
distribution, recompiles the ADR corpus to catch stale memory, and applies
`mneme check --mode strict` to each pull request and push-to-main change set.
Run the same local preflight with:

```
python -m pip install "mneme-hq>=0.5.0"
mneme adr import docs/adr --memory .mneme/project_memory.json --apply --update-existing
git diff --name-only HEAD^ HEAD > .mneme/changed-paths.txt
mneme check --memory .mneme/project_memory.json --input .mneme/changed-paths.txt --query "Assess these changed paths against Mneme HQ website publishing, shared site chrome, deployment, and validation governance." --top 10 --mode strict
```

`mneme-hq` is the distribution name; the installed CLI remains `mneme`.

## Deployment

`scripts/deploy_site.py` — run by the **Deploy site to mnemehq.com**
workflow — uploads `site/` via the cPanel API (a delta deploy uploads the
added/copied/modified `site/` paths since the `site-deployed` tag,
`git diff --diff-filter=ACM site-deployed..HEAD`; a full deploy uploads the
files present under `site/` when no tag exists), purges the Cloudflare cache,
strictly fingerprint-verifies each changed **HTML page**, runs a best-effort
(status-only) health probe over the rest of the sitemap, advances the
`site-deployed` tag, and submits IndexNow. Non-HTML assets — CSS, JS, fonts,
images — are uploaded without content verification.

MnemeHQ/mnemehq-site owns production deployment of mnemehq.com. `deploy-site.yml`
runs on a path-filtered push to `main` (touching `site/**` or
`scripts/deploy_site.py`), on manual `workflow_dispatch`, and on a daily
schedule at 06:00 UTC. Deploys run on the dedicated `mnemehq-site-deploy`
self-hosted runner; the required cPanel and Cloudflare credentials are supplied
from configured repository secrets and variables (values are never committed).
See [PUBLISHING.md](PUBLISHING.md#deployment-ownership).

## Dependencies

The deploy path and all validators use only the Python 3.12 standard library.
Asset regeneration (OG images, demo GIFs, screenshots) additionally needs:

```
pip install -r requirements.txt   # Pillow, Playwright
python -m playwright install chromium
```

## Licence

- Implementation (markup structure, CSS, JS, scripts, workflows): MIT — see [LICENSE](LICENSE).
- Editorial content, original visuals, logos and brand assets: all rights
  reserved — see [CONTENT-LICENSE.md](CONTENT-LICENSE.md).
- Third-party fonts and services: see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
