---
id: ADR-005
title: "Status labels are monochrome; colour is reserved for semantic verdicts"
status: accepted
priority: normal
date: 2026-08-24
scope: site.status_labels
---

# ADR-005: Status labels are monochrome; colour is reserved for semantic verdicts

## Status

Accepted — 2026-08-24

## Provenance

This is not a new decision. It is the site decision first recorded on
2026-08-24 as project-memory entry `ADR-003` (commit `83205ad3e`; anti-patterns
cleared in `e3a55f6d0`), moved into an ADR file on 2026-10-12 with its
decision, rationale, constraints and dates unchanged. Original source note:
"Visual audit 2026-08-24; integrations hub redesign commit d8b92f02".

Two reasons for the move:

- Mneme 0.10.0 migrates project memory into an authoritative decision index
  only from decisions whose source is an ADR file. The memory-only entry had a
  free-text source, so the migration refused it.
- `docs/adr/history/ADR-003-site-publishing-guidelines.md` is a different,
  superseded core decision that shares the id `ADR-003`. Renumbering this
  decision to ADR-005 removes that ambiguity. The historical record is
  unchanged.

Representational differences from the memory entry, none of which changes
what is enforced:

- Scope `site/*` becomes `site.status_labels`: ADR scopes must be dotted
  identifiers. Mneme uses decision scope as retrieval text, not as path
  applicability.
- The four constraint strings are listed under Constraints below as prose.
  As before, none is a machine-enforceable directive.
- Priority `normal` is set because ADR files require one. The decision is
  the only one in its scope, so no precedence outcome changes.

## Context

A visual audit of mnemehq.com (August 2026) found the same defect on three
surfaces: status/support-level tags rendered in multiple accent colours,
producing visual noise and implying distinctions the underlying evidence did
not support.

1. `/integrations/` used green (native), teal (validated), and amber
   (experimental) badge boxes on every card.
2. `/demo/` used a green "runs locally" pill and a purple "agents scripted"
   pill on every card.
3. `/works-with/` overrode its neutral card tags with green and teal
   variants, two coloured tags per card down an entire page.

The integrations hub fix (PR #45 follow-up, commit d8b92f02) established the
working pattern: a single monospace status line, one muted colour, no
background or coloured border, with shipped-versus-not-shipped differentiated
by card opacity rather than hue.

## Decision

Across the site, status and support-level labels are monochrome:

- One style: DM Mono, uppercase, small size, `var(--muted)` colour, no
  background, no coloured border.
- Non-shipped entries (experimental, planned, validation in progress) are
  differentiated by reduced card opacity, never by a second colour.
- Semantic verdict colours (PASS/WARN/FAIL greens/ambers/reds) are permitted
  only where the element reports an actual verdict from the enforcement
  engine (governance traces, demo output).
- Third-party brand marks inside logo pills are exempt.

## Constraints

- Status/support-level tags: DM Mono uppercase, var(--muted), no background, no coloured border
- Non-shipped differentiation via card opacity only
- Verdict colours only for real PASS/WARN/FAIL output
- Brand marks in logo pills exempt

## Compliance

The pattern is established in `site/integrations/index.html`
(`.int-status` + `.int-card.muted`) and applied to `site/demo/index.html`
(`.flagship-tag.*`) and `site/works-with/index.html` (`.card-tag` overrides
removed). New pages must not reintroduce coloured status badges.

### What Mneme does and does not enforce here

An earlier version of this record carried the three anti-patterns above as
prose sentences ("Colored badge/pill boxes...", "Two or more coloured tags
on one card", "Colour as the only signal..."). The first preflight run
produced three findings, recorded here rather than quietly fixed, because
this repository dogfoods the same semantics documented for users:

1. Anti-pattern values are tokenised and matched word-boundary, so the
   trigger `teal` fired on any page whose stylesheet references
   `var(--teal)` — including pages that comply with this ADR.
2. The triggers `two`, `one`, and `only` fire on ordinary English prose.
   Three compliant files failed; nothing non-compliant was caught that
   review would have missed.
3. Byte-level CSS conventions (which class may carry which colour) are not
   text-token properties. As with ADR-002's `FORBID_LITERAL` finding, this
   belongs with repository checks or a future directive that can match
   exact literals with include-paths, not with prose anti-patterns.

So badge-regression detection is **not** machine-enforced today. Compliance
depends on review attention; the canonical pattern to copy is
`.int-status` / `.int-card.muted` in `site/integrations/index.html`.
