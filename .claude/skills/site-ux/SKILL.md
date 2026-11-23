---
name: site-ux
description: Use when designing, building or reviewing any visual or interactive piece of mnemehq.com (a new section, page layout, tool, calculator, checker, form, card grid, table, diagram or CTA block), when a request says "make it look good", "redesign", "improve the UX", or when the frontend-design skill is also loaded for this repository.
---

# mnemehq.com UX: extend the system, never invent one

mnemehq.com already has a design system: tokens in `site/assets/css/base.css`, a colour contract
in `docs/site/cta-system.md`, typography and diagram rules in `PUBLISHING.md`, and interaction
principles in `PUBLISHING.md`, "Interaction and UX design standards". New work reuses them. If
this file and those disagree, those win; fix this file.

## Relation to `frontend-design`

`frontend-design` (plugin skill, do not edit) asks for a bold, distinctive aesthetic direction.
On this site the direction is already chosen. Use it only for craft inside the system (spacing,
rhythm, restraint). These house rules override it:

| `frontend-design` tendency | House rule here |
|---|---|
| Pick a new palette, fonts, motif | Use the tokens and the three families below. No new hex values in page CSS except a documented beat surface. |
| Avoid "templated" numbered sections and eyebrow labels | Numbered section markers (`.layer-num` `01`, `02`... in DM Mono, sage) and uppercase DM Mono eyebrows (`.section-eyebrow`, `.hm-section-label`, `.tool-hero-tag`, `.audit-hero-tag`) are house style. Keep them. |
| Distinctive display type on headings | Instrument Serif on the hero `h1` and on long-form section heads as `base.css` sets them; never as a new display face. Subheads are Inter semibold. |
| Bold accent colour for emphasis | Colour is a role, not decoration (below). |
| Motion and scroll effects for delight | One restrained load sequence at most, and none under `prefers-reduced-motion: reduce`. |
| Illustrations and decorative SVG | Diagrams are evidence: reuse a primitive from `site/assets/css/diagrams-v2.css`. No ornament. |

## What to reuse

**Tokens** (`base.css` `:root`): `--bg #0c0c0d`, `--surface`, `--surface2`, `--border`,
`--border2`, `--text`, `--muted`, `--quiet`, `--accent` (sage), `--accent-dim`, `--teal`,
`--action` (coral), `--action-soft`, `--action-dim`. The site is dark-only.

**Colour roles** (`docs/site/cta-system.md` section 3): coral fill = the cluster's one primary
action; neutral outline = secondary; teal = tertiary link / technical path; sage = success,
evidence and status only, never a button.

**Typography** (`PUBLISHING.md`, Deploy and asset conventions): Inter body and UI, DM Mono for
code, labels, eyebrows and buttons, Instrument Serif as above.

**Components, and where to copy them from.** Only `base.css`, `integration-system-v2.css`,
`diagrams-v2.css` and `home-v2.css` are shared files. The `.tool-*`, `.result-*`, `.layer-*`,
`.audit-*` and `.pricing-*` rules live in each page's inline `<style>`: copy the rules with the
markup into the new page's `<style>`, unchanged, so every class still resolves.

| Need | Reference |
|---|---|
| Buttons, CTA band, end block, install module | `base.css`: `.cta-btn-primary`, `.cta-band`, `.cta-block-end`, `.install-module`; placement in `cta-system.md` section 4 |
| Interactive tool (input → result) | `site/tools/adr-checker/`: `.tool-form`, `.tool-error[role=alert]`, `.result-*`, focus to result title, `tool_*` events (it has no `aria-live` region yet; add one in new work) |
| Hub with grouped, numbered sections and status pills | `site/integrations/index.html`: `.layer`, `.layer-num`, `.int-card`, `.int-status`, `.status-key` |
| Detail page reading layout, callouts, proof-before-CTA | `site/assets/css/integration-system-v2.css` (Claude Code page is the reference) |
| Product/landing sections, screen previews | `site/audit/index.html`: `.audit-section`, `.screen-card`, `.works-grid` |
| Pricing cards, honest status labels, boundary table | `site/pricing/index.html`: `.pricing-card`, `.status-today` / `.status-direction`, `.table-wrap` |
| Homepage beats, verdict card, FAQ | `site/assets/css/home-v2.css` (homepage only; do not link it elsewhere) |
| Diagrams | `site/assets/css/diagrams-v2.css` primitives |
| Nav, footer, hamburger, breadcrumb, page switcher | `site/_snippets/`, synced by `scripts/sync_shared.py`; never hand-edit a page copy |

