# 🚀 Complete Setup Guide - Your Project

This guide uses your actual project ID for the Datadog Challenge submission.

## ✅ Your Configuration

- **Google Cloud Project ID**: `llm-reliability-control`

## 🔑 Required API Keys (Get These First)

### 1. Gemini API Key
- **URL**: https://aistudio.google.com/app/apikey
- **Steps**:
  1. Sign in with Google account
  2. Click "Create API Key"
  3. Copy the key (save it!)

### 2. Datadog API Key
- **URL**: https://app.datadoghq.com/organization-settings/api-keys
- **Steps**:
  1. Sign up for free trial (14 days) or use existing account
  2. Go to: Organization Settings → API Keys
  3. Click "New Key"
  4. Name: `LLM-Reliability-Control-Plane`
  5. Copy the key

### 3. Datadog Application Key
- **URL**: https://app.datadoghq.com/organization-settings/application-keys
- **Steps**:
  1. Go to: Organization Settings → Application Keys
  2. Click "New Key"
  3. Name: `LLM-Reliability-Control-Plane`
  4. Copy the key

### 4. Datadog Site
- **How to find**: Check your Datadog login URL
- **Common values**: `datadoghq.com`, `datadoghq.eu`, `us3.datadoghq.com`
- **Example**: If you login at `https://app.datadoghq.com`, your site is `datadoghq.com`

---

## 🚀 Complete Deployment Steps

### **Step 1: Install Google Cloud SDK**

**Windows:**
- Download: https://cloud.google.com/sdk/docs/install
- Install and restart terminal

**macOS:**
```bash
brew install --cask google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### **Step 2: Authenticate with Google Cloud**

```bash
# Login
gcloud auth login

# Set your project
gcloud config set project llm-reliability-control

# Verify
gcloud config get-value project
# Should output: llm-reliability-control
```

### **Step 3: Setup Google Cloud Secrets**

**Windows PowerShell:**
```powershell
cd LLM-Reliability-Control-Plane
.\scripts\setup_gcp_secrets.ps1
```

The script will:
- ✅ Use your Datadog credentials automatically
- ✅ Prompt you for: Gemini API Key, Datadog API Key, Datadog App Key, Datadog Site
- ✅ Create all secrets in Secret Manager
- ✅ Grant Cloud Run access to secrets

**Linux/macOS:**
```bash
cd LLM-Reliability-Control-Plane
chmod +x scripts/setup_gcp_secrets.sh
./scripts/setup_gcp_secrets.sh
```

**Manual Setup (if scripts don't work):**
```bash
# Set project
gcloud config set project llm-reliability-control

# Enable Secret Manager
gcloud services enable secretmanager.googleapis.com

# Get project number
export PROJECT_NUMBER=$(gcloud projects describe llm-reliability-control --format="value(projectNumber)")

# Create secrets (replace YOUR_KEYS with actual values)
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
echo -n "YOUR_DATADOG_API_KEY" | gcloud secrets create datadog-api-key --data-file=-
echo -n "YOUR_DATADOG_APP_KEY" | gcloud secrets create datadog-app-key --data-file=-

# Grant Cloud Run access
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

### **Step 4: Deploy to Cloud Run**

**Windows PowerShell:**
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

# Enable required APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com

# Build Docker image
gcloud builds submit --tag gcr.io/llm-reliability-control/llm-reliability-control-plane:latest

# Deploy to Cloud Run
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

### **Step 5: Get Service URL and Update Configuration**

```bash
# Get your service URL
export SERVICE_URL=$(gcloud run services describe llm-reliability-control-plane --region us-central1 --format 'value(status.url)')
echo "Your Service URL: $SERVICE_URL"

# Save this URL - you'll need it!
```

**Update `datadog/workflows.json`:**
1. Open `datadog/workflows.json`
2. Find all instances of `{{APP_URL}}`
3. Replace with your actual service URL
4. Example: `"url": "{{APP_URL}}/api/configure/model"`
5. Becomes: `"url": "https://llm-reliability-control-plane-xxxxx-uc.a.run.app/api/configure/model"`

### **Step 6: Import Datadog Resources**

See `DATADOG_IMPORT_GUIDE.md` for detailed steps.

**Quick Summary:**
1. Set environment variables:
   ```bash
   export DD_API_KEY="your-datadog-api-key"
   export DD_APP_KEY="your-datadog-app-key"
   export DD_SITE="datadoghq.com"
   ```

2. Import Monitors:
   - Go to: Datadog → Monitors → New Monitor → Import from JSON
   - Import: `datadog/monitors.json`
   - Import: `datadog/monitors_anomaly.json`
   - Import: `datadog/monitors_advanced.json`

3. Import Dashboard:
   - Go to: Datadog → Dashboards → New Dashboard → Import Dashboard JSON
   - Import: `datadog/dashboard.json`

4. Import SLO:
   - Go to: Datadog → Service Management → SLOs → New SLO
   - Use `datadog/slo.json` as reference

5. Configure Workflows:
   - Go to: Datadog → Workflow Automation → Workflows
   - Create workflows using `datadog/workflows.json` (after updating URLs)

