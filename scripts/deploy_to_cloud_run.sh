#!/bin/bash
# Quick deployment script to Google Cloud Run
# Uses project ID: llm-reliability-control

set -e

PROJECT_ID="llm-reliability-control"
REGION="us-central1"
SERVICE_NAME="llm-reliability-control-plane"

echo "🚀 Deploying to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📦 Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com \
    --project=$PROJECT_ID

# Build and push Docker image
echo ""
echo "🐳 Building Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --project=$PROJECT_ID

# Deploy to Cloud Run
echo ""
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars "DD_SERVICE=llm-reliability-control-plane,DD_ENV=production,DD_VERSION=1.0.0,DD_LLMOBS_AGENTLESS_ENABLED=1,DD_TRACE_ENABLED=true,DD_LOGS_ENABLED=true,DD_SITE=datadoghq.com,LRCP_GCP_PROJECT_ID=$PROJECT_ID" \
  --set-secrets "LRCP_GEMINI_API_KEY=gemini-api-key:latest,LRCP_DATADOG_API_KEY=datadog-api-key:latest,DD_APP_KEY=datadog-app-key:latest,LRCP_CONFLUENT_BOOTSTRAP_SERVERS=confluent-bootstrap:latest,LRCP_CONFLUENT_API_KEY=confluent-api-key:latest,LRCP_CONFLUENT_API_SECRET=confluent-api-secret:latest" \
  --project=$PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' --project=$PROJECT_ID)

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📋 Test endpoints:"
echo "  Health: $SERVICE_URL/health"
echo "  API Docs: $SERVICE_URL/docs"
echo "  Products: $SERVICE_URL/datadog/products"
echo ""
echo "💡 Next steps:"
echo "  1. Update datadog/workflows.json - Replace {{APP_URL}} with: $SERVICE_URL"
echo "  2. Import Datadog resources (see DATADOG_IMPORT_GUIDE.md)"
echo "  3. Test the application"
echo ""

