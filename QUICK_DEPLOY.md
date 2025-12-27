# 🚀 Quick Deployment Guide - Your Project

This guide uses your actual project ID for the Datadog Challenge submission.

## 📋 Your Configuration

- **Google Cloud Project ID**: `llm-reliability-control`

## 🔑 Still Need These

1. **Gemini API Key** - https://aistudio.google.com/app/apikey
2. **Datadog API Key** - https://app.datadoghq.com/organization-settings/api-keys
3. **Datadog App Key** - https://app.datadoghq.com/organization-settings/application-keys
4. **Datadog Site** - Check your Datadog login URL (datadoghq.com, datadoghq.eu, etc.)

## 🚀 Quick Deployment Steps

### Step 1: Setup Google Cloud Secrets

**Windows (PowerShell):**
```powershell
# Run the setup script
.\scripts\setup_gcp_secrets.ps1

# It will prompt you for:
# - Gemini API Key
# - Datadog API Key
# - Datadog App Key
# - Datadog Site
```

**Linux/macOS:**
```bash
# Make script executable
chmod +x scripts/setup_gcp_secrets.sh

# Run the setup script
./scripts/setup_gcp_secrets.sh

# It will prompt you for:
# - Gemini API Key
# - Datadog API Key
# - Datadog App Key
# - Datadog Site
```

**Manual Setup (if scripts don't work):**
```bash
# Set project
gcloud config set project llm-reliability-control

# Create secrets (replace YOUR_KEYS with actual values)
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
echo -n "YOUR_DATADOG_API_KEY" | gcloud secrets create datadog-api-key --data-file=-
echo -n "YOUR_DATADOG_APP_KEY" | gcloud secrets create datadog-app-key --data-file=-

# Grant permissions
export PROJECT_NUMBER=$(gcloud projects describe llm-reliability-control --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding datadog-api-key \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding datadog-app-key \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Step 2: Deploy to Cloud Run

**Windows (PowerShell):**
```powershell
.\scripts\deploy_to_cloud_run.ps1
```

**Linux/macOS:**
```bash
chmod +x scripts/deploy_to_cloud_run.sh
./scripts/deploy_to_cloud_run.sh
```

**Manual Deployment:**
```bash
# Set project
gcloud config set project llm-reliability-control

# Enable APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com

# Build and deploy
gcloud builds submit --tag gcr.io/llm-reliability-control/llm-reliability-control-plane:latest

gcloud run deploy llm-reliability-control-plane \
  --image gcr.io/llm-reliability-control/llm-reliability-control-plane:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars "DD_SERVICE=llm-reliability-control-plane,DD_ENV=production,DD_VERSION=1.0.0,DD_LLMOBS_AGENTLESS_ENABLED=1,DD_TRACE_ENABLED=true,DD_LOGS_ENABLED=true,DD_SITE=datadoghq.com,LRCP_GCP_PROJECT_ID=llm-reliability-control" \
  --set-secrets "LRCP_GEMINI_API_KEY=gemini-api-key:latest,LRCP_DATADOG_API_KEY=datadog-api-key:latest,DD_APP_KEY=datadog-app-key:latest"

# Get service URL
gcloud run services describe llm-reliability-control-plane --region us-central1 --format 'value(status.url)'
```

### Step 3: Update Workflow URLs

After deployment, get your service URL and update `datadog/workflows.json`:

```bash
# Get service URL
export SERVICE_URL=$(gcloud run services describe llm-reliability-control-plane --region us-central1 --format 'value(status.url)')
echo "Service URL: $SERVICE_URL"

# Update workflows.json
# Replace all {{APP_URL}} with: $SERVICE_URL
```

### Step 4: Import Datadog Resources

Follow `DATADOG_IMPORT_GUIDE.md` to import:
- Monitors
- Dashboard
- SLOs
- Workflows (after updating URLs)
- On-Call (after updating emails/channels)

### Step 5: Test

```bash
# Get service URL
export SERVICE_URL=$(gcloud run services describe llm-reliability-control-plane --region us-central1 --format 'value(status.url)')

# Test health
curl $SERVICE_URL/health

# Test API docs
# Open in browser: $SERVICE_URL/docs

# Test QA endpoint
curl -X POST "$SERVICE_URL/qa" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Datadog?", "document": "Datadog is a monitoring platform."}'

# Test Datadog products list
curl $SERVICE_URL/datadog/products
```

## 📝 Quick Checklist

- [ ] Get Gemini API Key
- [ ] Get Datadog API Key & App Key
- [ ] Run `setup_gcp_secrets.sh` (or `.ps1` on Windows)
- [ ] Run `deploy_to_cloud_run.sh` (or `.ps1` on Windows)
- [ ] Get service URL
- [ ] Update `datadog/workflows.json` with service URL
- [ ] Import Datadog resources
- [ ] Test application

## 🎯 Expected Service URL Format

After deployment, your service URL will be:
```
https://llm-reliability-control-plane-xxxxx-uc.a.run.app
```

Use this URL to:
- Update `datadog/workflows.json` (replace `{{APP_URL}}`)
- Test endpoints
- Share in submission

---

**🚀 Ready to Deploy!** Run the scripts and you'll be live in minutes!

