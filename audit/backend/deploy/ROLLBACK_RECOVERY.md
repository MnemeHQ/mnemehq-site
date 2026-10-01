# Mneme Audit M1 - Rollback & Recovery Procedure

## Overview

This document describes the rollback and recovery procedures for the Mneme Audit M1 Cloud Run deployment with Cloud SQL PostgreSQL.

## Architecture Summary

- **Service**: `mneme-audit-api` on Cloud Run
- **Database**: Cloud SQL PostgreSQL 15 (`mneme-audit-db`)
- **Networking**: Private IP via VPC connector (`mneme-vpc-connector`)
- **Secrets**: Secret Manager (`mneme-audit-db-password`)
- **Deployment**: GitHub Actions → Cloud Run (container) + Cloud SQL Auth Proxy

---

## Rollback Procedures

### 1. Application Rollback (Container)

**Trigger**: New deployment has bugs, health checks fail, or performance regression.

```bash
# List recent revisions
gcloud run revisions list --service=mneme-audit-api --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic mneme-audit-api \
  --to-revisions=PREVIOUS_REVISION=100 \
  --region=us-central1

# Or rollback to specific revision
gcloud run services update-traffic mneme-audit-api \
  --to-revisions=mneme-audit-api-00042=100 \
  --region=us-central1
```

**Verification**:
```bash
# Check traffic split
gcloud run services describe mneme-audit-api --region=us-central1

# Health check
curl https://mneme-audit-api-xxxx-uc.a.run.app/health
```

### 2. Database Migration Rollback

**Trigger**: Migration causes data issues or application incompatibility.

```bash
# Check current migration version
gcloud sql connect mneme-audit-db --user=mneme_audit_user --database=mneme_audit
# In psql:
SELECT version_num FROM alembic_version;

# Rollback one migration
cd audit/backend
export DATABASE_URL="postgresql+asyncpg://user:pass@/mneme_audit?host=/cloudsql/project:region:instance"
alembic downgrade -1

# Or rollback to specific revision
alembic downgrade 001
```

**If migration cannot be rolled back** (destructive changes):
1. Restore database from Cloud SQL backup (see below)
2. Rollback application to matching revision

### 3. Database Restore from Backup

**Trigger**: Data corruption, accidental deletion, or migration rollback impossible.

```bash
# List available backups
gcloud sql backups list --instance=mneme-audit-db

# Create a new instance from backup (point-in-time recovery)
gcloud sql instances clone mneme-audit-db mneme-audit-db-restore \
  --point-in-time="2026-09-02T10:00:00Z" \
  --region=us-central1

# Update Cloud Run service to point to restored instance
# 1. Update Cloud SQL connection name in service.yaml
# 2. Deploy new revision
# 3. Verify health
# 4. Delete old instance after verification
```

---

## Recovery Procedures

### 1. Cloud Run Service Won't Start

**Symptoms**: Service shows "Revision failed to start" or health checks fail.

**Diagnosis**:
```bash
# Check revision logs
gcloud run revisions logs read mneme-audit-api-00042 --region=us-central1 --limit=100

# Check service events
gcloud run services describe mneme-audit-api --region=us-central1
```

**Common Causes & Fixes**:

| Cause | Fix |
|-------|-----|
| Cloud SQL Auth Proxy not connecting | Check VPC connector, private IP, service account permissions |
| Database migration failed | Check migration logs, rollback migration |
| Secret Manager access denied | Check service account has `roles/secretmanager.secretAccessor` |
| Health check timeout | Increase `startupProbe.failureThreshold` or check `/health` endpoint |

### 2. Database Connection Failures

**Symptoms**: Application returns 500, logs show connection errors.

**Diagnosis**:
```bash
# Test Cloud SQL Auth Proxy locally
cloud-sql-proxy --port 5432 project:region:instance &
psql "postgresql://user:pass@localhost:5432/db"

# Check Cloud SQL instance status
gcloud sql instances describe mneme-audit-db --region=us-central1

# Check VPC connector
gcloud compute networks vpc-access connectors describe mneme-vpc-connector --region=us-central1
```

**Common Causes & Fixes**:

| Cause | Fix |
|-------|-----|
| VPC connector down | Recreate VPC connector, check subnet |
| Private IP not accessible | Check VPC peering, servicenetworking API enabled |
| Service account lacks Cloud SQL Client role | Grant `roles/cloudsql.client` |
| Instance stopped | Start instance, check maintenance window |

### 3. Secret Manager Access Denied

**Symptoms**: Application fails to read DB password at startup.

**Diagnosis**:
```bash
# Test secret access
gcloud secrets versions access latest --secret=mneme-audit-db-password

# Check service account permissions
gcloud secrets get-iam-policy mneme-audit-db-password
```

**Fix**:
```bash
# Grant secret accessor role
gcloud secrets add-iam-policy-binding mneme-audit-db-password \
  --member=serviceAccount:mneme-audit-run@project.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### 4. Database Migration Stuck

**Symptoms**: `alembic upgrade head` hangs or fails.

**Diagnosis**:
```bash
# Check for locks
psql -c "SELECT * FROM pg_locks WHERE NOT granted;"

# Check alembic version table
psql -c "SELECT * FROM alembic_version;"
```

**Fix**:
```bash
# If stuck on advisory lock
psql -c "SELECT pg_advisory_unlock_all();"

# Force downgrade/upgrade
alembic stamp head  # If DB is correct but version table wrong
alembic upgrade head  # Retry
```

---

## Disaster Recovery Checklist

### Pre-Incident Preparation

- [ ] Document current revision and database version before each deploy
- [ ] Verify Cloud SQL automated backups enabled (daily, 7-day retention)
- [ ] Test point-in-time recovery quarterly
- [ ] Verify Secret Manager secret rotation procedure
- [ ] Document service account permissions

### During Incident

1. **Assess impact**: Check health endpoint, error rates, user impact
2. **Communicate**: Update status page, notify stakeholders
3. **Isolate**: Route traffic to previous revision if app issue
4. **Diagnose**: Check logs, metrics, database status
5. **Resolve**: Apply fix or rollback
6. **Verify**: Health checks, smoke test, user acceptance
7. **Document**: Record incident, root cause, resolution

### Post-Incident

- [ ] Update runbook with new findings
- [ ] Conduct post-mortem if severity warrants
- [ ] Update monitoring/alerting if gaps found
- [ ] Schedule follow-up review

---

## Emergency Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| Primary On-Call | [Name] | Immediate |
| Secondary On-Call | [Name] | 15 min |
| GCP Support | Case in Cloud Console | P1: 15 min |

---

## Useful Commands Quick Reference

```bash
# Service management
gcloud run services describe mneme-audit-api --region=us-central1
gcloud run services update-traffic mneme-audit-api --to-latest --region=us-central1
gcloud run revisions list --service=mneme-audit-api --region=us-central1

# Database
gcloud sql instances describe mneme-audit-db --region=us-central1
gcloud sql connect mneme-audit-db --user=mneme_audit_user --database=mneme_audit
gcloud sql backups list --instance=mneme-audit-db

# Logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mneme-audit-api" --limit=50
gcloud run revisions logs read REVISION_NAME --region=us-central1

# Secrets
gcloud secrets versions access latest --secret=mneme-audit-db-password
gcloud secrets list --filter="name:mneme-audit"

# VPC
gcloud compute networks vpc-access connectors describe mneme-vpc-connector --region=us-central1
```

---

## Version History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-09-02 | 1.0 | M1.1 Team | Initial creation |