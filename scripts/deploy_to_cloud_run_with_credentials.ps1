# PowerShell script to deploy to Google Cloud Run with your credentials
# Run this after running setup_secrets_with_credentials.ps1

$PROJECT_ID = "llm-reliability-control"
$REGION = "us-central1"
$SERVICE_NAME = "llm-reliability-control-plane"
$DD_SITE = "us5.datadoghq.com"

Write-Host "Deploying to Google Cloud Run" -ForegroundColor Green
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service: $SERVICE_NAME"
Write-Host "Datadog Site: $DD_SITE"
Write-Host ""

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable `
    cloudbuild.googleapis.com `
    run.googleapis.com `
    containerregistry.googleapis.com `
    secretmanager.googleapis.com `
    aiplatform.googleapis.com `
    --project=$PROJECT_ID

# Build and push Docker image
Write-Host ""
Write-Host "Building Docker image..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest --project=$PROJECT_ID

# Deploy to Cloud Run
Write-Host ""
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
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
  --set-env-vars "DD_SERVICE=llm-reliability-control-plane,DD_ENV=production,DD_VERSION=1.0.0,DD_LLMOBS_AGENTLESS_ENABLED=1,DD_TRACE_ENABLED=true,DD_LOGS_ENABLED=true,DD_SITE=$DD_SITE,LRCP_GCP_PROJECT_ID=$PROJECT_ID" `
  --set-secrets "LRCP_GEMINI_API_KEY=gemini-api-key:latest,LRCP_DATADOG_API_KEY=datadog-api-key:latest,DD_APP_KEY=datadog-app-key:latest,LRCP_CONFLUENT_BOOTSTRAP_SERVERS=confluent-bootstrap:latest,LRCP_CONFLUENT_API_KEY=confluent-api-key:latest,LRCP_CONFLUENT_API_SECRET=confluent-api-secret:latest" `
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
