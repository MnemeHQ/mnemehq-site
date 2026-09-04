# AGENTS.md

Notes for AI agents working in this repository.

## Branch naming

Use purpose-based prefixes: `feat/`, `fix/`, `site/`, `ci/`, `docs/`, or `refactor/`.
Keep names short and kebab-case. Do not use an agent name such as `codex/` as the
branch prefix; record agent identity in execution provenance instead.

## OG images are generated, not hand-made

Every page's `og.png` is produced by the deploy/asset pipeline:

1. Create an HTML template `site/og-<slug>.html` (1200x630, dark theme — copy an existing `og-integration-*.html` as the base).
2. Register it in `TEMPLATE_MAP` in `scripts/generate_og_images.py`:
   `"og-<slug>.html": "<page-dir>/og.png",`
3. Render with Playwright (`python scripts/generate_og_images.py` renders all; a targeted one-off render of just the new template is fine).

Never reference an `og.png` in meta tags without the template + TEMPLATE_MAP entry existing.

## Agent execution provenance

Every pull request must record who actually produced the change. Git author identity is not sufficient because agent work is commonly committed under the human owner's Git identity.

Use the PR template's `Execution provenance` block. Required fields:

- `Change author`: `human`, `agent`, or `mixed`.
- `Agent`: the concrete agent surface (`codex`, `claude-code`, `kiro`, `chatgpt-work`, etc.), or `none` for human-only work.
- `Agent model`: model identifier when exposed; `not-exposed` is acceptable when the tool does not expose it; `n/a` only for human-only work.
- `Agent session`: stable session ID or share/work URL when available; `not-exposed` is acceptable when unavailable; `n/a` only for human-only work.
- `Task origin`: where the task was scoped (`chatgpt`, `claude`, `local`, `manual`, etc.).
- `Human owner`: GitHub username responsible for review/promotion.

When an agent creates commits directly, also append commit trailers where practical:

```text
Agent: codex
Agent-Model: gpt-5.6-sol
Agent-Session: cx_...
Task-Origin: chatgpt
Human-Owner: TheoV823
```

The PR body is the durable source of truth because squash merges may collapse or discard individual commit trailers.

### Deployment claims

Do not report a site change as deployed merely because a PR was merged or a deployment was started.

Canonical deployment evidence is:

1. a successful `Deploy site to mnemehq.com` workflow run for the exact `main` SHA,
2. `site-deployed` resolving to that exact SHA after the deploy, and
3. live verification when the task explicitly requires it.

Agent authorship, human promotion, deployment, and worktree cleanup are separate lifecycle facts. Report each independently. If usage/session limits interrupt the task, leave the remaining lifecycle step explicit rather than inferring completion.
