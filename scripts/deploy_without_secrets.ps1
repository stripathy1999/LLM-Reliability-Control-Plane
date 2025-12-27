# PowerShell script to deploy to Google Cloud Run WITHOUT Secret Manager
# This uses environment variables directly (no billing required for basic Cloud Run)
# Run this if Secret Manager API requires billing

$PROJECT_ID = "llm-reliability-control"
$REGION = "us-central1"
$SERVICE_NAME = "llm-reliability-control-plane"
$DD_SITE = "us5.datadoghq.com"

# Your credentials (will be passed as environment variables)
$GEMINI_API_KEY = "AIzaSyBjZGBe204-N215wVOyh8K6ksGbKAi8JNc"
$DATADOG_API_KEY = "e38221fb258a4ea3ec8bd312db36fa6e"
$DATADOG_APP_KEY = "ef51694759c084b54ecd2ced19579924c9eb968c"

# Confluent credentials
$CONFLUENT_BOOTSTRAP = "pkc-619z3.us-east1.gcp.confluent.cloud:9092"
$CONFLUENT_API_KEY = "53CGSDMC2E7HOPN3"
$CONFLUENT_API_SECRET = "cfltC5QSsc7nWwn7nA1v68Q8kdsBBVbst2n89xtQ2S3Srzf7r761vZjOStlyBqDg"

Write-Host "Deploying to Google Cloud Run (without Secret Manager)" -ForegroundColor Green
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service: $SERVICE_NAME"
Write-Host "Datadog Site: $DD_SITE"
Write-Host ""
Write-Host "Note: Using environment variables directly (no Secret Manager required)" -ForegroundColor Yellow
Write-Host ""

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs (these don't require billing)
Write-Host "Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable `
    cloudbuild.googleapis.com `
    run.googleapis.com `
    containerregistry.googleapis.com `
    --project=$PROJECT_ID

# Build and push Docker image
Write-Host ""
Write-Host "Building Docker image..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest --project=$PROJECT_ID

# Deploy to Cloud Run with environment variables directly
Write-Host ""
Write-Host "Deploying to Cloud Run with environment variables..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest `
  --region $REGION `
  --platform managed `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 2 `
  --timeout 300 `
  --max-instances 10 `
  --min-instances 0 `
  --set-env-vars "DD_SERVICE=llm-reliability-control-plane,DD_ENV=production,DD_VERSION=1.0.0,DD_LLMOBS_AGENTLESS_ENABLED=1,DD_TRACE_ENABLED=true,DD_LOGS_ENABLED=true,DD_SITE=$DD_SITE,LRCP_GCP_PROJECT_ID=$PROJECT_ID,LRCP_GEMINI_API_KEY=$GEMINI_API_KEY,LRCP_DATADOG_API_KEY=$DATADOG_API_KEY,DD_APP_KEY=$DATADOG_APP_KEY,LRCP_CONFLUENT_BOOTSTRAP_SERVERS=$CONFLUENT_BOOTSTRAP,LRCP_CONFLUENT_API_KEY=$CONFLUENT_API_KEY,LRCP_CONFLUENT_API_SECRET=$CONFLUENT_API_SECRET" `
  --project=$PROJECT_ID

# Get service URL
$SERVICE_URL = (gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' --project=$PROJECT_ID)

Write-Host ""
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test endpoints:" -ForegroundColor Yellow
Write-Host "  Health: $SERVICE_URL/health"
Write-Host "  API Docs: $SERVICE_URL/docs"
Write-Host "  Products: $SERVICE_URL/datadog/products"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Update datadog/workflows.json - Replace {{APP_URL}} with: $SERVICE_URL"
Write-Host "  2. Import Datadog resources (see DATADOG_IMPORT_GUIDE.md)"
Write-Host "  3. Test the application"
Write-Host ""
Write-Host "Save this URL for your submission: $SERVICE_URL" -ForegroundColor Cyan

