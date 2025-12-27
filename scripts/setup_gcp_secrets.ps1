# PowerShell script to setup Google Cloud Secrets
# This script creates all required secrets in Google Secret Manager

$PROJECT_ID = "llm-reliability-control"
$REGION = "us-central1"

Write-Host "🚀 Setting up Google Cloud Secrets for project: $PROJECT_ID" -ForegroundColor Green

# Set project
gcloud config set project $PROJECT_ID

# Enable Secret Manager API
Write-Host "📦 Enabling Secret Manager API..." -ForegroundColor Yellow
gcloud services enable secretmanager.googleapis.com

# Get project number
$PROJECT_NUMBER = (gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
Write-Host "📊 Project Number: $PROJECT_NUMBER" -ForegroundColor Cyan

# Prompt for credentials
Write-Host ""
Write-Host "Please provide the following credentials:" -ForegroundColor Yellow
Write-Host ""

$GEMINI_API_KEY = Read-Host "Gemini API Key"
$DATADOG_API_KEY = Read-Host "Datadog API Key"
$DATADOG_APP_KEY = Read-Host "Datadog App Key"
$DD_SITE = Read-Host "Datadog Site (datadoghq.com, datadoghq.eu, etc.)"

# Confluent credentials (already provided)
$CONFLUENT_BOOTSTRAP = "pkc-619z3.us-east1.gcp.confluent.cloud:9092"
$CONFLUENT_API_KEY = "53CGSDMC2E7HOPN3"
$CONFLUENT_API_SECRET = "cfltC5QSsc7nWwn7nA1v68Q8kdsBBVbst2n89xtQ2S3Srzf7r761vZjOStlyBqDg"

Write-Host ""
Write-Host "🔐 Creating secrets in Secret Manager..." -ForegroundColor Yellow

# Create secrets (create or update)
$GEMINI_API_KEY | gcloud secrets create gemini-api-key --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    $GEMINI_API_KEY | gcloud secrets versions add gemini-api-key --data-file=- --project=$PROJECT_ID
}

$DATADOG_API_KEY | gcloud secrets create datadog-api-key --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    $DATADOG_API_KEY | gcloud secrets versions add datadog-api-key --data-file=- --project=$PROJECT_ID
}

$DATADOG_APP_KEY | gcloud secrets create datadog-app-key --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    $DATADOG_APP_KEY | gcloud secrets versions add datadog-app-key --data-file=- --project=$PROJECT_ID
}

$CONFLUENT_BOOTSTRAP | gcloud secrets create confluent-bootstrap --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    $CONFLUENT_BOOTSTRAP | gcloud secrets versions add confluent-bootstrap --data-file=- --project=$PROJECT_ID
}

$CONFLUENT_API_KEY | gcloud secrets create confluent-api-key --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    $CONFLUENT_API_KEY | gcloud secrets versions add confluent-api-key --data-file=- --project=$PROJECT_ID
}

$CONFLUENT_API_SECRET | gcloud secrets create confluent-api-secret --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    $CONFLUENT_API_SECRET | gcloud secrets versions add confluent-api-secret --data-file=- --project=$PROJECT_ID
}

$PROJECT_ID | gcloud secrets create gcp-project-id --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    $PROJECT_ID | gcloud secrets versions add gcp-project-id --data-file=- --project=$PROJECT_ID
}

Write-Host ""
Write-Host "🔑 Granting Cloud Run service account access to secrets..." -ForegroundColor Yellow

# Grant Cloud Run service account access
gcloud secrets add-iam-policy-binding gemini-api-key `
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding datadog-api-key `
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding datadog-app-key `
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding confluent-bootstrap `
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding confluent-api-key `
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding confluent-api-secret `
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding gcp-project-id `
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

Write-Host ""
Write-Host "✅ Secrets created and permissions granted!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Created secrets:" -ForegroundColor Cyan
Write-Host "  - gemini-api-key"
Write-Host "  - datadog-api-key"
Write-Host "  - datadog-app-key"
Write-Host "  - confluent-bootstrap"
Write-Host "  - confluent-api-key"
Write-Host "  - confluent-api-secret"
Write-Host "  - gcp-project-id"
Write-Host ""
Write-Host "🚀 Next step: Run deployment script or deploy manually" -ForegroundColor Yellow

