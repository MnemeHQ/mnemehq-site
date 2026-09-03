# M1 backend release checks

The canonical workspace endpoints are `/api/v1/audit` (multipart),
`/api/v1/baselines` (JSON `{ "audit_id": "UUID" }`), and
`/api/v1/projects/:id/audits` (JSON). The legacy `/api/audit` remains unchanged
for clients that have not migrated. Completed result IDs equal record IDs.

The initial canonical audit is persisted under an ephemeral project. Saving
promotes that project and attaches the existing immutable result; it does not
evaluate the repository again. Re-audit creates a separate immutable record.
ZIP provenance explicitly says `not-applicable:archive`; Git SHA comes from the
actual checkout. The installed `mneme-hq` distribution supplies the version.

Comparison returns canonical `baseline_summary`, `current_summary`, server-owned
score deltas, summary counts and per-decision states. Consumers must not score,
classify or infer transitions from decision rows. Classification/scoring formulas
in the frozen P1.2 classifier are not changed by this contract repair.

## Package and migrations

Build from repository root: `docker build -f audit/backend/Dockerfile -t mneme-m1:rc .`.
The image includes app/api/workspace.py, the M1 persistence/comparison modules,
alembic.ini, alembic/env.py and alembic/versions/001_initial_schema.py. No local
proxy executable, test repository or credentials are copied.

With DATABASE_URL supplied securely, run from audit/backend (or /app in image):

```
python -m alembic -c alembic.ini upgrade head --sql
python -m alembic -c alembic.ini upgrade head
python -m alembic -c alembic.ini current
```

Run the online migration as a separately approved release job, not on every web
replica startup. Revision 001 creates a fresh schema without dropping existing
tables. For an existing unversioned M1 database, first back up and compare its
schema with the migration; use an explicitly reviewed baseline/stamp procedure.
Do not blindly stamp or run a destructive reset against production.

Current deployment approval does not follow from local test success. A coordinated
preview must contain the matching frontend and backend, and pass the real browser
journey before the frontend PR is promoted.
