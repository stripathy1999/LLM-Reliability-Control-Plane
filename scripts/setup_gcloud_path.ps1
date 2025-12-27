# Add Google Cloud SDK to PATH permanently
# Run this script once to add gcloud to your PATH

$gcloudPath = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"

if (Test-Path $gcloudPath) {
    Write-Host "✅ Found Google Cloud SDK at: $gcloudPath" -ForegroundColor Green
    
    # Add to PATH for current session
    $env:PATH += ";$gcloudPath"
    Write-Host "✅ Added to PATH for current session" -ForegroundColor Green
    
    # Add to PATH permanently (User PATH)
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$gcloudPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$gcloudPath", "User")
        Write-Host "✅ Added to PATH permanently (User PATH)" -ForegroundColor Green
        Write-Host "⚠️  Please restart your terminal for permanent PATH changes to take effect" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Already in permanent PATH" -ForegroundColor Green
    }
    
    # Test gcloud
    Write-Host ""
    Write-Host "Testing gcloud..." -ForegroundColor Yellow
    & "$gcloudPath\gcloud.cmd" --version
    
    Write-Host ""
    Write-Host "✅ Setup complete! You can now use 'gcloud' commands." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Authenticate: gcloud auth login" -ForegroundColor White
    Write-Host "  2. Set project: gcloud config set project llm-reliability-control" -ForegroundColor White
    Write-Host "  3. Run setup script: .\scripts\setup_secrets_with_credentials.ps1" -ForegroundColor White
} else {
    Write-Host "❌ Google Cloud SDK not found at: $gcloudPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Google Cloud SDK:" -ForegroundColor Yellow
    Write-Host "  Download: https://cloud.google.com/sdk/docs/install" -ForegroundColor White
    Write-Host "  Or run: winget install Google.CloudSDK" -ForegroundColor White
}

