# Enable Billing for Secret Manager (Optional)

If you want to use Secret Manager (more secure), you need to enable billing first.

## Quick Fix: Use Alternative Deployment (No Billing Required)

**Recommended for hackathon:** Use the alternative deployment script that doesn't require Secret Manager:

```powershell
.\scripts\deploy_without_secrets.ps1
```

This uses environment variables directly (still secure for Cloud Run, just not using Secret Manager).

## Enable Billing (If You Want Secret Manager)

If you prefer to use Secret Manager:

### Step 1: Enable Billing

1. Go to: https://console.cloud.google.com/billing
2. Select your project: `llm-reliability-control`
3. Click **Link a billing account**
4. Create a new billing account or link an existing one
5. Google provides $300 free credit for new accounts

### Step 2: Enable Secret Manager API

After billing is enabled, run:

```powershell
gcloud services enable secretmanager.googleapis.com --project=llm-reliability-control
```

Or visit: https://console.developers.google.com/apis/api/secretmanager.googleapis.com/overview?project=llm-reliability-control

### Step 3: Run Setup Script

```powershell
.\scripts\setup_secrets_with_credentials.ps1
```

## Recommendation

For the hackathon, **use the alternative deployment** (`deploy_without_secrets.ps1`) - it's faster and doesn't require billing setup. Environment variables in Cloud Run are still secure and sufficient for this use case.

