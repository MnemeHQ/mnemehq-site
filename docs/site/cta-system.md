# CTA System — placement, hierarchy and rollout

Status: adopted plan. Templates live in `templates/ctas.css` + `templates/cta-components.html`.
Built on the shared token layer in `site/assets/css/base.css` (synced site-wide by
`scripts/sync_shared.py`), the same system as `site/_snippets/`.

---

## 1. The one-line rule

Every page expresses Mneme's actual progression:

> **prove it → run it → apply it to a real repository**

Concretely: **Install → Demo → Pilot** on developer surfaces; reversed to
**Pilot → Demo → Install** only where the visitor has shown team-level intent.
Never equal buttons — always **one filled, one outlined, one text link**.

**"One coral action" = one primary intent per page.** The same intent may repeat
at hero, mid-page and ending — that is correct sequencing, not competition.
The hard constraint is per **cluster**: one filled coral button per CTA cluster,
never two in the same view.

## 2. Canonical funnels

| Visitor             | Journey                                            | Outcome                        |
| ------------------- | -------------------------------------------------- | ------------------------------ |
| Developer/evaluator | Install → quickstart → first check → demo          | OSS activation                 |
| Engineering team    | Evidence/use case → drift audit → complimentary pilot | Design-partner validation   |

Newsletter stays at article endings/footer only. Contact routes technical
queries to GitHub Discussions and team evaluations to the pilot page.

### GA4 baseline (run before rollout; informs sequencing, does not block P0)

Pull last 90 days with last-28-days comparison:

- Landing-page sessions by page/template
- Homepage paths into `/docs/`, `/demo/`, `/pilot/`
- Outbound clicks to GitHub and PyPI
- Pilot page views, form starts, submissions, success rate
- Engagement rate and the ~90% scroll event
- Device split, especially mobile conversion
- Source/medium split: developer-intent vs team-intent traffic
- Highest-traffic integration, insight and use-case pages

Output: a table of **page traffic × current next-page path × current conversion
proxy**, used to decide whether PR 2 is demos/integrations or team pages.
Traffic is currently too modest for A/B testing — use GA4 for baseline and
prioritization only.

Known GA4 limitations to plan around:

- Standard `scroll` fires near 90% — it cannot validate mid-page CTA placement.
- Hash navigation (`/docs/#quickstart`) may not produce a new page_view, so
  install clicks must be measured via the explicit `cta_click` event.

## 3. Visual semantics (colour = role, not funnel stage)

| Token                | Hex        | Meaning                                    |
| -------------------- | ---------- | ------------------------------------------ |
| `--action` (coral)   | `#ea735e`  | The page's ONE primary conversion action   |
| `--action-dim`       | `#c95a46`  | Hover state for primary                    |
| Neutral outline      | `var(--border2)` / `var(--text)` | Secondary action     |
| Text link            | mint `#8be0c8` | Tertiary action, editorial references  |
| Lime (`--accent`)    | `#c8f060`  | Success, shipped/validated status, evidence — **never a button fill** |

Contrast (all pass WCAG AA): black-on-coral 6.76:1 · black-on-lime 14.98:1 ·
mint-on-dark 12.66:1 · grey-on-dark 8.31:1.

Button spec: ~14px text, 44–48px height, DM Mono labels, focus ring per base.css.

## 4. Placement matrix — what goes where and WHY

The "why" column is the contract: if a placement can't justify itself against
this table, it doesn't ship.

| Page type            | Primary (coral filled)         | Why primary here                                              | Secondary (outline)      | Tertiary (text link)    |
| -------------------- | ------------------------------ | ------------------------------------------------------------- | ------------------------ | ----------------------- |
| Homepage hero        | **Install Mneme**              | Installation is product activation; demo is proof, not the ask | Run the 2-minute demo    | View source on GitHub → |
| Homepage team section | Request a pilot               | Only section where visitor intent is explicitly team-level     | Run the demo             | Install                 |
| Docs / quickstart    | Copy install command           | Docs visitors are mid-activation; remove all friction          | Run your first check     | GitHub source           |
| Integration hub      | Install Mneme                  | Hub browsers are evaluating fit; install is the low-cost step  | View supported tools     | Request a pilot         |
| Integration detail   | **Set up Mneme with [tool]**   | Tool-specific intent is the highest-signal developer moment    | View evidence/source     | Request a pilot         |
| Demo hub             | Install Mneme (right after flagship proof) | Proof just landed; convert uncertainty into action immediately | View another demo | Request a pilot |
| Demo details         | Install Mneme (~50–60% down)   | Same as hub but placed at proof density peak, not 75%          | View source              | Request a pilot         |
| Use-cases hub        | See the demo after first proof | First use-case creates the problem; demo resolves it           | Request a drift audit    | —                       |
| Use-case detail      | Install via quickstart         | Never label a GitHub link "Install" — destination must match   | View GitHub              | Pilot                   |
| Insights articles    | Install Mneme (~45–60% down)   | Long-form readers hit proof mid-article, not only at the end   | See the demo             | Newsletter (end only)   |
| Concept pages        | See this enforced (soft link)  | Conceptual readers need one concrete next step, not a form     | Relevant demo            | —                       |
| Benchmark            | Run the benchmark (top)        | Page IS an action; GitHub scenarios at 89% was wasted intent   | Contribute a scenario    | —                       |
| `/for/` + role pages | **Request a pilot**            | Team-intent pages: audit/pilot is the correct first ask        | Run the demo             | Install                 |
| Team-heavy use cases | Request a pilot                | Multi-agent/compliance/platform readers evaluate for teams     | See relevant demo        | Install                 |
| Pilot page           | Submit pilot request           | Single-purpose conversion page                                 | See qualification criteria | Install               |
| Pricing (if kept)    | Request a pilot for teams      | No mature tiers exist yet — OSS + pilot framing only           | Install open source      | —                       |
| Global nav           | Request a pilot — **outline everywhere** | Filled lime competed with the page's own primary before content loaded | — | — |

