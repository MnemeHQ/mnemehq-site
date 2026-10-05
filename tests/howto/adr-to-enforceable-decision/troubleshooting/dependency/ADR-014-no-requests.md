---
id: ADR-014
title: Services use the shared HTTP client
status: accepted
priority: foundational
date: "2026-10-03"
scope: network
---
Use app.clients.http so retries and timeouts stay consistent.

## Constraints
- FORBID_DEPENDENCY: requests