Shared-asset changes follow `PUBLISHING.md`: a changed CSS or image ships under a new filename;
a `base.css` change bumps its `?v=` on every page. Every `class=` must resolve to a rule
(`seo_check.py` `style.classes`).

## Checklist for interactive pieces

Build each item; do not leave it for review to find.

1. **Flow:** one primary action per cluster, a visible path input → result → next step.
2. **Selection state:** chosen options look chosen (not by colour alone) and use
   `aria-pressed`, `aria-checked` or `aria-selected` as fits the control.
3. **Live result:** results render into a region with `aria-live="polite"` (errors use
   `role="alert"`), and progress is shown while waiting.
4. **Focus:** after submit, move focus to the result heading (`tabindex="-1"`); on error, back
   to the field. Visible focus ring on every control; logical tab order.
5. **Error and empty states:** say what happened and what to do, in plain words. Empty input
   gets its own message, not a failed request.
6. **No-JS fallback:** the page still explains the tool and links to the static alternative
   (docs page, Audit, install).
7. **375px:** no horizontal scroll, targets at least 44px, inputs readable without zoom.
8. **Dark and light OS settings:** the site is dark-only, so check native controls,
   autofill and scrollbars do not render light-on-light when the OS is in light mode
   (`color-scheme: dark` where needed).
9. **`prefers-reduced-motion`:** no animation or smooth scroll under `reduce`.
10. **Analytics:** events and parameters exactly per `docs/site/gtm-tagging-requirements.md`
    (canonical `cta_click`, `code_copy`, or a documented tool event set like section 11),
    dev-host suppression, never user content in a parameter. Links and buttons use `cta_click`
    through `site/_snippets/cta-analytics.js`. A widget that needs its own events gets a new
    contract section in that file (modelled on section 11), with the GTM container change
    listed as pending.

## UX rubric (/50)

Score in the in-app browser (`mcp__Claude_Browser__*`) from the local preview
(`preview_start` with name `site`, from `.claude/launch.json`, port 8765), at desktop,
`resize_window` mobile (375px) and with `colorScheme` dark and light. Each criterion 1-5.
**Pass: 40 or more, and no criterion below 3.** Record the table in the PR body.

| # | Criterion | 5 looks like |
|---|---|---|
| 1 | 5-second clarity | A cold visitor can say what the page is and what to do next |
| 2 | Flow and feedback | Every action has a visible, prompt response; progress shown |
| 3 | Information scent | Labels and links predict where they lead |
| 4 | Site consistency | Only house tokens, components and roles; looks like its siblings |
| 5 | Hierarchy and readability | One focal point, one dominant action, measure under ~75ch |
| 6 | Accessibility | Keyboard-complete, ARIA live/roles right, contrast AA, focus visible |
| 7 | Mobile | Works at 375px with no loss of function |
| 8 | Resilience and performance | Error, empty and no-JS states handled; no layout shift; no new heavy asset |
| 9 | Honesty about status and limits | Status labels and limits match the shipped product (`claim-audit`) |
| 10 | Path to next step | The next step fits the visitor's intent (`cta-system.md` placement) |

Have a fresh agent, not the builder, do the scoring when the piece is new.

## Common mistakes

- Adding a new accent colour or font "for this one section".
- A sage button, or two coral buttons in one cluster.
- Removing eyebrows or section numbers because another skill called them generic.
- A result that appears without an `aria-live` region or focus move, so screen readers miss it.
- Copying `home-v2.css` patterns onto other pages instead of the `base.css` equivalents.
- Editing nav or footer markup in a page instead of `site/_snippets/` + `sync_shared.py`.
