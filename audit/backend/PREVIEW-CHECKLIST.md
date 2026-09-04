# M1.2 combined preview — next approved session only

**Prepared, not executed. This checklist is not authorization to rotate credentials,
change production permissions, provision resources, or deploy. #90 is not merge-ready.**

Use the final clean `fix/m12-release-fixes` HEAD recorded in the release handoff.
Build both images from that same checkout. Do not use the dirty `C:/dev` checkout,
its deployment scripts, or the earlier local-only proxy/bootstrap helper.

## 1. Owner credential rotation — independent production maintenance gate

- Human owner/DBA coordinates rotation of the exposed credential through the
  approved production procedure. Do not retrieve or reuse the exposed value.
- Inventory dependent consumers without dumping their env values. The previously
  serving revision used a plaintext DATABASE_URL: rotating only the Secret Manager
  value is not sufficient to update that revision's credential.
- Owner arranges the necessary production-consumer update and verifies production
  health. This can require a separately authorized revision/maintenance operation;
  the preview operator must not perform it implicitly.
- Restrict/redact the exposed transcript through available account controls.
- Record owner confirmation of rotation and successful production verification.
  Never record passwords, complete database URLs, or secret payloads in evidence.

## 2. DBA permission audit — mandatory before preview runtime creation

- DBA examines production **permission metadata**, not application data, through
  an explicitly approved DBA path. The preview operator still has no authorization
  to connect to production. Check database/schema/table/view/sequence privileges,
  PUBLIC grants, inherited roles, ownership, and callable SECURITY DEFINER functions
  or foreign-data paths that could expose production data to a new login.
- Prior preview-only check showed PUBLIC CONNECT on `mneme_audit`. CONNECT is not
  SELECT: this does not prove exposure, but it cannot prove object-level isolation.
  Do not repeat that check as though it settles table access.
- DBA must attest that each proposed preview login has no production data access
  through direct, PUBLIC, inherited, or function/view privileges. If an unwanted
  grant exists, STOP: changing production ACLs needs separate owner approval.
- Do not use the existing production runtime service account for preview runtime:
  it can access the production DB secret. Use the isolated identities below.

## 3. Exact temporary resources and permissions

Reuse project `mneme-hq-prod`, region `us-central1`, Cloud Run service
`mneme-audit-api`, Cloud SQL instance `mneme-audit-db` (PostgreSQL 15), VPC connector
`mneme-vpc-connector`, Cloud SQL attachment
`mneme-hq-prod:us-central1:mneme-audit-db`, and existing `gcr.io` image repository.
Do not create a service, SQL instance, VPC, DNS record, or public database endpoint.

Create only after renewed approval and the preceding security gates:

| Resource | Name | Purpose/access |
| --- | --- | --- |
| Database | `mneme_audit_preview` | Empty, isolated test data only |
| SQL login | `mneme_audit_preview_migrator` | Owns preview schema/objects; DDL only in preview |
| SQL login | `mneme_audit_preview_runtime` | CONNECT + schema USAGE + required table DML in preview; no DDL |
| Runtime service account | `mneme-audit-preview-run@mneme-hq-prod.iam.gserviceaccount.com` | Cloud SQL client; accessor on runtime preview secret only |
| Migration service account | `mneme-audit-preview-migrate@mneme-hq-prod.iam.gserviceaccount.com` | Cloud SQL client; accessor on migrator preview secret only |
| Runtime secret | `mneme-audit-preview-runtime-url` | Full URL with URL-encoded preview password; numeric version pin |
| Migrator secret | `mneme-audit-preview-migrator-url` | Separate preview-only migration credential; numeric version pin |
| Temporary migration job | `mneme-m12-preview-migrate` | One task, no retries, same image digest as web candidate |
| Candidate revision/tag | `mneme-audit-api-m12-<short-sha>` / `m12-rc` | No production traffic; access only via returned tag URL |
| Candidate image tag | `gcr.io/mneme-hq-prod/mneme-audit-api:m12-<full-sha>` | Combined app; deploy by immutable digest |

DBA bootstrap uses only the newly rotated approved admin credential, only against
`mneme_audit_preview`, only in memory, and never in runtime/job config or logs.
Both preview roles must be LOGIN, NOSUPERUSER, NOCREATEDB, NOCREATEROLE,
NOREPLICATION, NOBYPASSRLS, with no privileged role memberships. Do not create them
as default Cloud SQL built-in users that inherit cloudsqlsuperuser.

