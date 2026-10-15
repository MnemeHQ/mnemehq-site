---
id: ADR-001
title: No Celery
status: accepted
priority: foundational
date: "2026-10-01"
scope: workers
---
Background jobs run on the managed Pub/Sub queue. Celery was retired after
the 2026 queue incident, and reintroducing it brings back a broker the team
no longer operates.
