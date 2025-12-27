# 🚀 Your Deployment Steps - Ready to Execute

This guide uses your actual credentials and project ID.

## ✅ What You Already Have

- ✅ **Google Cloud Project ID**: `llm-reliability-control`

## 🔑 What You Still Need

1. **Gemini API Key**
   - Go to: https://aistudio.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key

2. **Datadog API Key**
   - Go to: https://app.datadoghq.com/organization-settings/api-keys
   - Click "New Key"
   - Name: `LLM-Reliability-Control-Plane`
   - Copy the key

3. **Datadog Application Key**
   - Go to: https://app.datadoghq.com/organization-settings/application-keys
   - Click "New Key"
   - Name: `LLM-Reliability-Control-Plane`
   - Copy the key

4. **Datadog Site**
   - Check your Datadog login URL
   - Common: `datadoghq.com`, `datadoghq.eu`, `us3.datadoghq.com`

---

## 🚀 Step-by-Step Deployment

### **Step 1: Install Google Cloud SDK** (if not installed)

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

### **Step 3: Setup Secrets** (Choose one method)

#### **Option A: Use Setup Script** (Recommended)

**Windows PowerShell:**
```powershell
cd LLM-Reliability-Control-Plane
.\scripts\setup_gcp_secrets.ps1
# Script will prompt for: Gemini API Key, Datadog API Key, Datadog App Key, Datadog Site
```

**Linux/macOS:**
```bash
cd LLM-Reliability-Control-Plane
chmod +x scripts/setup_gcp_secrets.sh
./scripts/setup_gcp_secrets.sh
# Script will prompt for: Gemini API Key, Datadog API Key, Datadog App Key, Datadog Site
```

#### **Option B: Manual Setup**

```bash
# Set project
gcloud config set project llm-reliability-control

# Enable Secret Manager
gcloud services enable secretmanager.googleapis.com

# Create secrets (replace YOUR_KEYS with actual values)
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
echo -n "YOUR_DATADOG_API_KEY" | gcloud secrets create datadog-api-key --data-file=-
echo -n "YOUR_DATADOG_APP_KEY" | gcloud secrets create datadog-app-key --data-file=-

# Grant Cloud Run access
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

### **Step 4: Deploy to Cloud Run**

#### **Option A: Use Deployment Script** (Recommended)

**Windows PowerShell:**
```powershell
.\scripts\deploy_to_cloud_run.ps1
```

**Linux/macOS:**
```bash
chmod +x scripts/deploy_to_cloud_run.sh
./scripts/deploy_to_cloud_run.sh
```

#### **Option B: Manual Deployment**

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

### **Step 5: Get Service URL and Update Workflows**

```bash
# Get your service URL
export SERVICE_URL=$(gcloud run services describe llm-reliability-control-plane --region us-central1 --format 'value(status.url)')
echo "Your Service URL: $SERVICE_URL"

# Example output:
# https://llm-reliability-control-plane-xxxxx-uc.a.run.app
```

**Update `datadog/workflows.json`:**
- Open `datadog/workflows.json`
- Find all instances of `{{APP_URL}}`
- Replace with your actual service URL
- Example: `"url": "{{APP_URL}}/api/configure/model"` 
- Becomes: `"url": "https://llm-reliability-control-plane-xxxxx-uc.a.run.app/api/configure/model"`

### **Step 6: Import Datadog Resources**

See `DATADOG_IMPORT_GUIDE.md` for detailed steps. Quick summary:

1. **Set environment variables:**
```bash
export DD_API_KEY="your-datadog-api-key"
export DD_APP_KEY="your-datadog-app-key"
export DD_SITE="datadoghq.com"  # or your site
```

2. **Import Monitors:**
   - Go to: Datadog → Monitors → New Monitor → Import from JSON
   - Import: `datadog/monitors.json`
   - Import: `datadog/monitors_anomaly.json`
   - Import: `datadog/monitors_advanced.json`

3. **Import Dashboard:**
   - Go to: Datadog → Dashboards → New Dashboard → Import Dashboard JSON
   - Import: `datadog/dashboard.json`

4. **Import SLO:**
   - Go to: Datadog → Service Management → SLOs → New SLO
   - Use `datadog/slo.json` as reference

5. **Configure Workflows:**
   - Go to: Datadog → Workflow Automation → Workflows
   - Create workflows using `datadog/workflows.json` (after updating URLs)

6. **Configure On-Call:**
   - Go to: Datadog → On-Call → Settings
   - Update `datadog/oncall.json` with real emails/channels first
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

1. **Check APM:**
   - Go to: Datadog → APM → Services
   - Look for: `llm-reliability-control-plane`
   - Verify traces are appearing

2. **Check Metrics:**
   - Go to: Datadog → Metrics Explorer
   - Search: `llm.*`
   - Verify metrics are appearing

3. **Check Logs:**
   - Go to: Datadog → Logs
   - Filter: `service:llm-reliability-control-plane`
   - Verify logs are appearing

4. **Check Dashboard:**
   - Open your imported dashboard
   - Verify widgets show data

5. **Check Monitors:**
   - Go to: Datadog → Monitors
   - Verify monitors are evaluating

---

## 📋 Complete Checklist

### Pre-Deployment
- [ ] Gemini API key obtained
- [ ] Datadog API key obtained
- [ ] Datadog App key obtained
- [ ] Datadog site identified
- [ ] Google Cloud SDK installed
- [ ] Authenticated with Google Cloud

### Deployment
- [ ] Secrets created in Secret Manager
- [ ] APIs enabled
- [ ] Docker image built
- [ ] Deployed to Cloud Run
- [ ] Service URL obtained

### Configuration
- [ ] Workflows.json updated with service URL
- [ ] Oncall.json updated with real emails/channels
- [ ] Datadog monitors imported
- [ ] Datadog dashboard imported
- [ ] Datadog SLO imported

### Verification
- [ ] Application responds to requests
- [ ] Datadog receives traces
- [ ] Datadog receives metrics
- [ ] Datadog receives logs
- [ ] Dashboard shows data
- [ ] Monitors are evaluating

---

## 🎯 Expected Results

After deployment, you should have:

1. **Service URL**: `https://llm-reliability-control-plane-xxxxx-uc.a.run.app`
2. **All endpoints working**: `/health`, `/docs`, `/qa`, `/insights`, etc.
3. **Datadog integration**: Traces, metrics, logs appearing
4. **19 Datadog products**: All integrated and working

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
gcloud run services logs read llm-reliability-control-plane --region us-central1 --limit 100

# Common issues:
# - Missing secrets: Verify secrets exist
# - Invalid API keys: Check secret values
```

### Datadog not receiving data
```bash
# Verify environment variables
gcloud run services describe llm-reliability-control-plane --region us-central1 --format="value(spec.template.spec.containers[0].env)"

# Check:
# - DD_LLMOBS_AGENTLESS_ENABLED=1
# - DD_API_KEY is set (from secret)
# - DD_SITE matches your Datadog organization
```

### Secrets not accessible
```bash
# List secrets
gcloud secrets list

# Check permissions
gcloud secrets get-iam-policy gemini-api-key
```

---

**🚀 You're Ready!** Follow these steps and your application will be live!

