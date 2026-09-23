# AGENTS.md

Notes for AI agents working in this repository.

## Branch naming

Use purpose-based prefixes: `feat/`, `fix/`, `site/`, `ci/`, `docs/`, or `refactor/`.
Keep names short and kebab-case. Do not use an agent name such as `codex/` as the
branch prefix; record agent identity in execution provenance instead.

## OG images are generated, not hand-made

Every page's OG card is produced from a manifest, not a hand-built template:

1. Card content lives in `site/og/cards.yaml`, one record per page path. A page's
   family (`editorial`, `integration`, `proof`, `comparison`, `brand`) is derived
   from its URL path, and an Editorial motif is derived from a topic rule against
   the slug; both are overridable per record.
2. Render with `python scripts/render_og.py --strict --out site`. Cards land at
   `<page-dir>/og-v2.png` (`og-v2.png` at the site root for the homepage).
3. Per `PUBLISHING.md:105`, a changed static asset ships under a **new**
   filename, never overwritten in place — this is why the card file is
   `og-v2.png` and not a rewritten `og.png`.

Copy budgets (enforced by the manifest resolver and the voice lint):

- Headline target is 4-7 words; 8-10 words warns; over 10 is a hard failure.
- Editorial cards carry no secondary copy at all.
- Brand cards have secondary copy off by default.
- Integration cards get at most one short mechanism line.
- Proof and Comparison cards convey detail through structured `rows`/`boxes`,
  not secondary copy.

A new or changed card must pass, in order:
`python scripts/render_og.py --strict --dry-run`,
`python scripts/check_og_coverage.py`,
`python scripts/lint_og_voice.py`,
`python scripts/check_og_render_unique.py`.

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
