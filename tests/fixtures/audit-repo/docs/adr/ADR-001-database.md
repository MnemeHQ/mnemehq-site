---
id: ADR-001
title: Database Choice
status: accepted
date: 2026-01-15
priority: foundational
---

# ADR-001: Database Choice

## Context
The application needs a primary relational database for persistent data storage.

## Decision
Use PostgreSQL for all persistent application data.

## Constraints
- FORBID_LITERAL: sqlite
- FORBID_LITERAL: mysql

## Rationale
PostgreSQL provides the best balance of features, performance, and operational maturity for our workload. SQLite is not suitable for production concurrent workloads. MySQL lacks some advanced features we need (partial indexes, JSONB operations).