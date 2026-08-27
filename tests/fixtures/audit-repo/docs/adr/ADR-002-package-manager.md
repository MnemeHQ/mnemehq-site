---
id: ADR-002
title: Package Manager
status: accepted
date: 2026-01-15
priority: foundational
---

# ADR-002: Package Manager

## Context
Python dependency management needs to be consistent across all environments.

## Decision
Standardize on a single package manager for all Python dependencies.

## Constraints
- no pip install in CI
- no poetry

## Rationale
uv provides faster installs, better caching, and deterministic resolution. The team has standardized on uv. Pip is acceptable for local development but not in CI. Poetry adds unnecessary complexity.