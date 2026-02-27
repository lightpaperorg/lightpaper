#!/bin/bash
# Create Cloud SQL PostgreSQL instance for lightpaper.org
# Run once, then use deploy-cloud-run.sh for app deployments.

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID environment variable}"
REGION="${GCP_REGION:-us-central1}"
INSTANCE_NAME="lightpaper-db"
DB_NAME="lightpaper"
DB_USER="lightpaper"

echo "=== Creating Cloud SQL PostgreSQL instance ==="
gcloud sql instances create "$INSTANCE_NAME" \
  --project="$PROJECT_ID" \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region="$REGION" \
  --storage-type=SSD \
  --storage-size=10GB \
  --storage-auto-increase \
  --availability-type=zonal \
  --no-assign-ip \
  --network=default \
  --enable-google-private-path

echo "=== Setting database password ==="
DB_PASSWORD=$(openssl rand -base64 24)
gcloud sql users set-password postgres \
  --instance="$INSTANCE_NAME" \
  --project="$PROJECT_ID" \
  --password="$DB_PASSWORD"

echo "=== Creating database ==="
gcloud sql databases create "$DB_NAME" \
  --instance="$INSTANCE_NAME" \
  --project="$PROJECT_ID"

echo "=== Creating application user ==="
gcloud sql users create "$DB_USER" \
  --instance="$INSTANCE_NAME" \
  --project="$PROJECT_ID" \
  --password="$DB_PASSWORD"

echo "=== Initializing schema ==="
# Connect via Cloud SQL Proxy and run init.sql
CONN_NAME=$(gcloud sql instances describe "$INSTANCE_NAME" --project="$PROJECT_ID" --format="value(connectionName)")
echo "Connection name: $CONN_NAME"
echo ""
echo "Run the following to initialize the schema:"
echo "  cloud-sql-proxy $CONN_NAME &"
echo "  psql -h 127.0.0.1 -U $DB_USER -d $DB_NAME -f init.sql"
echo ""
echo "=== Store these values ==="
echo "CLOUD_SQL_CONNECTION: $CONN_NAME"
echo "DATABASE_URL: postgresql+asyncpg://$DB_USER:$DB_PASSWORD@/$DB_NAME?host=/cloudsql/$CONN_NAME"
echo "DB_PASSWORD: $DB_PASSWORD"
echo ""
echo "Save the password — it won't be shown again."
