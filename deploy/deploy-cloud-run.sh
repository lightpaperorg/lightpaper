#!/bin/bash
# Deploy lightpaper.org to Cloud Run
# Prerequisites: Cloud SQL instance created via setup-cloud-sql.sh

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID environment variable}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="lightpaper"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/api"

# Cloud SQL connection (update after running setup-cloud-sql.sh)
CLOUD_SQL_CONNECTION="${CLOUD_SQL_CONNECTION:-$PROJECT_ID:$REGION:lightpaper-db}"

echo "=== Building container image ==="
gcloud builds submit \
  --project="$PROJECT_ID" \
  --tag="$IMAGE" \
  --timeout=600

echo "=== Deploying to Cloud Run ==="
gcloud run deploy "$SERVICE_NAME" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --image="$IMAGE" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --cpu=2 \
  --memory=2Gi \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=120 \
  --concurrency=100 \
  --add-cloudsql-instances="$CLOUD_SQL_CONNECTION" \
  --set-env-vars="^||^FIREBASE_PROJECT_ID=$PROJECT_ID||BASE_URL=https://lightpaper.org||CORS_ORIGINS=https://lightpaper.org,http://localhost:3000" \
  --update-secrets="DATABASE_URL=lightpaper-db-url:latest,RESEND_API_KEY=resend-api-key:latest,LINKEDIN_CLIENT_ID=linkedin-client-id:latest,LINKEDIN_CLIENT_SECRET=linkedin-client-secret:latest,GSC_SERVICE_ACCOUNT_KEY=gsc-service-account-key:latest"

echo ""
echo "=== Deployment complete ==="
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --project="$PROJECT_ID" --region="$REGION" --format="value(status.url)")
echo "Service URL: $SERVICE_URL"
echo ""
echo "Health check:"
echo "  curl $SERVICE_URL/health"
echo ""
echo "Next steps:"
echo "  1. Map custom domain: gcloud run domain-mappings create --service=$SERVICE_NAME --domain=lightpaper.org --region=$REGION"
echo "  2. Configure DNS: CNAME lightpaper.org → ghs.googlehosted.com"
echo "  3. SSL certificate will auto-provision (takes ~15 minutes)"
