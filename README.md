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

Each check has a path-filtered PR workflow. These workflows remain inactive
until GitHub Actions is enabled during the later repository-validation step.

## Deployment

`scripts/deploy_site.py` — invoked by the manual **Deploy site to mnemehq.com**
workflow — delta-uploads `site/` via the cPanel API (delta = `git diff
site-deployed..HEAD`), purges the Cloudflare cache, strictly
fingerprint-verifies each changed **HTML page**, runs a best-effort
(status-only) health probe over the rest of the sitemap, advances the
`site-deployed` tag, and submits IndexNow. Non-HTML assets — CSS, JS, fonts,
images — are uploaded without content verification.

Deployment ownership is being cut over from the core repository in stages:
GitHub Actions is currently **disabled** on this repository, the deploy
workflow is **manual-only**, and no deploy secrets or runner are configured —
this repository cannot deploy until the cutover step completes.

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
