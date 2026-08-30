# GTM/GA4 canonical tagging requirements

Status: site changes and GTM workspace staged; production publish pending.
Last verified against GTM container `GTM-KL7FB67N`: 2026-08-30.

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
  cta_intent: 'install|demo|pilot|github|quickstart|first_check|setup|evidence|benchmark|contribute',
  cta_position: 'nav|hero|mid|end',
  cta_component: 'hero_cluster|install_module|cta_band|end_block|nav|concept_link|pricing_card',
  cta_destination: '<href>',
  page_type: 'homepage|docs|demo|integration|use_case|insight|concept|team|pilot|pricing|benchmark|other'
}
```

### `code_copy`

```js
{ event: 'code_copy', copy_context: '<copied command>', page_type: '<page type>' }
```

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
- Event parameters: explicitly map all eight DLVs listed in section 3

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

Keep raw `cta_destination` and `copy_context` in BigQuery. They can have many
distinct values and do not need GA4 custom-dimension quota for current reports.

## 6. Legacy cutover

The live container still has click-triggered legacy tags including
`cta_demo_click`, `cta_github_click`, and `install_command_copied`. The homepage
also previously fired `cta_clicked` directly.

1. Publish the canonical tags while legacy tags remain unchanged.
2. Verify exactly one canonical event per action in GTM Preview and DebugView.
3. Verify one daily BigQuery export.
4. Pause overlapping legacy tags; do not repoint them to `cta_click` because
   both the legacy click trigger and the data-layer trigger would then send the
   same event.
5. Confirm legacy counts fall to zero before deleting anything.

## 7. Verification checklist

- [ ] Homepage hero Install sends one `cta_click` with all five parameters.
- [ ] Homepage team Pilot sends one `cta_click` with `cta_position=mid`.
- [ ] Copy sends one `code_copy` and no `cta_click`.
- [ ] Invalid pilot form sends `pilot_form_start` and `pilot_form_error` only.
- [ ] Valid pilot submission sends `pilot_form_attempt`, then
      `pilot_form_success` only after Formspree returns HTTP success.
- [ ] DebugView shows parameters populated, not `(not set)`.
- [ ] BigQuery daily export contains the canonical events and parameters.
- [ ] `pilot_form_success` is marked as a GA4 key event.
- [ ] Obsolete key-event flags and overlapping legacy tags are removed only
      after the daily-export check.

## 8. Change log

- [x] 2026-08-30 — live GTM/GA4 configuration audited
- [x] 2026-08-30 — canonical event taxonomy and explicit parameter map defined
- [ ] date — site event normalization deployed
- [x] 2026-08-30 — GTM variables, regex trigger, and router tag staged and verified in Preview
- [ ] date — staged GTM workspace published
- [x] 2026-08-30 — six low-cardinality GA4 dimensions created
- [ ] date — pilot success verified and legacy tags paused
