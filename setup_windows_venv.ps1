# PowerShell script to set up virtual environment with standard Windows Python
# This avoids the MSYS Python compatibility issues with grpcio

Write-Host "Setting up virtual environment with standard Windows Python..." -ForegroundColor Green

# Find standard Windows Python (not MSYS)
$pythonPaths = @(
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python313\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Python313\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe"
)

$pythonExe = $null
foreach ($path in $pythonPaths) {
    if (Test-Path $path) {
        $pythonExe = $path
        Write-Host "Found Python at: $pythonExe" -ForegroundColor Green
        break
    }
}

if (-not $pythonExe) {
    Write-Host "ERROR: Could not find standard Windows Python installation." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Remove old venv if it exists
if (Test-Path "venv") {
    Write-Host "Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

# Create new venv
Write-Host "Creating new virtual environment..." -ForegroundColor Green
& $pythonExe -m venv venv

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
python -m pip install -r requirements.txt

Write-Host "`nSetup complete! Next steps:" -ForegroundColor Green
Write-Host "1. Set your Gemini API key: `$env:GEMINI_API_KEY = 'your-key-here'" -ForegroundColor Cyan
Write-Host "2. Start the server: uvicorn app.main:app --reload" -ForegroundColor Cyan
Write-Host "3. Run tests: python test_end_to_end.py" -ForegroundColor Cyan

