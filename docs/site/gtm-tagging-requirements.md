# GTM/GA4 tagging requirements — handoff for Codex

Status: ready to execute. Owner: Codex (requires interactive Chrome with a
logged-in Google session — automation could not attach; see §6).
Context: `docs/site/cta-system.md` (system) and `scratch/ga4-baseline.md` (data).

## 0. Preconditions

- GTM container: `GTM-KL7FB67N` (present in every site page's `<head>`)
- GA4 property: export dataset `analytics_534820916` in BQ project `mneme-hq-prod`
- The site-side handler is already live: every page pushes structured events to
  `window.dataLayer` via `site/_snippets/cta-analytics.js` (synced by
  `scripts/sync_shared.py`). Nothing on the site needs to change.

## 1. GA4 custom dimensions (Admin → Custom definitions)

Create event-scoped dimensions (used as event parameters):

| Dimension name    | Parameter        | Scope |
| ----------------- | ---------------- | ----- |
| CTA intent        | `cta_intent`     | event |
| CTA position      | `cta_position`   | event |
| CTA component     | `cta_component`  | event |
| CTA destination   | `cta_destination`| event |
| Page type         | `page_type`      | event |
| Copy context      | `copy_context`   | event |

## 2. GTM: `cta_click` event

- **Trigger:** Custom Event, event name `cta_click`, fires on all clicks.
- **Tag:** GA4 Event, name `cta_click`, parameters exactly as pushed:
  `cta_intent`, `cta_position`, `cta_component`, `cta_destination`, `page_type`.
  Create GTM Data Layer Variables (v2) for each name, or use "Event Settings"
  auto-collection of dataLayer variables.

Expected payload shape (from `cta-analytics.js`):

```
{ event: 'cta_click',
  cta_intent: 'install|demo|pilot|github|quickstart|first_check|setup|evidence',
  cta_position: 'nav|hero|mid|end',
  cta_component: 'hero_cluster|install_module|cta_band|end_block|nav',
  cta_destination: '<href>',
  page_type: 'homepage|docs|demo|integration|use_case|insight|concept|team|pilot|pricing|benchmark|other' }
```

## 3. GTM: `code_copy` event

- **Trigger:** Custom Event `code_copy`.
- **Tag:** GA4 Event `code_copy` with `copy_context`, `page_type`.
- Copy controls must NEVER emit `cta_click` (handler guarantees this).

## 4. GTM: pilot form events (PR 3 prerequisite)

Reserve GA4 events now so PR 3 only adds page code:
`form_start`, `form_error`, `form_submit`, `form_success` — each Custom Event
trigger + GA4 event tag passing `page_type` (form pages will push the rest).

## 5. Migrate legacy events (single-source reporting)

The property already receives hand-rolled events that must be mapped to the new
schema (baseline volumes in `scratch/ga4-baseline.md` §8):

| Legacy event            | 90d volume | Migration |
| ----------------------- | ---------- | --------- |
| `cta_github_click`      | 93         | Find the GTM tag/trigger producing it; repoint to `cta_click` with `cta_intent=github`. If produced by inline site JS, list the pages for a site-side fix instead of forcing it in GTM. |
| `cta_demo_click`        | 32         | Same → `cta_click` with `cta_intent=demo`. |
| `insight_article_clicked` | 87       | Keep for now (editorial nav, not conversion); revisit in PR 4. |
| `outbound_link_clicked` | 335        | Keep — GA4 enhanced measurement; complements `cta_click`. |

Do NOT delete legacy triggers until the new events are verified in the GA4
DebugView and one BQ daily export has landed.

## 6. Chrome/automation constraints (why this is manual)

Playwright/CDP can only attach to a Chrome instance started with
`--remote-debugging-port`. The user's daily Chrome is not started that way, and
automating login credential entry is out of bounds. Two sanctioned approaches:

1. **Restart user's Chrome with the flag** (preferred): close Chrome, relaunch
   with `--remote-debugging-port=9222` on the EXISTING default profile
   (`--user-data-dir` must NOT be overridden — that would create a new,
   logged-out profile). Attach via CDP `http://127.0.0.1:9222`. All sessions
   persist; nothing is deleted. Restore tabs afterwards.
2. **One-time login in a scratch profile**: launch Playwright
   `launch_persistent_context` on a temp dir, user signs in once, session
   persists for the session.

NEVER: delete or modify Chrome profile directories, automate password entry,
or disable existing Chrome processes' data.

## 7. Verification checklist (Codex)

1. GTM Preview mode: click homepage hero Install → `cta_click` fires with full payload.
2. Click a Copy control → `code_copy` fires, no `cta_click`.
3. GA4 DebugView shows both events with all parameters populated.
4. Next day: `bq query` on `analytics_534820916.events_*` confirms export.
5. Legacy `cta_github_click`/`cta_demo_click` counts drop to ~0 while
   `cta_click` with matching intents rises.
6. Document the final trigger/tag names in this file (§8).

## 8. Change log (Codex fills in)

- [ ] date — dimensions created
- [ ] date — cta_click tag live
- [ ] date — code_copy tag live
- [ ] date — form event tags reserved
- [ ] date — legacy migration done
