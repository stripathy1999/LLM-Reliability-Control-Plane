# ✅ Fixed: gcloud Command Not Found

## Problem
The `gcloud` command wasn't recognized because it wasn't in your PATH.

## Solution
Google Cloud SDK is installed at: `$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin`

## Quick Fix (Current Session)

Run this in PowerShell to add gcloud to PATH for the current session:

```powershell
$env:PATH += ";$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"
```

Then test:
```powershell
gcloud --version
```

## Permanent Fix

Run this script to add gcloud to PATH permanently:

```powershell
cd "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
.\scripts\setup_gcloud_path.ps1
```

**Note:** You'll need to restart your terminal after running this for the permanent PATH change to take effect.

## Quick Setup (All-in-One)

Run this script to:
1. Add gcloud to PATH
2. Set project to `llm-reliability-control`
3. Authenticate with Google Cloud

```powershell
cd "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
$env:PATH += ";$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"
.\scripts\quick_setup.ps1
```

## Manual Steps

If scripts don't work, run these commands manually:

```powershell
# 1. Add to PATH for current session
$env:PATH += ";$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"

# 2. Verify it works
gcloud --version

# 3. Set project
gcloud config set project llm-reliability-control

# 4. Authenticate (will open browser)
gcloud auth login
```

## After Authentication

Once authenticated, you can proceed with deployment:

```powershell
# 1. Setup secrets
.\scripts\setup_secrets_with_credentials.ps1

# 2. Deploy
.\scripts\deploy_to_cloud_run_with_credentials.ps1
```

---

**✅ gcloud is now working!** You can use all gcloud commands.

