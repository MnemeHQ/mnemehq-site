---
id: ADR-013
title: Request handlers do not call HTTP services directly
status: accepted
priority: foundational
date: "2026-10-02"
scope: handlers
---
Handlers call service clients in app/clients.

## Constraints
- FORBID_LITERAL:
    value: import requests
    include_paths:
      - "app/handlers/**"
