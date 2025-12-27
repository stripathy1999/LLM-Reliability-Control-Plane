# Test Runner Script for LLM Reliability Control Plane
# Run this after starting the server

Write-Host "🧪 Running End-to-End Tests..." -ForegroundColor Green
Write-Host ""

# Navigate to project directory
$projectDir = "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
Set-Location $projectDir

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Set API key and encoding
$env:LRCP_GEMINI_API_KEY = "AIzaSyCGMd-wESGb3PUKG_fOF2E2tSTmax40ke8"
$env:GEMINI_API_KEY = "AIzaSyCGMd-wESGb3PUKG_fOF2E2tSTmax40ke8"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "✅ API key configured" -ForegroundColor Green
Write-Host ""

# Check if server is running
Write-Host "Checking if server is running..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Server is running!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Server is not running!" -ForegroundColor Red
    Write-Host "Please start the server first using START_SERVER.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Run tests
Write-Host "Running test suite..." -ForegroundColor Cyan
Write-Host ""
python test_end_to_end.py

Write-Host ""
Write-Host "✅ Tests completed!" -ForegroundColor Green