Within **preview only**, remove PUBLIC schema/database grants as needed; grant
migrator CONNECT and schema CREATE/USAGE/ownership. Grant runtime CONNECT, schema
USAGE, SELECT/INSERT/UPDATE/DELETE on `projects`, `audits`, `contacts`, and
`project_contacts`; grant needed sequence privileges if any. Set migrator default
table grants for runtime before migration. Runtime must not own objects, inherit
migrator, or receive CREATE, TRUNCATE, role management or `alembic_version` writes.
Restrict the post-migration grants to these application tables. Confirm permissions
using catalog checks through preview connections; retain DBA attestation for prod.

Store separate async SQLAlchemy URLs in the new secrets using a secure input/API,
not shell literals or checked-in env files. Required shape (placeholder only):
`postgresql+asyncpg://PREVIEW_USER:ENCODED_PASSWORD@/mneme_audit_preview?host=/cloudsql/mneme-hq-prod:us-central1:mneme-audit-db`.
No project-wide Secret Manager accessor grants. Preview identities must be unable
to access the production secret. Delete any one-off bootstrap helper immediately.

## 4. Pin and build the committed candidate

Run in the clean isolated candidate checkout; stop on any failed command:

```powershell
git status --porcelain
git fetch origin
git merge-base --is-ancestor origin/main HEAD
$candidateSha = git rev-parse HEAD
$candidateShort = git rev-parse --short=12 HEAD
$backendImage = "mneme-m12-backend:$candidateSha"
$previewImage = "gcr.io/mneme-hq-prod/mneme-audit-api:m12-$candidateSha"
docker build --label "org.opencontainers.image.revision=$candidateSha" -f audit/backend/Dockerfile -t $backendImage .
docker build --build-arg "BACKEND_IMAGE=$backendImage" --label "org.opencontainers.image.revision=$candidateSha" -f audit/backend/Dockerfile.preview -t $previewImage .
```

If main advanced, reconcile/retest and obtain candidate approval first. A failed
ancestor check is a stop, not permission to force-push or overwrite another branch.
The preview build uses npm ci and `VITE_API_BASE=/`, packages marketing + workspace
with the exact backend, and serves clean SPA deep links under `/audit/workspace`.
The regular production backend command is unchanged. Preview startup rejects
non-preview database names, administrator usernames, absent credentials and DB_ECHO.
Those checks supplement, not replace, IAM/DB isolation. Record image digest and
dependency inventory; reuse the tested digest rather than rebuilding after E2E.

Push only the reviewed candidate image after approval; resolve its immutable digest
using Artifact Registry. Store it as `$previewDigest`, including repository@sha256.
Confirm app/preview.py, app/api/workspace.py, persistence/comparison modules, Alembic
001, landing HTML, workspace index and its referenced JS/CSS exist in that image.

## 5. Preview-only migration job

Use the migrator identity, VPC connector, Cloud SQL attachment and the candidate
digest. Set only DB_ECHO=false and the preview migrator DATABASE_URL secret at a
specific numeric version. No production env inheritance, credentials, or secret refs.

Job container command: `python`; arguments: `-m,app.preview_migrate,--sql` for dry
run. Review generated SQL. Then execute the same image as `-m,app.preview_migrate`
for online migration. One task, parallelism 1, max retries 0, timeout 300s,
1 CPU/512Mi. The entry point checks database/user before engine creation and checks
current_database() before DDL. It must finish at Alembic 001. No migrations on web
startup, no production migration, no blind stamp, reset or truncate.

Verify preview runtime can perform required DML, cannot create tables or SET ROLE
to migrator, and cannot access production secrets. Never probe production data.
Retain the DBA object-permission audit as the production-isolation evidence.

## 6. No-traffic revision — service mutations limited to the new candidate

Capture redacted pre-deploy revision identity, exact traffic assignments/tags,
IAM/ingress, VPC/Cloud SQL attachment, and service-wide scaling. **Do not dump full
environment values.** Use the post-rotation serving revision as the baseline; it
may differ from the previously observed `mneme-audit-api-00020-zjp`.
Check `m12-rc` is unused or belongs to this task. Stop on an unexpected existing tag.

After the safety gates, deployment command template (numeric secret version must
be supplied from the approved resource manifest):

