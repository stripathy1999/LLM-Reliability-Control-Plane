# Quick Start Script for LLM Reliability Control Plane
# This script starts the server with the API key configured

Write-Host "🚀 Starting LLM Reliability Control Plane Server..." -ForegroundColor Green
Write-Host ""

# Navigate to project directory
$projectDir = "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
Set-Location $projectDir

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Set API key
$env:LRCP_GEMINI_API_KEY = "AIzaSyCGMd-wESGb3PUKG_fOF2E2tSTmax40ke8"
$env:GEMINI_API_KEY = "AIzaSyCGMd-wESGb3PUKG_fOF2E2tSTmax40ke8"

Write-Host "✅ API key configured" -ForegroundColor Green
Write-Host ""
Write-Host "Starting server on http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Swagger UI will be available at: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "📖 ReDoc will be available at: http://127.0.0.1:8000/redoc" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