6. Configure On-Call:
   - Update `datadog/oncall.json` with real emails/channels
   - Go to: Datadog → On-Call → Settings
   - Create escalation policies and schedules

### **Step 7: Test Everything**

```bash
# Get service URL
export SERVICE_URL=$(gcloud run services describe llm-reliability-control-plane --region us-central1 --format 'value(status.url)')

# Test health
curl $SERVICE_URL/health

# Test API docs (open in browser)
# $SERVICE_URL/docs

# Test QA endpoint
curl -X POST "$SERVICE_URL/qa" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Datadog?", "document": "Datadog is a monitoring platform."}'

# Test Datadog products
curl $SERVICE_URL/datadog/products

# Test insights
curl -X POST "$SERVICE_URL/insights" \
  -H "Content-Type: application/json" \
  -d '{"avg_latency_ms": 1200, "error_rate": 0.02, "avg_cost_per_request": 0.008}'
```

### **Step 8: Verify Datadog Integration**

1. **APM**: Datadog → APM → Services → Look for `llm-reliability-control-plane`
2. **Metrics**: Datadog → Metrics Explorer → Search `llm.*`
3. **Logs**: Datadog → Logs → Filter `service:llm-reliability-control-plane`
4. **Dashboard**: Open your imported dashboard
5. **Monitors**: Datadog → Monitors → Verify evaluating

---

## 📋 Complete Checklist

### Pre-Deployment
- [ ] Gemini API key obtained
- [ ] Datadog API key obtained
- [ ] Datadog App key obtained
- [ ] Datadog site identified
- [ ] Google Cloud SDK installed
- [ ] Authenticated with Google Cloud (`gcloud auth login`)
- [ ] Project set (`gcloud config set project llm-reliability-control`)

### Deployment
- [ ] Secrets created (run `setup_gcp_secrets.sh` or `.ps1`)
- [ ] APIs enabled
- [ ] Docker image built
- [ ] Deployed to Cloud Run (run `deploy_to_cloud_run.sh` or `.ps1`)
- [ ] Service URL obtained

### Configuration
- [ ] `datadog/workflows.json` updated with service URL
- [ ] `datadog/oncall.json` updated with real emails/channels
- [ ] Datadog monitors imported
- [ ] Datadog dashboard imported
- [ ] Datadog SLO imported

### Verification
- [ ] Application responds (`/health` endpoint)
- [ ] Datadog receives traces (APM → Services)
- [ ] Datadog receives metrics (Metrics Explorer)
- [ ] Datadog receives logs (Logs)
- [ ] Dashboard shows data
- [ ] Monitors are evaluating

---

## 🎯 Expected Service URL

After deployment, your service URL will be:
```
https://llm-reliability-control-plane-xxxxx-uc.a.run.app
```

Use this URL to:
- Update `datadog/workflows.json`
- Test endpoints
- Share in submission

---

## 🔗 All API Endpoints You'll Have

After deployment, your application will expose:

### Core Endpoints
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger UI)
- `POST /qa` - Question & Answer
- `POST /reason` - Reasoning endpoint
- `POST /stress` - Stress testing
- `POST /insights` - AI-powered insights

### Datadog Integration Endpoints
- `GET /datadog/products` - List all 19 integrated products
- `POST /datadog/synthetics/*` - Synthetics management
- `POST /datadog/notebooks/*` - Notebook creation
- `POST /datadog/workflows/*` - Workflow automation
- `POST /datadog/oncall/*` - On-Call paging
- `GET /datadog/log-pipelines` - List log pipelines
- `POST /datadog/service-map/*` - Service Map tracking
- `POST /datadog/ci/*` - CI Visibility tracking

### Optimization Endpoints
- `GET /optimization/roi-report` - ROI report
- `POST /optimization/anomaly/attribute` - Anomaly attribution

### Optimization Endpoints
- `POST /optimization/recommendations` - Cost optimization recommendations
- `POST /optimization/roi-report` - ROI calculation report
- `POST /optimization/attribute-anomaly` - Anomaly attribution analysis

---

## 🐛 Troubleshooting

### "Service won't start"
```bash
# Check logs
gcloud run services logs read llm-reliability-control-plane --region us-central1 --limit 100

# Verify secrets exist
gcloud secrets list
```

### "Datadog not receiving data"
```bash
# Check environment variables
gcloud run services describe llm-reliability-control-plane --region us-central1 --format="value(spec.template.spec.containers[0].env)"

# Verify:
# - DD_LLMOBS_AGENTLESS_ENABLED=1
# - DD_API_KEY is set (from secret)
# - DD_SITE matches your Datadog organization
```

### "Secrets not accessible"
```bash
# List secrets
gcloud secrets list

# Check permissions
gcloud secrets get-iam-policy gemini-api-key
```

---

## 📝 Summary: What You Need

### Required (4 items)
1. ✅ Gemini API Key
2. ✅ Datadog API Key
3. ✅ Datadog App Key
4. ✅ Datadog Site

### Already Have (4 items)
- ✅ Google Cloud Project ID: `llm-reliability-control`

---

**🚀 Ready to Deploy!** Get the 4 required API keys, then run the setup scripts!

