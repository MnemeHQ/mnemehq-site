---
id: ADR-001
title: "The website repository dogfoods Mneme governance"
status: accepted
priority: foundational
date: 2026-08-20
scope: repo.website_governance
---

# ADR-001: The website repository dogfoods Mneme governance

## Status

Accepted — 2026-08-20

## Context

The mnemehq.com source and deployment path moved from `MnemeHQ/mneme` into
this repository in July 2026. The transfer was recorded by core ADR-016. Seven
older core ADRs (ADR-003, ADR-006, ADR-007, ADR-008, ADR-011, ADR-012, and
ADR-015) remain there as immutable, superseded historical records. Exact
copies also live under `docs/adr/history/` so the website repository carries
its provenance locally without making those records active again.

Their current rules were migrated into this repository's `PUBLISHING.md`,
which is the canonical and maintained publishing-governance document. Copying
the superseded records here as active ADRs would create a second copy of those
rules and allow it to drift from `PUBLISHING.md`.

The website repository nevertheless needs to exercise Mneme's released
installation, ADR compiler, decision memory, retrieval, and strict preflight
on its own changes. That is the most direct dogfood path for the product the
site documents.

## Decision

1. `PUBLISHING.md` remains the canonical source for detailed website
   publishing and deployment governance.
2. The superseded site ADRs remain in `MnemeHQ/mneme/docs/adr/` as historical
   records and are mirrored unchanged under `docs/adr/history/`. They are not
   deleted, modified, or reactivated.
3. This repository owns an active ADR corpus under `docs/adr/` for current
   repository-level governance decisions. This decision supersedes only the
   earlier transfer plan's statement that the site would not run the compiler;
   it does not reactivate any superseded core ADR.
4. The Mneme ADR compiler produces the native entries in
   `.mneme/project_memory.json`. The compiled file is committed so agent and CI
   consumers all see the same deterministic decision.
5. CI installs the published `mneme-hq` distribution, recompiles the corpus to
   detect stale memory, and runs `mneme check --mode strict` against the change
   surface on every pull request and push to `main`.
6. Purpose-built website validators remain authoritative for structural rules
   that Mneme's current lexical preflight cannot evaluate, including nav/footer
   synchronization, schemas, sitemap registration, and install-command safety.

## Constraints

- REQUIRE_PATH: site/**
- REQUIRE_PATH: PUBLISHING.md
- REQUIRE_PATH: .mneme/project_memory.json
- FORBID_PATH: scratch/**

## Consequences

- The website now exercises the same install, compile, memory, retrieval, and
  enforcement path recommended to Mneme users.
- The historical rationale is locally available without admitting the stale
  ADR bodies into the active website corpus.
- Future website governance decisions can be added here and compiled normally;
  detailed publishing procedures continue to live in `PUBLISHING.md`.

## Related

- `PUBLISHING.md`
- `MnemeHQ/mneme/docs/adr/ADR-016-site-governance-transfer.md`
- `MnemeHQ/mneme/docs/adr/ADR-003`, `ADR-006`, `ADR-007`, `ADR-008`,
  `ADR-011`, `ADR-012`, and `ADR-015` (superseded historical records)
