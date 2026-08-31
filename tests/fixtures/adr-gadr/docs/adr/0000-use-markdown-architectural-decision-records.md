# 0000-use-markdown-architectural-decision-records.md

# Use Markdown Architectural Decision Records

## Status

Accepted

## Context

We need a lightweight way to record architectural decisions. Many existing ADR formats are too heavy or require specific tooling.

## Decision

We will use Markdown files for Architectural Decision Records (ADRs), stored in `docs/adr/`.

Each ADR is a separate Markdown file with a number and a title, e.g., `0001-use-gadr-as-name.md`.

## Consequences

- Lightweight and easy to read
- No special tooling required
- Version controllable
- Works with any Markdown viewer