```powershell
gcloud run deploy mneme-audit-api --project=mneme-hq-prod --region=us-central1 --image=$previewDigest --revision-suffix="m12-$candidateShort" --no-traffic --tag=m12-rc --service-account=mneme-audit-preview-run@mneme-hq-prod.iam.gserviceaccount.com --vpc-connector=mneme-vpc-connector --vpc-egress=private-ranges-only --set-cloudsql-instances=mneme-hq-prod:us-central1:mneme-audit-db --set-env-vars="DB_ECHO=false,DB_POOL_DISABLED=true,APP_VERSION=m12-$candidateShort" --set-secrets="DATABASE_URL=mneme-audit-preview-runtime-url:$runtimeSecretVersion" --cpu=1 --memory=1Gi --concurrency=1 --min-instances=0 --max-instances=1 --timeout=300 --port=8000 --command='' --args=''
```

`--set-env-vars` and `--set-secrets` replace candidate environment/secret mappings;
never merge the production DATABASE_URL. Empty command/args select the image's
preview entry point. Do not pass service-wide `--min`, `--max`, IAM, ingress,
unauthenticated, DNS, or traffic-promotion flags. Verify the resulting spec before
sending test requests: correct image digest, runtime identity, only preview DB
secret, and preview entry point. Tags inherit the existing service's access policy:
no authentication-policy change is authorized; use public non-sensitive inputs only.

Confirm production still routes 100% to the exact pre-deploy revision (or identical
preexisting split), with no candidate allocation. Cloud Run may pin a previous
LATEST allocation when using --no-traffic; actual recipients/percentages must not
change. Do not use --to-latest during preview or cleanup. Record the returned tag
URL, don't guess its hostname. Check /health, /audit/, workspace assets and deep links.

## 7. Real deployed browser release gate

Using the tag URL, execute **Audit → Result → Save Baseline → Project → hard refresh
→ Re-audit → Compare → hard refresh**. Use the public demo repository for persistence;
use `tests/fixtures/guardrail-ready/AGENTS.md` in a ZIP for positive Mneme-ready
evidence. The real ZIP pipeline integration test verifies its explicit sqlite3
constraint yields a serializable supported guardrail. This is a test input, not a
mocked audit or a rule invented for an actual repository. Do not modify its result.

Record screenshots, browser console and redacted request/response evidence:

- Schema mneme.audit/v1, non-empty stable project/audit IDs, backend score/count
  agreement, no NaN or frontend score/transition/classification reconstruction.
- Correct four classifications; Guidance secondary; potential conditional on ready.
- Every Mneme-ready has a non-empty supported guardrail and working View guardrail;
  Requires modelling has Review protection gap and no false enforcement promise.
- Baseline save and saved lifecycle; exact repository SHA, version and timestamps.
- Project and Compare clean URLs survive hard refresh and independent navigation.
- Re-audit creates a distinct persisted audit; baseline ID/payload hash unchanged.
- Compare baseline/latest IDs, backend deltas, narrative counts and item states agree.
  Unchanged repo validates unchanged states; other states need controlled repository
  changes or separate backend fixtures, not claims that one identical rerun covers all.
- Desktop/mobile layouts, long text, loading/empty/error states, back/forward, links,
  keyboard access; no core runtime errors or unexpected failed requests.
- No credential, production data, or sensitive infrastructure details in responses.

PASS only after all required checks. Unit/build success is not deployed E2E success.
Do not merge frontend #90 before the backend dependency/release path is agreed.

## 8. Evidence and cleanup

- Export only preview test results and IDs before deletion. Record SHA/digest/tag URL,
  final tests and explicit PASS/FAIL. Do not export secrets or production data.
- Remove only this task's m12-rc tag; delete the exact zero-traffic candidate revision.
  Verify it is not a serving revision before deletion. Recheck production allocation.
- Delete the temporary migration job/executions and preview database, then the two
  preview SQL roles, two secrets, preview-only IAM grants and two preview identities.
  DBA handles role/object dependency cleanup against preview only. Confirm exact names
  against the creation manifest; never delete shared infrastructure or broad resources.
- Keep the tested image digest until release decision/retention approval. Delete only
  task-owned image versions later, never shared tags such as latest/production.
- Do not restore traffic with --to-latest. Do not update the production DB/revision as
  a cleanup shortcut. Reconfirm original traffic recipients, IAM, DNS and shared infra.

References: [Cloud Run deploy flags](https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy),
[no-traffic tagged revisions](https://docs.cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration),
[PostgreSQL privilege boundaries](https://www.postgresql.org/docs/current/ddl-priv.html).
