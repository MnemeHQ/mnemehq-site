#!/usr/bin/env bash
# provision_infrastructure.sh - Provision Cloud SQL PostgreSQL and related infrastructure
#
# This script provisions:
# 1. Cloud SQL PostgreSQL instance
# 2. Database and user
# 3. Secret Manager secret for DB password
# 4. VPC connector for Cloud Run
# 5. Service account for Cloud Run
#
# Usage: ./provision_infrastructure.sh [environment]
#   environment: prod (default) or staging

set -euo pipefail

ENVIRONMENT="${1:-prod}"
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${REGION:-us-central1}"
INSTANCE_NAME="${INSTANCE_NAME:-mneme-audit-db}"
DB_NAME="${DB_NAME:-mneme_audit}"
DB_USER="${DB_USER:-mneme_audit_user}"
DB_PASSWORD_SECRET="${DB_PASSWORD_SECRET:-mneme-audit-db-password}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-mneme-audit-run@${PROJECT_ID}.iam.gserviceaccount.com}"
VPC_CONNECTOR="${VPC_CONNECTOR:-mneme-vpc-connector}"
VPC_NETWORK="${VPC_NETWORK:-default}"
VPC_SUBNET="${VPC_SUBNET:-mneme-vpc-subnet}"

echo "=========================================="
echo "Provisioning Mneme Audit Infrastructure"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Instance: ${INSTANCE_NAME}"
echo "Database: ${DB_NAME}"
echo "=========================================="

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    run.googleapis.com \
    vpcaccess.googleapis.com \
    servicenetworking.googleapis.com \
    --project="${PROJECT_ID}"

# Create VPC subnet for Cloud SQL private IP if it doesn't exist
echo "Checking VPC subnet..."
if ! gcloud compute networks subnets describe "${VPC_SUBNET}" --region="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
    echo "Creating VPC subnet..."
    gcloud compute networks subnets create "${VPC_SUBNET}" \
        --network="${VPC_NETWORK}" \
        --range=10.0.0.0/24 \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --purpose=PRIVATE_SERVICE_CONNECT
else
    echo "VPC subnet already exists"
fi

# Reserve IP range for Cloud SQL private IP
echo "Reserving IP range for Cloud SQL..."
if ! gcloud compute addresses describe "google-managed-services-${VPC_NETWORK}" --global --project="${PROJECT_ID}" &>/dev/null; then
    gcloud compute addresses create "google-managed-services-${VPC_NETWORK}" \
        --global \
        --purpose=VPC_PEERING \
        --prefix-length=16 \
        --network="${VPC_NETWORK}" \
        --project="${PROJECT_ID}"
fi

# Create VPC peering connection
echo "Creating VPC peering connection..."
if ! gcloud services vpc-peerings list --network="${VPC_NETWORK}" --project="${PROJECT_ID}" --format="value(name)" | grep -q "servicenetworking-googleapis-com"; then
    gcloud services vpc-peerings connect \
        --service=servicenetworking.googleapis.com \
        --ranges="google-managed-services-${VPC_NETWORK}" \
        --network="${VPC_NETWORK}" \
        --project="${PROJECT_ID}"
fi

# Create Cloud SQL instance
echo "Creating Cloud SQL PostgreSQL instance..."
if ! gcloud sql instances describe "${INSTANCE_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud sql instances create "${INSTANCE_NAME}" \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region="${REGION}" \
        --network="${VPC_NETWORK}" \
        --no-assign-ip \
        --enable-private-ip \
        --storage-type=SSD \
        --storage-size=10GB \
        --storage-auto-increase \
        --backup-start-time=03:00 \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=04 \
        --deletion-protection \
        --project="${PROJECT_ID}"
else
    echo "Cloud SQL instance already exists"
fi

# Create database
echo "Creating database..."
if ! gcloud sql databases describe "${DB_NAME}" --instance="${INSTANCE_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud sql databases create "${DB_NAME}" \
        --instance="${INSTANCE_NAME}" \
        --project="${PROJECT_ID}"
else
    echo "Database already exists"
fi

# Create database user with generated password
echo "Creating database user..."
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
if ! gcloud sql users describe "${DB_USER}" --instance="${INSTANCE_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud sql users create "${DB_USER}" \
        --instance="${INSTANCE_NAME}" \
        --password="${DB_PASSWORD}" \
        --project="${PROJECT_ID}"
else
    echo "User already exists, updating password..."
    gcloud sql users set-password "${DB_USER}" \
        --instance="${INSTANCE_NAME}" \
        --password="${DB_PASSWORD}" \
        --project="${PROJECT_ID}"
fi

# Store password in Secret Manager
echo "Storing password in Secret Manager..."
if ! gcloud secrets describe "${DB_PASSWORD_SECRET}" --project="${PROJECT_ID}" &>/dev/null; then
    echo -n "${DB_PASSWORD}" | gcloud secrets create "${DB_PASSWORD_SECRET}" \
        --data-file=- \
        --project="${PROJECT_ID}"
else
    echo -n "${DB_PASSWORD}" | gcloud secrets versions add "${DB_PASSWORD_SECRET}" \
        --data-file=- \
        --project="${PROJECT_ID}"
fi

# Grant Secret Manager access to service account
echo "Granting Secret Manager access..."
gcloud secrets add-iam-policy-binding "${DB_PASSWORD_SECRET}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --project="${PROJECT_ID}"

# Create service account for Cloud Run
echo "Creating service account..."
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud iam service-accounts create "mneme-audit-run" \
        --display-name="Mneme Audit Cloud Run Service Account" \
        --project="${PROJECT_ID}"
else
    echo "Service account already exists"
fi

# Grant Cloud SQL Client role to service account
echo "Granting Cloud SQL Client role..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/cloudsql.client"

# Create VPC connector
echo "Creating VPC connector..."
if ! gcloud compute networks vpc-access connectors describe "${VPC_CONNECTOR}" --region="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud compute networks vpc-access connectors create "${VPC_CONNECTOR}" \
        --region="${REGION}" \
        --network="${VPC_NETWORK}" \
        --subnet="${VPC_SUBNET}" \
        --min-instances=2 \
        --max-instances=10 \
        --project="${PROJECT_ID}"
else
    echo "VPC connector already exists"
fi

echo "=========================================="
echo "Infrastructure provisioning complete!"
echo "=========================================="
echo "Instance: ${INSTANCE_NAME}"
echo "Database: ${DB_NAME}"
echo "User: ${DB_USER}"
echo "Password secret: ${DB_PASSWORD_SECRET}"
echo "Service account: ${SERVICE_ACCOUNT}"
echo "VPC connector: ${VPC_CONNECTOR}"
echo ""
echo "Next steps:"
echo "1. Run database migrations: cd audit/backend && alembic upgrade head"
echo "2. Deploy audit service: ./deploy/deploy_audit.sh"
echo "=========================================="