# GTM/GA4 canonical tagging requirements

Status: canonical tags LIVE since 2026-08-30 (version 5). Legacy duplicate
tags PAUSED 2026-09-03 (version 6, "Attribution params + legacy duplicate
cutover"), which also added the three attribution DLVs.
Last verified against GTM container `GTM-KL7FB67N`: 2026-09-05 (version 7).

**2026-09-03 is the clean measurement baseline.** Canonical analytics did not
exist before 2026-08-30 and ran duplicated until 2026-09-03. Do not infer
anything about install intent, CTA performance or activation from the absence
or volume of these events before that date, and do not use pre-baseline data
as a control for the Wave 1 CTA routing experiment.

This document is the source of truth for site event delivery. The site pushes
structured objects to `window.dataLayer`; GTM reads those objects and sends GA4
events to measurement ID `G-ZZ9YG12PPX` (property `534820916`).

## 1. Canonical events

| Event | Meaning | Key event? |
|---|---|---|
| `cta_click` | A tagged conversion-oriented link was clicked | No |
| `code_copy` | An install/code control was copied | No |
| `pilot_form_start` | First interaction with the pilot form | No |
| `pilot_form_attempt` | A locally valid form was sent to Formspree | No |
| `pilot_form_error` | Validation or network/server failure | No |
| `pilot_form_success` | Formspree returned HTTP success | **Yes** |

`pilot_form_success` is the sole primary conversion. CTA clicks, code copies,
and page views remain funnel signals rather than GA4 key events.

## 2. Payload contract

### `cta_click`

```js
{
  event: 'cta_click',
  cta_intent: 'install|demo|pilot|github|quickstart|first_check|setup|evidence|benchmark|contribute|audit|start_audit',
  cta_position: 'nav|hero|mid|end',
  cta_component: 'hero_cluster|install_module|cta_band|end_block|nav|concept_link|pricing_card|context',
  cta_destination: '<href>',
  link_text: '<visible label, trimmed to 100 chars>',
  source_page: '<pathname of the page the click came from>',
  content_segment: 'developer_evaluation|problem_awareness',   // omitted if unsegmented
  page_type: 'homepage|docs|demo|audit|integration|use_case|insight|concept|team|pilot|pricing|benchmark|other'
}
```

### `code_copy`

```js
{
  event: 'code_copy',
  copy_context: '<copied command>',
  source_page: '<pathname>',
  content_segment: '<segment>',   // omitted if unsegmented
  page_type: '<page type>'
}
```

### Attribution parameters

`source_page`, `link_text` and `content_segment` exist so a report can ask
which *content type* produced a conversion, not merely how many fired.

`content_segment` is declared per page by the CTA routing work as
`<meta name="mneme:content-segment" content="...">`. Pages that have not been
segmented omit the parameter rather than guessing a value. The two values
correspond to the two organic conversion motions:

| Segment | Motion |
|---|---|
| `developer_evaluation` | insight → demo/quickstart/compare → install / GitHub → usage → audit/pilot |
| `problem_awareness` | insight → Architecture Audit → baseline → demo → pilot |

### Dev-host suppression

`cta-analytics.js` returns before registering any listener when
`location.hostname` is a dev host (`localhost`, `127.0.0.0/8`, `::1`, `0.0.0.0`,
`*.local`, `*.test`, `*.localhost`) or the page is `file://`.

This is deliberate: localhost events reached the production property and were
visible in the BigQuery export as `page_location = http://localhost:3456/...`,
inflating `outbound_link_clicked` and corrupting landing-page attribution.
Suppressing at the source keeps BigQuery clean as well as GA4, which a GA4-side
data filter would not.

### Pilot form

All pilot events include `page_type=pilot` and `form_id=pilot-form`.
`pilot_form_error` also includes `error_type=validation|network`.

The names are deliberately prefixed with `pilot_`. GA4 enhanced measurement
already uses `form_start` and `form_submit`; reusing those names would merge
automatic and application-defined events.

## 3. GTM variables

Create Data Layer Variables (version 2) with these exact names:

| GTM variable name | Data layer key |
|---|---|
| `DLV - cta_intent` | `cta_intent` |
| `DLV - cta_position` | `cta_position` |
| `DLV - cta_component` | `cta_component` |
| `DLV - cta_destination` | `cta_destination` |
| `DLV - page_type` | `page_type` |
| `DLV - copy_context` | `copy_context` |
| `DLV - form_id` | `form_id` |
| `DLV - error_type` | `error_type` |
| `DLV - link_text` | `link_text` |
| `DLV - source_page` | `source_page` |
| `DLV - content_segment` | `content_segment` |

Do not rely on Event Settings to discover arbitrary data-layer keys. Each GA4
event parameter must be explicitly mapped to the corresponding DLV.

## 4. GTM trigger and router tag

Use one Custom Event trigger named `Custom Event - Canonical Analytics`:

- Event name: `^(cta_click|code_copy|pilot_form_(start|attempt|error|success))$`
- Use regex matching: enabled
- Fires on: **All Custom Events**

Attach it to one GA4 Event tag named `GA4 - Canonical dataLayer event`:

- Measurement ID: `G-ZZ9YG12PPX`
- Event name: `{{Event}}`
- Event parameters: explicitly map all eleven DLVs listed in section 3

Parameters that are not present on an event resolve to `undefined` and are not
sent. This router preserves the originating event name while keeping one
auditable mapping instead of six near-identical tags.

## 5. GA4 custom dimensions

Register these event-scoped dimensions after parameters are visible in
Realtime/DebugView:

| Dimension | Parameter |
|---|---|
| CTA intent | `cta_intent` |
| CTA position | `cta_position` |
| CTA component | `cta_component` |
| Page type | `page_type` |
| Form ID | `form_id` |
| Form error type | `error_type` |
| Content segment | `content_segment` |

Keep raw `cta_destination`, `copy_context`, `link_text` and `source_page` in
BigQuery. They can have many distinct values and do not need GA4
custom-dimension quota for current reports.

## 6. Reading the funnel: three buckets, not "key events"

GA4 key events alone are NOT Mneme's activation metric. Treating them as such
produces a materially wrong picture of the site.

A September 2026 analysis of organic Insight landing pages concluded that the
top articles produced "zero key events" and should therefore all be re-routed
to the Architecture Audit. That conclusion was wrong. The query counted a
hand-picked set of `cta_*` events and omitted `outbound_link_clicked`, which
had 393 events in the window -- 95 of them to the GitHub repository. Those are
product activations. Re-measuring with them included moved organic Insight
activation from 0% to ~5.4%, and the proposed blanket re-route would have
removed working developer activation paths from technical articles.

Compounding it, the single most important activation action -- copying
`pip install mneme-hq` -- appeared to be invisible. That was a second
measurement error, not a second bug: `code_copy` was absent from the query
window only because the canonical tags went live on 2026-08-30 and the window
ended 2026-09-01. `code_copy` fires correctly (first observed 2026-09-02).
Always check the window against the container's publish date before concluding
an event does not exist. An unmeasured action is not an absent one, and a
recently-instrumented one is not an unmeasured one.

### Mneme's funnel definition

Stop treating a bag of GA4 events as "key events". These three states are the
funnel; report against all of them or none:

| State | Members |
|---|---|
| **PLG activation** | `code_copy`, Quickstart/docs CTA, GitHub CTA, demo activation |
| **Evaluation** | Audit CTA, `audit_start`, `audit_complete`, comparison interaction |
| **Commercial** | baseline saved, pilot CTA, contact/pilot submission |

**Count unique sessions or users reaching a state -- never sum raw events.**
A state is binary per session: reached or not. This is what makes the funnel
robust even when a generic analytics event legitimately coexists with a
canonical one, and it is why the 2x/5x duplication corrupted raw totals while
leaving session-level rates intact.

### One canonical event per action -- not one event per action

The target is **one canonical Mneme event per user action, with no duplicate
canonical/legacy equivalent.** It is NOT "exactly one GA4 event per click".

GA4 Enhanced Measurement stays enabled, so a GitHub CTA click legitimately
produces both a canonical `cta_click` and a generic Enhanced Measurement
`click`. That is correct and useful. The rule is that the two must never be
counted as the same conversion: canonical events define the funnel states
above, and Enhanced Measurement events are generic context only.

The two organic motions in section 2 map onto these differently: the
developer/evaluation motion terminates in Activation, the architecture-leader
motion in Commercial. Optimising one bucket while blind to another is how a
product-led funnel gets traded away for a small number of commercial leads.

Corollary for any future query: enumerate the event names in the window first
(`SELECT event_name, COUNT(*) ... GROUP BY event_name`) rather than filtering
to a remembered list, and exclude dev hosts.

## 7. Legacy cutover -- COMPLETED 2026-09-03 (version 6)

The live container still has click-triggered legacy tags including
`cta_demo_click`, `cta_github_click`, and `install_command_copied`. The homepage
also previously fired `cta_clicked` directly.

Canonical and legacy were both live from 2026-08-30 to 2026-09-03, so every
tagged click in that window was counted more than once. Measured 2026-09-03,
grouping events by session and second:

| One user action | Events actually recorded |
|---|---|
| GitHub link click | `cta_github_click` + `outbound_link_clicked` (2x) |
| GitHub link click (worst observed) | `click` + `cta_github_click` x2 + `outbound_link_clicked` x2 (5x) |
| Demo CTA click | `cta_click` + `cta_demo_click` (2x) |

Any raw event count between 2026-08-30 and 2026-09-03 is inflated.
Session-level metrics that use `MAX(...)` per session are unaffected.

Paused in version 6, with the duplication each caused:

| Paused tag | Trigger | Duplicated |
|---|---|---|
| `GA4 - cta_demo_click` | Click - Demo | canonical `cta_click` (demo CTAs carry `data-cta-intent="demo"`) |
| `GA4 - cta_github_click` | Click - GitHub | canonical `cta_click` (GitHub CTAs carry `data-cta-intent="github"`) |
| `GA4 - install_command_copied` | Custom Event | `code_copy`; also dead -- no page emits that event |
| `GA4 - outbound_link_clicked` | Click - Outbound | Enhanced Measurement's native outbound `click` |

Deliberately NOT paused: Enhanced Measurement (generic outbound continues via
its native `click`), and `insight_article_clicked`, `use_case_viewed`,
`demo_page_viewed`, `contact_method_clicked`, `community_engagement_click`,
`benchmark_section_viewed`, `scroll_depth` -- none of which duplicate a
canonical event.

Verified against the live container (`gtm.js?id=GTM-KL7FB67N`) after publish:
`cta_demo_click`, `cta_github_click` and `outbound_link_clicked` are absent
entirely; `install_command_copied` survives only as an orphaned trigger
predicate with no tag attached, so it cannot fire. `cta_click`, `code_copy`,
the `pilot_form_*` regex, and all three new DLVs are present.

Still to confirm from the daily BigQuery export (first clean day 2026-09-04):
legacy event counts fall to zero. Delete the paused tags only after that.

1. Publish the canonical tags while legacy tags remain unchanged.
2. Verify exactly one canonical event per action in GTM Preview and DebugView.
3. Verify one daily BigQuery export.
4. Pause overlapping legacy tags; do not repoint them to `cta_click` because
   both the legacy click trigger and the data-layer trigger would then send the
   same event.
5. Confirm legacy counts fall to zero before deleting anything.

## 8. Verification checklist

- [ ] Homepage hero Install sends one `cta_click` with all parameters.
- [ ] Copy sends one `code_copy` and no `cta_click`, with
      `copy_context = pip install mneme-hq`.
- [ ] An Insight Audit CTA sends `cta_click` with `cta_intent=audit`,
      `cta_component=context`, and the article path in `source_page`.
- [ ] `content_segment` is present on segmented Insights and absent elsewhere.
- [ ] No event arrives with `page_location` on a localhost/dev host.
- [ ] Homepage team Pilot sends one `cta_click` with `cta_position=mid`.
- [ ] Invalid pilot form sends `pilot_form_start` and `pilot_form_error` only.
- [ ] Valid pilot submission sends `pilot_form_attempt`, then
      `pilot_form_success` only after Formspree returns HTTP success.
- [ ] DebugView shows parameters populated, not `(not set)`.
- [ ] BigQuery daily export contains the canonical events and parameters.
- [ ] `pilot_form_success` is marked as a GA4 key event.
- [ ] Obsolete key-event flags and overlapping legacy tags are removed only
      after the daily-export check.

## 9. Change log

- [x] 2026-08-30 — live GTM/GA4 configuration audited
- [x] 2026-08-30 — canonical event taxonomy and explicit parameter map defined
- [x] 2026-09-03 — attribution parameters (`source_page`, `link_text`,
      `content_segment`), dev-host suppression, `/audit/` nav tagging and the
      `audit` page_type added to `cta-analytics.js`; synced to all pages
- [ ] date — site event normalization deployed
- [x] 2026-08-30 — GTM variables, regex trigger, and router tag staged and verified in Preview
- [x] 2026-09-05 — version 7 published: Audit workspace DLVs, canonical
      event routing, sanitized virtual page views, automatic workspace
      page-view suppression, and the Audit-only `send_page_view=false` Google
      tag; GA4 browser-history page views disabled separately
- [x] 2026-09-03 — version 6 published: `DLV - link_text`, `DLV - source_page`,
      `DLV - content_segment` added and mapped onto the canonical tag (11
      parameters); `cta_demo_click`, `cta_github_click`,
      `install_command_copied` and `outbound_link_clicked` paused; verified
      against the live container
- [x] 2026-08-30 — six low-cardinality GA4 dimensions created
- [ ] date — pilot success verified and legacy tags paused

## 10. Audit workspace extension — container live, application release pending

The BrowserRouter application at `/audit/workspace/` now owns a separate,
production-host-gated data-layer adapter. The adapter loads `GTM-KL7FB67N`
only for a production build running at exactly `https://mnemehq.com`; local,
preview, test, non-HTTPS, and deployment/build-kill-switched builds neither
load GTM nor push events. `VITE_AUDIT_GTM_ENABLED` is compiled into the bundle,
so changing it requires a rebuild and redeploy. Do not merge or deploy the
application change until the container work below is published, because the
current Google tag could otherwise create an automatic page view containing a
real BrowserRouter identifier.

GTM version 7, `Audit workspace analytics + SPA pageview privacy`, was
published on 2026-09-05. It contains 37 additions and 3 modifications. The
four paused legacy tags remain unchanged.

The application emits these canonical events:

| Event | Meaning | Parameters beyond attribution/context |
|---|---|---|
| `audit_screen_view` | One canonical Audit SPA screen became active | `audit_screen`, templated `page_path`, `page_location`, `page_title` |
| `audit_input_selected` | A URL, ZIP, or demo input was selected | `input_type`, `selection_method` |
| `audit_start` | A fresh create-audit request started | `input_type` |
| `audit_complete` | A fresh create response passed `mneme.audit/v1` validation | `input_type`, `duration_ms`, the eight shipped summary fields below |
| `audit_error` | A validation, API, re-audit, copy, or export operation failed | `stage`, allowlisted `error_code`, optional `format` |
| `audit_baseline_saved` | Baseline persistence was confirmed by the backend | none |
| `audit_reaudit_start` | A project re-audit request started | none |
| `audit_reaudit_complete` | The backend returned a completed re-audit | `duration_ms` |
| `audit_comparison_view` | A validated backend comparison loaded | compatibility, six backend state counts, two backend deltas |
| `audit_decision_toggle` | A decision card expanded or collapsed | `action` plus safe decision fields |
| `audit_decision_view` | A validated decision detail loaded | safe decision fields |
| `audit_rule_copy` | A proposed rule was successfully copied | safe decision fields |
| `audit_export` | An export response body was successfully read | `format` |

The eight Audit summary fields are `decisions_discovered`,
`protection_relevant`, `protected_count`, `mneme_ready_count`,
`requires_modelling_count`, `guidance_count`, `current_protection`, and
`identified_mneme_potential`. These values, all comparison counts, and both
comparison deltas are copied verbatim from validated backend responses.
Analytics must never calculate or reconstruct an Audit score.

Safe decision fields are `protection_classification`, `evidence_confidence`,
`has_proposed_rule`, and the allowlisted `rule_type`. Rule patterns, decision
text, evidence/source paths, repository data, audit/project/decision IDs,
commit SHAs, credentials, and tokens are never parameters.

Every Audit event also carries `page_type=audit`, a templated `source_page`,
and, where declared, `content_segment`. `cta_click` continues the existing
canonical contract and carries sanitized `cta_destination` and bounded
`link_text`; Audit and pilot identifiers/query values are stripped from the
destination. Screen paths use these templates only:

```
/audit/workspace/
/audit/workspace/audit/:auditId
/audit/workspace/audit/:auditId/decisions/:decisionId
/audit/workspace/audit/:auditId/gaps
/audit/workspace/project/:projectId
/audit/workspace/project/:projectId/compare
```

Audit CTA intents include `run_audit`, `try_demo`, `private_repo_docs`,
`install_mneme`, and `discuss_pilot`, alongside the existing navigation,
report, export, baseline, and decision CTA intents.

### Release sequence

1. Before merging the replacement analytics PR, configure and publish GTM: add
   version-2 Data Layer Variables for every Audit parameter named above,
   plus `page_location`, `page_title`, and `page_referrer`; retain the existing
   attribution DLVs from section 3.
2. Extend `Custom Event - Canonical Analytics` and its single canonical GA4
   router tag to the Audit events. Explicitly map each event parameter; do not
   enable arbitrary parameter collection and do not resurrect paused legacy
   event tags.
3. Add `GA4 - Audit virtual page view`, triggered only by
   `audit_screen_view`, with GA4 event name `page_view` and the templated
   `page_path`, `page_location`, `page_title`, `page_referrer`, `page_type`,
   `audit_screen`, `source_page`, and `content_segment` values.
4. Exclude `/audit/workspace/` from the existing automatic page-load tag and
   configure its Audit-specific Google tag with `send_page_view=false`.
   Disable Enhanced Measurement browser-history page views so BrowserRouter
   transitions cannot transmit raw identifiers; the explicit virtual tag is
   the sole page-view source for the workspace.
5. Publish the container and record the new version/date here. Do not weaken
   the exact-production-host gate to force pre-merge application events into
   GTM Preview; the app cannot emit them on localhost or a preview hostname by
   design. Leave all four paused legacy tags untouched pending the separate
   zero-legacy BigQuery confirmation.
6. Immediately after the GTM publish, squash-merge the replacement analytics
   PR and allow the normal production deployment to complete. A merge or
   started deployment is not deployment proof; use the repository deployment
   evidence contract.
7. Immediately validate the deployed production workspace with Tag Assistant
   and GA4 DebugView: one templated `page_view` per screen; no raw identifiers;
   fresh-create `audit_start` then `audit_complete`; no completion on refresh;
   persistence-confirmed baseline events; mutually correct re-audit outcomes;
   backend comparison values; pattern-free decision/copy events; export only
   after body completion; and intact `source_page`, `link_text`, and
   `content_segment` CTA attribution.
8. If an identifier leaks or page views duplicate, disable the Audit GTM
   configuration immediately (or deploy a build with
   `VITE_AUDIT_GTM_ENABLED=false`) and roll back the application deployment as
   appropriate. Confirm the next BigQuery daily export before deleting any
   paused legacy configuration.
