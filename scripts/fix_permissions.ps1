# Fix IAM permissions for Cloud Build and deployment
# Run this to grant necessary permissions

$PROJECT_ID = "llm-reliability-control"
$USER_EMAIL = "sakshisanskruti.tripathy@sjsu.edu"

Write-Host "Fixing IAM permissions for project: $PROJECT_ID" -ForegroundColor Green
Write-Host "User: $USER_EMAIL"
Write-Host ""

# Grant necessary roles
Write-Host "Granting Cloud Build Editor role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="user:$USER_EMAIL" `
    --role="roles/cloudbuild.builds.editor"

Write-Host "Granting Service Account User role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="user:$USER_EMAIL" `
    --role="roles/iam.serviceAccountUser"

Write-Host "Granting Cloud Run Admin role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="user:$USER_EMAIL" `
    --role="roles/run.admin"

Write-Host "Granting Storage Admin role (for Cloud Build)..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="user:$USER_EMAIL" `
    --role="roles/storage.admin"

Write-Host ""
Write-Host "Permissions granted! Wait a few seconds for propagation, then try deployment again." -ForegroundColor Green

