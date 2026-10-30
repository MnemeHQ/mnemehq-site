# Audit API deployment record

Durable provenance for production deployments of the Audit backend
(`api.mnemehq.com`, Cloud Run service `mneme-audit-api`, project
`mneme-hq-prod`, region `us-central1`). Newest first. Add an entry for every
production cutover; a merge or a started deploy is not a deployment.

Deployment is currently manual (`gcloud`), not repo-automated. Each entry
records how that deployment was produced so it can be reproduced.

## 2026-10-30: `154878aa` (operator auth on cross-project routes; ADR import resilience)

| | |
|---|---|
| Source commit | `154878aa4209890ea7ff95e4fe84693402b9f94f` (`main`); backend changes from PR #278 (`ea2c6fa2`) and PR #282 (`792b31d0`) |
| Cloud Run revision | `mneme-audit-api-154878aa4209` |
| Image | `gcr.io/mneme-hq-prod/mneme-audit-api@sha256:5e15f8b6d7897db9713e83ca8de7acfd1d9f6cf121d94c17f3f8fc16d83121d1` (tag = full commit SHA) |
| Mneme engine | `mneme-hq` 0.9.2 (lock unchanged) |
| Python dependencies | exactly `audit/backend/requirements.lock` (50 distributions; `pip freeze` in the image verified identical) |
| `APP_VERSION` | `154878aa4209` |
| Traffic | 100% since 2026-10-30 11:15Z |
| Previous revision | `mneme-audit-api-a2aa74f4856d`, retained at 0% for rollback |
| Outcome | Production cutover successful; no rollback |

Why: an anonymous `GET /api/v1/projects` returned every audited project (found 2026-10-30 by `scripts/audit_health_report.py`). The project-create, PATCH, per-project audit list and contact routes had no auth either. That contradicted `site/security/data-handling/`, which says only Mneme HQ operators can access the audit database.

How it was produced:

1. New Secret Manager secret `mneme-audit-operator-token`, version 1, generated locally and piped in without being printed or stored on disk. `roles/secretmanager.secretAccessor` granted to `mneme-audit-run`.
2. Image built with Docker from a clean `git archive` of the source commit: `docker build -f audit/backend/Dockerfile --build-arg GIT_SHA=<sha> .`. Then pushed.
3. Deployed as a no-traffic revision:
   `gcloud run deploy mneme-audit-api --image <digest> --no-traffic --tag candidate --revision-suffix 154878aa4209 --update-env-vars APP_VERSION=154878aa4209 --update-secrets MNEME_AUDIT_OPERATOR_TOKEN=mneme-audit-operator-token:latest`.
4. Candidate verified, then traffic shifted with `gcloud run services update-traffic mneme-audit-api --to-revisions mneme-audit-api-154878aa4209=100`.

Configuration: identical to the previous revision (service account, Cloud SQL, VPC connector, max instances, CPU and memory, timeout, concurrency, `DATABASE_URL` secret). Only two values differ: `APP_VERSION`, and the new `MNEME_AUDIT_OPERATOR_TOKEN` secret reference. No migration: this deployment introduces none.

Validation evidence:

- Candidate, at 0% traffic:
  - `/health` 200.
  - Anonymous and wrong-token calls to the project list, project create, PATCH, contacts list and contact create all return 401. The operator token lists all projects.
  - A ZIP audit of `tests/fixtures/audit-repo` returned 201 with `mneme_version` 0.9.2 and 11 decisions. Read-back, project, export and save-baseline all returned 200. Compare returned 400, as expected for a single audit.
  - CORS allows `https://mnemehq.com`. No error-level logs.
- After cutover, via `api.mnemehq.com`:
  - `/health` 200. Anonymous list, contacts and PATCH return 401. CORS is unchanged.
  - Request logs show the new revision serving.
  - The live workspace demo audit ran end to end in a browser with no console errors.
  - `scripts/audit_health_report.py` reports Exposure PASS, exit 0. No error-level logs.
- Exposure assessment: with the token, no project has any linked contact (40 projects, 0 contact links). The API has no route that lists contacts on their own. So no contact data was reachable through the open routes. The project list exposed repository locators: public GitHub URLs and `upload:` markers.
- CI: the "Audit contracts on the locked production resolution" job passed on both merge commits.

Left in place after this deployment:

