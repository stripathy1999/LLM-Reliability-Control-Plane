# PowerShell script to setup Google Cloud Secrets with your actual credentials
# Run this after installing Google Cloud SDK

$PROJECT_ID = "llm-reliability-control"
$REGION = "us-central1"

# Your credentials
$GEMINI_API_KEY = "AIzaSyBjZGBe204-N215wVOyh8K6ksGbKAi8JNc"
$DATADOG_API_KEY = "e38221fb258a4ea3ec8bd312db36fa6e"
$DATADOG_APP_KEY = "ef51694759c084b54ecd2ced19579924c9eb968c"
$DD_SITE = "us5.datadoghq.com"

# Confluent credentials
$CONFLUENT_BOOTSTRAP = "pkc-619z3.us-east1.gcp.confluent.cloud:9092"
$CONFLUENT_API_KEY = "53CGSDMC2E7HOPN3"
$CONFLUENT_API_SECRET = "cfltC5QSsc7nWwn7nA1v68Q8kdsBBVbst2n89xtQ2S3Srzf7r761vZjOStlyBqDg"

Write-Host "Setting up Google Cloud Secrets for project: $PROJECT_ID" -ForegroundColor Green

# Set project
gcloud config set project $PROJECT_ID

# Enable Secret Manager API
Write-Host "Enabling Secret Manager API..." -ForegroundColor Yellow
gcloud services enable secretmanager.googleapis.com

# Get project number
$PROJECT_NUMBER = (gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
Write-Host "Project Number: $PROJECT_NUMBER" -ForegroundColor Cyan

Write-Host ""
Write-Host "Creating secrets in Secret Manager..." -ForegroundColor Yellow

# Create secrets (create or update)
$GEMINI_API_KEY | gcloud secrets create gemini-api-key --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Updating gemini-api-key..." -ForegroundColor Gray
    $GEMINI_API_KEY | gcloud secrets versions add gemini-api-key --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "  Created gemini-api-key" -ForegroundColor Green
}

$DATADOG_API_KEY | gcloud secrets create datadog-api-key --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Updating datadog-api-key..." -ForegroundColor Gray
    $DATADOG_API_KEY | gcloud secrets versions add datadog-api-key --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "  Created datadog-api-key" -ForegroundColor Green
}

$DATADOG_APP_KEY | gcloud secrets create datadog-app-key --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Updating datadog-app-key..." -ForegroundColor Gray
    $DATADOG_APP_KEY | gcloud secrets versions add datadog-app-key --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "  Created datadog-app-key" -ForegroundColor Green
}

$CONFLUENT_BOOTSTRAP | gcloud secrets create confluent-bootstrap --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Updating confluent-bootstrap..." -ForegroundColor Gray
    $CONFLUENT_BOOTSTRAP | gcloud secrets versions add confluent-bootstrap --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "  Created confluent-bootstrap" -ForegroundColor Green
}

$CONFLUENT_API_KEY | gcloud secrets create confluent-api-key --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Updating confluent-api-key..." -ForegroundColor Gray
    $CONFLUENT_API_KEY | gcloud secrets versions add confluent-api-key --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "  Created confluent-api-key" -ForegroundColor Green
}

$CONFLUENT_API_SECRET | gcloud secrets create confluent-api-secret --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Updating confluent-api-secret..." -ForegroundColor Gray
    $CONFLUENT_API_SECRET | gcloud secrets versions add confluent-api-secret --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "  Created confluent-api-secret" -ForegroundColor Green
}

$PROJECT_ID | gcloud secrets create gcp-project-id --data-file=- --project=$PROJECT_ID 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Updating gcp-project-id..." -ForegroundColor Gray
    $PROJECT_ID | gcloud secrets versions add gcp-project-id --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "  Created gcp-project-id" -ForegroundColor Green
}

Write-Host ""
Write-Host "Granting Cloud Run service account access to secrets..." -ForegroundColor Yellow

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
Write-Host "Secrets created and permissions granted!" -ForegroundColor Green
Write-Host ""
Write-Host "Created secrets:" -ForegroundColor Cyan
Write-Host "  - gemini-api-key"
Write-Host "  - datadog-api-key"
Write-Host "  - datadog-app-key"
Write-Host "  - confluent-bootstrap"
Write-Host "  - confluent-api-key"
Write-Host "  - confluent-api-secret"
Write-Host "  - gcp-project-id"
Write-Host ""
Write-Host "Next step: Run deploy_to_cloud_run_with_credentials.ps1" -ForegroundColor Yellow