### Position rules

1. Above-the-fold cluster on every template family page (hero or breadcrumb+H1 area).
2. One mid-page action band on long pages, placed **after the first substantial
   proof/evidence section**. The 45–60%-of-scroll figure is a heuristic from the
   audit, not a rule — evidence position wins when the two disagree.
3. One end-of-page block; never more than three destinations there.
4. Every shipped integration page gets its setup CTA — no exceptions.

## 5. Components

Primitives live **in `base.css` itself** (no separate stylesheet, no override
layer); markup partials in `templates/cta-components.html`:

| Component          | Class                  | Used for                                   |
| ------------------ | ---------------------- | ------------------------------------------ |
| Primary button     | `.cta-btn-primary`     | The single coral action per cluster        |
| Secondary button   | `.cta-btn-outline`     | Demo / source / criteria links             |
| Tertiary link      | `.cta-link`            | GitHub, editorial hops                     |
| Cluster wrapper    | `.cta-row`             | Enforces filled + outlined + text layout   |
| Install module     | `.install-module`      | Canonical pip-install + Copy + quickstart  |
| Mid-article band   | `.cta-band`            | Post-proof contextual conversion           |
| End-of-page block  | `.cta-block-end`       | Final cluster (max 3 destinations)         |
| Nav CTA            | `.btn-nav-cta` outline | Global pilot entry, outline in base.css    |

## 6. Analytics

Handler: `site/_snippets/cta-analytics.js`, injected/refreshed site-wide by
`scripts/sync_shared.py`. Inert until GTM tags consume these `dataLayer` events
(create GA4 events for each name + parameter):

```
cta_click
  cta_intent:      install | demo | pilot | github | quickstart | first_check
  cta_position:    nav | hero | mid | end
  cta_component:   hero_cluster | install_module | cta_band | end_block | nav
  cta_destination: href of the control
  page_type:       homepage | docs | demo | integration | use_case | insight |
                   concept | team | pilot | pricing | benchmark | other

code_copy
  copy_context: command string copied
  page_type

form_start / form_error / form_submit / form_success  (pilot form, PR 3)
```

Markup contract: CTA controls carry `data-cta-intent`, `data-cta-position`,
`data-cta-component`; destination comes from `href`. Copy controls carry
`data-code-copy` and emit `code_copy`, never `cta_click`.

## 7. Rollout plan

Each PR verifies: desktop/mobile screenshots, keyboard focus, axe scan,
destination integrity, one-filled-action-per-cluster, and that no lime button
styling has returned.

### PR 1 — Foundation + nav + homepage + docs (shipped as one slice)
1. CTA primitives folded into `base.css`; legacy lime nav rules swept from all pages.
2. Nav pilot button → outline site-wide (`sync_shared.py`).
3. Homepage hero: Install primary (→ `#install`), Demo secondary, GitHub text link;
   pricing removed from homepage ending.
4. Homepage install module anchored at `#install`; quickstart links point to `/docs/#quickstart`.
5. Docs install-first cluster above doc cards; `#quickstart` anchor added.
6. `cta-analytics.js` handler live site-wide.

### PR 2 — Demo and integration surfaces
Sequencing decided by the GA4 baseline table.

### PR 3 — Use cases, team pages, pricing (+ pilot form events)
Pilot page: form + criteria side-by-side above the fold; four required fields;
`form_start/form_error/form_submit/form_success` wired.

### PR 4 — Insights, concepts, benchmark and remaining templates
Mid-article bands placed after first proof section (not by scroll percentage).

### Later / optimization
- A/B "Request a drift audit" vs "Apply for a complimentary pilot" (only if traffic supports it).
- Per-tool integration CTAs ("Set up with Codex", "Set up with Claude Code").
- Newsletter capture restricted to article endings + footer.

## 8. Guardrails

- One filled coral button **per cluster**; one primary intent per page (it may repeat down-page).
- A CTA label must describe its destination exactly ("Install" ⇒ quickstart/pypi).
- Lime is reserved for evidence/status; converting it back to buttons is a regression.
- New pages consume the base.css primitives rather than re-inlining button styles;
  genuinely new patterns go into base.css so sync keeps them canonical.
- OG images: any new page still follows the AGENTS.md og-template pipeline — unaffected.
