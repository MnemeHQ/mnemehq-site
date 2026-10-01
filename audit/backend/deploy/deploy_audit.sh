#!/usr/bin/env bash
# deploy_audit.sh - Deploy Mneme Audit API to Cloud Run with Cloud SQL
#
# Usage: ./deploy_audit.sh [environment]
#   environment: prod (default) or staging
#
# Required environment variables:
#   PROJECT_ID - GCP project ID
#   REGION - GCP region (e.g., us-central1)
#   INSTANCE_NAME - Cloud SQL instance name
#   DB_NAME - Database name
#   DB_USER - Database user
#   DB_PASSWORD_SECRET - Secret Manager secret name for DB password
#   SERVICE_ACCOUNT - Cloud Run service account email
#   VPC_CONNECTOR - VPC connector name
#   IMAGE_URL - Container image URL (or will be built)
#   APP_VERSION - Application version tag

set -euo pipefail

ENVIRONMENT="${1:-prod}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Default values
REGION="${REGION:-us-central1}"
APP_VERSION="${APP_VERSION:-$(git rev-parse --short HEAD)}"
SERVICE_NAME="mneme-audit-api"

echo "=========================================="
echo "Deploying Mneme Audit API to Cloud Run"
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "App Version: ${APP_VERSION}"
echo "=========================================="

# Validate required environment variables
required_vars=(
    "PROJECT_ID"
    "REGION"
    "INSTANCE_NAME"
    "DB_NAME"
    "DB_USER"
    "DB_PASSWORD_SECRET"
    "SERVICE_ACCOUNT"
    "VPC_CONNECTOR"
)

for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        echo "ERROR: Required environment variable ${var} is not set"
        exit 1
    fi
done

# Set gcloud project
gcloud config set project "${PROJECT_ID}"

# Build and push Docker image
IMAGE_URL="${IMAGE_URL:-gcr.io/${PROJECT_ID}/mneme-audit-api:${APP_VERSION}}"
echo "Building image: ${IMAGE_URL}"
cd "${PROJECT_ROOT}"
docker build -f audit/backend/Dockerfile -t "${IMAGE_URL}" .
docker push "${IMAGE_URL}"

# Run database migrations
echo "Running database migrations..."
# Use Cloud SQL Auth Proxy for migration
cloud_sql_proxy -instances="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"=tcp:5432 &
PROXY_PID=$!
sleep 3

export DATABASE_URL="postgresql+asyncpg://${DB_USER}:$(gcloud secrets versions access latest --secret="${DB_PASSWORD_SECRET}")@localhost:5432/${DB_NAME}"
cd "${PROJECT_ROOT}/audit/backend"
alembic upgrade head

# Kill the proxy
kill $PROXY_PID

# Deploy to Cloud Run using service.yaml template
echo "Deploying to Cloud Run..."
# Substitute environment variables in service.yaml
sed -e "s|\${PROJECT_ID}|${PROJECT_ID}|g" \
    -e "s|\${REGION}|${REGION}|g" \
    -e "s|\${INSTANCE_NAME}|${INSTANCE_NAME}|g" \
    -e "s|\${PROJECT_ID}:${REGION}:${INSTANCE_NAME}|${PROJECT_ID}:${REGION}:${INSTANCE_NAME}|g" \
    -e "s|\${SERVICE_ACCOUNT}|${SERVICE_ACCOUNT}|g" \
    -e "s|\${VPC_CONNECTOR}|${VPC_CONNECTOR}|g" \
    -e "s|\${IMAGE_URL}|${IMAGE_URL}|g" \
    -e "s|\${DB_USER}|${DB_USER}|g" \
    -e "s|\${DB_PASSWORD}|$(gcloud secrets versions access latest --secret="${DB_PASSWORD_SECRET}")|g" \
    -e "s|\${APP_VERSION}|${APP_VERSION}|g" \
    -e "s|\${PROJECT_ID}:${REGION}:${INSTANCE_NAME}|${PROJECT_ID}:${REGION}:${INSTANCE_NAME}|g" \
    "${SCRIPT_DIR}/service.yaml" | gcloud run services replace - --region="${REGION}"

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
gcloud run services wait "${SERVICE_NAME}" --region="${REGION}" --timeout=300s

# Get service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --format="value(status.url)")
echo "=========================================="
echo "Deployment complete!"
echo "Service URL: ${SERVICE_URL}"
echo "=========================================="

# Health check
echo "Running health check..."
if curl -sf "${SERVICE_URL}/health" > /dev/null; then
    echo "Health check PASSED"
else
    echo "Health check FAILED"
    exit 1
fi