# 🚀 Deploy Now - Ready to Execute

All your credentials are configured! Just follow these steps.

## ✅ Your Credentials (Already Configured)

- ✅ **Google Cloud Project ID**: `llm-reliability-control`
- ✅ **Gemini API Key**: Configured
- ✅ **Datadog API Key**: `e38221fb258a4ea3ec8bd312db36fa6e`
- ✅ **Datadog App Key**: `ef51694759c084b54ecd2ced19579924c9eb968c`
- ✅ **Datadog Site**: `us5.datadoghq.com`

## 📋 Prerequisites

1. **Install Google Cloud SDK** (if not installed):
   - Download: https://cloud.google.com/sdk/docs/install
   - Or use: `winget install Google.CloudSDK` (Windows)
   - Restart terminal after installation

2. **Authenticate with Google Cloud**:
   ```powershell
   gcloud auth login
   ```

## 🚀 Quick Deployment (2 Steps)

### **Step 1: Setup Secrets**

```powershell
cd LLM-Reliability-Control-Plane
.\scripts\setup_secrets_with_credentials.ps1
```

This script will:
- ✅ Create all secrets in Google Secret Manager
- ✅ Grant Cloud Run access to secrets
- ✅ Use all your provided credentials

### **Step 2: Deploy to Cloud Run**

```powershell
.\scripts\deploy_to_cloud_run_with_credentials.ps1
```

This script will:
- ✅ Enable required APIs
- ✅ Build Docker image
- ✅ Deploy to Cloud Run
- ✅ Show you the service URL

## 📝 After Deployment

### 1. Get Your Service URL

The deployment script will show your service URL. It will look like:
```
https://llm-reliability-control-plane-xxxxx-uc.a.run.app
```

### 2. Update Workflows JSON

Open `datadog/workflows.json` and replace all instances of `{{APP_URL}}` with your service URL.

**Find and replace:**
- `{{APP_URL}}` → `https://llm-reliability-control-plane-xxxxx-uc.a.run.app`

There are 7 instances to replace.

### 3. Import Datadog Resources

See `DATADOG_IMPORT_GUIDE.md` for detailed steps.

**Quick commands:**
```powershell
# Set environment variables
$env:DD_API_KEY = "e38221fb258a4ea3ec8bd312db36fa6e"
$env:DD_APP_KEY = "ef51694759c084b54ecd2ced19579924c9eb968c"
$env:DD_SITE = "us5.datadoghq.com"

# Then import:
# 1. Monitors: Datadog UI → Monitors → New Monitor → Import from JSON
#    - Import datadog/monitors.json
#    - Import datadog/monitors_anomaly.json
#    - Import datadog/monitors_advanced.json
# 2. Dashboard: Datadog UI → Dashboards → New Dashboard → Import Dashboard JSON
#    - Import datadog/dashboard.json
# 3. SLO: Datadog UI → Service Management → SLOs → New SLO
#    - Use datadog/slo.json as reference
```

### 4. Test Your Application

```powershell
# Get service URL (if you didn't save it)
$SERVICE_URL = (gcloud run services describe llm-reliability-control-plane --region us-central1 --format 'value(status.url)')

# Test health
curl $SERVICE_URL/health

# Test API docs (open in browser)
# $SERVICE_URL/docs

# Test QA endpoint
curl -X POST "$SERVICE_URL/qa" `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"What is Datadog?\", \"document\": \"Datadog is a monitoring platform.\"}'

# Test Datadog products
curl $SERVICE_URL/datadog/products
```

## ✅ Verification Checklist

- [ ] Secrets created successfully
- [ ] Deployment completed
- [ ] Service URL obtained
- [ ] `datadog/workflows.json` updated with service URL
- [ ] Datadog monitors imported
- [ ] Datadog dashboard imported
- [ ] Application responds to requests
- [ ] Datadog receiving traces/metrics/logs

## 🎯 Expected Results

After deployment:
- ✅ Service URL: `https://llm-reliability-control-plane-xxxxx-uc.a.run.app`
- ✅ All endpoints working
- ✅ Datadog integration active (site: us5.datadoghq.com)
- ✅ 19 Datadog products integrated

## 🐛 Troubleshooting

### "gcloud not found"
- Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
- Restart terminal after installation

### "Permission denied"
- Run: `gcloud auth login`
- Verify project: `gcloud config get-value project`

### "Secret already exists"
- This is normal if you run the script multiple times
- The script will update existing secrets

### "Service won't start"
- Check logs: `gcloud run services logs read llm-reliability-control-plane --region us-central1 --limit 100`
- Verify secrets exist: `gcloud secrets list`

---

**🚀 Ready!** Install gcloud, authenticate, then run the two scripts!