- Test records in the production database: audit `572e42d3-c529-4ab4-bad6-1494ee64920b` (ZIP fixture, project `38eaba1d-d9ba-4358-b2a8-778e03a39a90`), and audit `68862beb-982d-44ad-9f61-dae0826dca9a` (workspace demo run).
- The `candidate` traffic tag, pointing at the new revision.

Operator access: read the token with `gcloud secrets versions access latest --secret mneme-audit-operator-token --project mneme-hq-prod` into `MNEME_AUDIT_OPERATOR_TOKEN`, and never print it. Send it as `Authorization: Bearer`.

Rollback:
`gcloud run services update-traffic mneme-audit-api --project mneme-hq-prod --region us-central1 --to-revisions mneme-audit-api-a2aa74f4856d=100`.
Rolling back reopens the exposure.

## 2026-10-01: `a2aa74f4` (first locked-resolution deployment)

| | |
|---|---|
| Source commit | `a2aa74f4856db8b027fa2fffb47738c3f3ae6963` (`main`, PR #180) |
| Cloud Run revision | `mneme-audit-api-a2aa74f4856d` (created 2026-10-01T21:59:05Z) |
| Image | `gcr.io/mneme-hq-prod/mneme-audit-api@sha256:d94312f9c4117e8b88f203ca067767401333cb61eff0c4173cb998c5681c1996` (OCI index; tag = full commit SHA) |
| linux/amd64 manifest | `sha256:a1473462898453e520632668fed104ddbda9f607a4432feb2175a99543860d8c` (the digest Cloud Run records) |
| Mneme engine | `mneme-hq` 0.9.2 |
| Python dependencies | exactly `audit/backend/requirements.lock` at the source commit (50 distributions; `pip freeze` in the image verified identical) |
| `APP_VERSION` | `a2aa74f4856d` |
| Traffic | 100% since 2026-10-01 ~22:05Z |
| Previous revision | `mneme-audit-api-m14-60e156f45f30-v2` (commit `60e156f4`, deployed 2026-09-14), retained at 0% for rollback |
| Outcome | Production cutover successful; no rollback |

How it was produced:

1. Image built with Docker from a clean `git archive` export of the source
   commit: `docker build -f audit/backend/Dockerfile --build-arg GIT_SHA=<sha> .`,
   then pushed to `gcr.io/mneme-hq-prod/mneme-audit-api:<sha>`.
2. Deployed as a no-traffic revision:
   `gcloud run deploy mneme-audit-api --image <index digest> --no-traffic --tag candidate --revision-suffix a2aa74f4856d --update-env-vars APP_VERSION=a2aa74f4856d`.
   All other configuration was inherited from the serving revision.
3. Candidate verified on its tag URL, then traffic shifted with
   `gcloud run services update-traffic mneme-audit-api --to-revisions mneme-audit-api-a2aa74f4856d=100`.

Configuration, verified identical to the previous revision except image and
`APP_VERSION`: `DATABASE_URL` from Secret Manager secret
`mneme-audit-database-url`; max instances 1; service account
`mneme-audit-run`; Cloud SQL instance `mneme-audit-db`; VPC connector
`mneme-vpc-connector`; 1 CPU / 512Mi; timeout 300s; concurrency 80.

No migration was run: this deployment introduced none, and the image does not
run migrations at startup. The production database's Alembic revision was not
independently confirmed.

Validation evidence:

- Candidate (0% traffic): `/health` 200; `/openapi.json` byte-identical to the
  previous revision (17 paths, 21 operations); unknown path returns a JSON 404.
- One audit of `tests/fixtures/audit-repo` (ZIP) against the candidate: 201,
  `mneme_version` 0.9.2; summary matches the locked semantic snapshot. Read-back
  and save-baseline succeeded.
- After cutover, via `api.mnemehq.com`: `/health` 200; the test audit and
  project load; CORS allows `https://mnemehq.com`; the workspace audit and
  project pages render with no console errors; request logs show the new
  revision serving; no error-level logs in the following 15 minutes.
- Not exercised in production: a real baseline-versus-current comparison
  (covered by `test_workspace_contract.py` and `test_m1_acceptance_gates.py`
  on the locked resolution).

Left in place after this deployment:

- Test records in the production database: project
  `7f13810c-98ce-4fe2-a5a9-abbcfcad244e`, audit
  `554e0e16-d221-418c-b48c-e683c5d50938`.
- The `candidate` traffic tag, pointing at the new revision.

Rollback:
`gcloud run services update-traffic mneme-audit-api --project mneme-hq-prod --region us-central1 --to-revisions mneme-audit-api-m14-60e156f45f30-v2=100`
