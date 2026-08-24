# AGENTS.md

Notes for AI agents working in this repository.

## OG images are generated, not hand-made

Every page's `og.png` is produced by the deploy/asset pipeline:

1. Create an HTML template `site/og-<slug>.html` (1200x630, dark theme — copy an existing `og-integration-*.html` as the base).
2. Register it in `TEMPLATE_MAP` in `scripts/generate_og_images.py`:
   `"og-<slug>.html": "<page-dir>/og.png",`
3. Render with Playwright (`python scripts/generate_og_images.py` renders all; a targeted one-off render of just the new template is fine).

Never reference an `og.png` in meta tags without the template + TEMPLATE_MAP entry existing.
