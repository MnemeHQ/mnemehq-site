---
id: ADR-003
title: "Public empirical claims must resolve to a verified public artifact"
status: accepted
priority: foundational
date: 2026-08-30
scope: site.evidence
---

# ADR-003: Public empirical claims must resolve to a verified public artifact

## Status

Accepted — 2026-08-30

## Context

A citation-worthiness review of the site's insights content found that
several articles synthesize third-party evidence (Gartner, research
papers, vendor reports) well but supply little first-party evidence of
their own — content that interprets sources rather than contributing an
observation a retrieval system could cite. Mneme already has reproducible
first-party evidence in the public `MnemeHQ/mneme` repository: a frozen
enforcement benchmark and an enforcement-quality suite, both with
committed, versioned results.

[ADR-002](ADR-002-demo-evidence-contract.md) already established this
discipline for `site/demo/**`: a claim must correspond to an executable
path that produces it, or be marked illustrative. Content outside
`site/demo/**` — insights articles citing benchmark numbers — has no
equivalent contract, and nothing stops a number from drifting out of
sync with the artifact that produced it once either side is edited.

## Decision

Public empirical claims must resolve to a verified public artifact and
carry an explicit claim boundary.

Concretely: any first-party result cited on the site (a benchmark
number, a measured rate, a pass/fail count) must link to a public,
committed artifact that actually contains that result, and the
surrounding copy must state what the result does and does not
establish. A result whose source artifact is not yet public, or has not
been verified against the page's claim, is not eligible to be cited.

This ADR states the rule. It does not prescribe a visual component,
page layout, or paragraph template — those are implementation detail
that can change without revising this document. The initial
implementation (an evidence registry and a small CI checker) is recorded
in `docs/superpowers/specs/2026-08-30-citation-worthiness-evidence-design.md`,
not here.

## Consequences

- A claim can be written before its source artifact is public, but
  cannot ship until the artifact is merged to the source repository's
  main branch and the claim is verified against it.
- This is expected to recur: future benchmark results, design-partner
  evidence, and other first-party observations should be checked
  against this same rule before being cited on the site.
