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

## Dependency model: floor and production resolution

- `requirements.txt` is the dynamic compatibility floor (`name>=X.Y.Z`). It is
  never an exact pin; `scripts/check_mneme_version_parity.py` enforces that for
  the Mneme engine.
- `requirements.lock` is the production resolution: every resolved distribution
  as an exact `name==version` pip constraint. It is generated, never hand-edited,
  and used only by the image build
  (`pip install -r requirements.txt -c requirements.lock`).
- The resolution may deliberately lag the newest published engine. It is not
  tied to `scripts/core_version.json`, which is the website's install-reference
  contract, not the Audit backend's.

Scope: this makes the image's **Python dependency graph** reproducible. The
container build as a whole is not: the `python:3.12-slim` base image, the apt
packages and `pip install --upgrade pip` still float.

CI (`audit-release-check.yml`) runs two jobs. The unconstrained job installs the
floor and tests the newest resolution, so new releases are exercised early. The
locked job installs the production resolution, proves the environment matches it
exactly (`scripts/check_audit_lock.py --installed`), and runs the same contracts.

### Upgrading the Mneme engine (or any dependency) in production

An upgrade is an explicit, reviewed change to `requirements.lock`:

1. Regenerate on Linux / CPython 3.12, from the repository root:

   ```
   docker run --rm -v "$PWD:/src" -w /src python:3.12-slim sh -c \
     "apt-get update -qq && apt-get install -y -qq git gcc >/dev/null && \
      python scripts/lock_audit_requirements.py"
   ```

2. In that same locked environment, run the backend tests. If
   `tests/test_production_semantics_snapshot.py` fails, the engine changed what
   the Audit concludes about a fixture repository. Regenerate the snapshots with
   `UPDATE_AUDIT_SNAPSHOTS=1` and review the snapshot diff: every changed
   classification, confidence, guardrail or score is a production semantics
   change and must be intended.
3. Open a PR with the lock diff and any snapshot diff together. Both CI jobs
   must pass.
4. Deployment remains a separate, explicitly approved step. After it, one real
   audit must report `mneme_version` equal to the `mneme-hq` pin in the lock.

In the unconstrained job the snapshot test reports drift against a newer engine
as a skip (visible with `-rs`), not a failure: it is early warning for the next
upgrade, and does not block work while production stays on the reviewed lock.

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
