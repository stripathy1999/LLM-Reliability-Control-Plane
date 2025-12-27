# Simplified deployment script that handles permissions and uses environment variables
# This is the easiest way to deploy without Secret Manager issues

$PROJECT_ID = "llm-reliability-control"
$REGION = "us-central1"
$SERVICE_NAME = "llm-reliability-control-plane"
$DD_SITE = "us5.datadoghq.com"

# Your credentials
$GEMINI_API_KEY = "AIzaSyBjZGBe204-N215wVOyh8K6ksGbKAi8JNc"
$DATADOG_API_KEY = "e38221fb258a4ea3ec8bd312db36fa6e"
$DATADOG_APP_KEY = "ef51694759c084b54ecd2ced19579924c9eb968c"

Write-Host "Deploying to Google Cloud Run (Simple Method)" -ForegroundColor Green
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service: $SERVICE_NAME"
Write-Host ""

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable `
    cloudbuild.googleapis.com `
    run.googleapis.com `
    containerregistry.googleapis.com `
    --project=$PROJECT_ID

# Grant necessary permissions to current user
Write-Host ""
Write-Host "Granting necessary permissions..." -ForegroundColor Yellow
$USER_EMAIL = (gcloud config get-value account)
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="user:$USER_EMAIL" `
    --role="roles/cloudbuild.builds.editor" 2>$null

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="user:$USER_EMAIL" `
    --role="roles/iam.serviceAccountUser" 2>$null

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="user:$USER_EMAIL" `
    --role="roles/run.admin" 2>$null

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="user:$USER_EMAIL" `
    --role="roles/storage.admin" 2>$null

Write-Host "Waiting 10 seconds for permissions to propagate..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Build and push Docker image
Write-Host ""
Write-Host "Building Docker image..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest --project=$PROJECT_ID

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Build failed. Trying alternative: Build locally and push..." -ForegroundColor Yellow
    Write-Host "This requires Docker to be installed and running." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Use Cloud Shell or enable billing for Cloud Build." -ForegroundColor Yellow
    exit 1
}

# Check if service exists and clear environment variables if needed
Write-Host ""
Write-Host "Checking existing service..." -ForegroundColor Yellow
$serviceExists = gcloud run services describe $SERVICE_NAME --region $REGION --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Service exists. Clearing existing environment variables..." -ForegroundColor Yellow
    # Clear all environment variables first
    gcloud run services update $SERVICE_NAME `
      --region $REGION `
      --clear-env-vars `
      --project=$PROJECT_ID 2>$null
    Write-Host "Waiting 5 seconds for update to propagate..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

# Deploy to Cloud Run with environment variables directly
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
  --set-env-vars "DD_SERVICE=llm-reliability-control-plane,DD_ENV=production,DD_VERSION=1.0.0,DD_LLMOBS_AGENTLESS_ENABLED=1,DD_TRACE_ENABLED=true,DD_LOGS_ENABLED=true,DD_SITE=$DD_SITE,LRCP_GCP_PROJECT_ID=$PROJECT_ID,LRCP_GEMINI_API_KEY=$GEMINI_API_KEY,LRCP_DATADOG_API_KEY=$DATADOG_API_KEY,DD_APP_KEY=$DATADOG_APP_KEY" `
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

