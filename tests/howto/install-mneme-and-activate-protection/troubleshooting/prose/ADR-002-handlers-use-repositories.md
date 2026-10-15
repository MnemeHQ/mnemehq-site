---
id: ADR-002
title: Request handlers must not import the database client
status: accepted
priority: foundational
date: "2026-10-02"
scope: handlers
---
Handlers call repositories. A direct client import skips the transaction
and tenancy handling that lives in app/repositories.
