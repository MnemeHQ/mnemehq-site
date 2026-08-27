---
id: ADR-003
title: Service Boundaries
status: accepted
date: 2026-01-15
priority: foundational
scope: architecture
---

# ADR-003: Service Boundaries

## Context
We need clear boundaries between services to maintain modularity and prevent tight coupling.

## Decision
Services must not import each other's internal modules. Cross-service communication must go through defined APIs.

## Rationale
Tight coupling between services makes independent deployment impossible and creates cascade failures. Each service owns its data and exposes a well-defined contract. Internal implementation details must remain private.