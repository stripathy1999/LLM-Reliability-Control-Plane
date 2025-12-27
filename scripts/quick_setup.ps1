# Quick setup script - Adds gcloud to PATH and authenticates
# Run this first before deploying

Write-Host "🚀 Quick Setup for Google Cloud SDK" -ForegroundColor Green
Write-Host ""

# Add gcloud to PATH
$gcloudPath = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"

if (Test-Path $gcloudPath) {
    Write-Host "✅ Found Google Cloud SDK" -ForegroundColor Green
    $env:PATH += ";$gcloudPath"
} else {
    Write-Host "❌ Google Cloud SDK not found!" -ForegroundColor Red
    Write-Host "Please install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Verify gcloud works
Write-Host ""
Write-Host "Checking gcloud version..." -ForegroundColor Yellow
& "$gcloudPath\gcloud.cmd" --version

# Set project
Write-Host ""
Write-Host "Setting project to: llm-reliability-control" -ForegroundColor Yellow
& "$gcloudPath\gcloud.cmd" config set project llm-reliability-control

# Authenticate
Write-Host ""
Write-Host "🔐 Authenticating with Google Cloud..." -ForegroundColor Yellow
Write-Host "A browser window will open. Please sign in and authorize." -ForegroundColor Cyan
Write-Host ""

& "$gcloudPath\gcloud.cmd" auth login

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Authentication successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run: .\scripts\setup_secrets_with_credentials.ps1" -ForegroundColor White
    Write-Host "  2. Run: .\scripts\deploy_to_cloud_run_with_credentials.ps1" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "⚠️  Authentication failed. Try running manually:" -ForegroundColor Yellow
    Write-Host "  gcloud auth login" -ForegroundColor White
    Write-Host ""
}

