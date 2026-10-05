---
id: ADR-012
title: Request handlers do not import the database client
status: accepted
priority: foundational
date: "2026-10-01"
scope: handlers
---
Handlers call repositories. A direct client import skips the transaction
and tenancy handling that lives in app/repositories.

## Constraints
- FORBID_LITERAL:
    value: from app.db.client import
    include_paths:
      - "app/handlers/**"
