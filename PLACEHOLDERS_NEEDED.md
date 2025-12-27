# 🔑 Placeholders That Need Real Values

This document lists all placeholders in the codebase that need to be replaced with actual values from your services and platforms.

## 📋 Quick Checklist

- [ ] Gemini API Key
- [ ] Datadog API Key & App Key
- [ ] Datadog Site (datadoghq.com, datadoghq.eu, etc.)
- [ ] Google Cloud Project ID
- [ ] Vertex AI Endpoints (optional)
- [ ] Datadog RUM Application ID & Client Token (optional)
- [ ] On-Call Email Addresses
- [ ] On-Call Slack Channels
- [ ] Workflow API URLs (Cloud Run service URL)

## 🔑 Required Credentials

### 1. Gemini API Key
**Where to get**: https://aistudio.google.com/app/apikey
**Where used**:
- Environment variable: `LRCP_GEMINI_API_KEY` or `GEMINI_API_KEY`
- Google Cloud Secret: `gemini-api-key`
- Files: `.env`, `env.template`, Cloud Run secrets

### 2. Datadog API Key
**Where to get**: https://app.datadoghq.com/organization-settings/api-keys
**Where used**:
- Environment variable: `LRCP_DATADOG_API_KEY` or `DD_API_KEY`
- Google Cloud Secret: `datadog-api-key`
- Files: `.env`, `env.template`, Cloud Run secrets, GitHub Actions secrets

### 3. Datadog Application Key
**Where to get**: https://app.datadoghq.com/organization-settings/application-keys
**Where used**:
- Environment variable: `DD_APP_KEY`
- Google Cloud Secret: `datadog-app-key`
- Files: `.env`, `env.template`, Cloud Run secrets, GitHub Actions secrets

### 4. Datadog Site
**Options**: `datadoghq.com`, `datadoghq.eu`, `us3.datadoghq.com`, `us5.datadoghq.com`, `ap1.datadoghq.com`, `ddog-gov.com`
**Where used**:
- Environment variable: `DD_SITE`
- Files: `.env`, `env.template`, application code

## 🌐 Google Cloud Configuration

### 5. Google Cloud Project ID
**Where to get**: https://console.cloud.google.com/
**Where used**:
- Environment variable: `LRCP_GCP_PROJECT_ID` or `GCP_PROJECT_ID`
- Google Cloud Secret: `gcp-project-id`
- Files: `.env`, `env.template`, `cloudbuild.yaml`, GitHub Actions secrets
- Commands: `gcloud config set project YOUR_PROJECT_ID`

### 6. Google Cloud Region
**Default**: `us-central1`
**Where used**:
- Environment variable: `LRCP_GCP_REGION`
- Files: `.env`, `env.template`, `cloudbuild.yaml`, deployment scripts

## 🤖 Vertex AI Configuration (Optional)

### 7. Vertex AI Endpoints
**Where to get**: Google Cloud Console → Vertex AI → Endpoints
**Format**: `https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT/locations/us-central1/endpoints/YOUR_ENDPOINT_ID:predict`
**Where used**:
- Environment variables:
  - `LRCP_VERTEX_AI_COST_ENDPOINT`
  - `LRCP_VERTEX_AI_QUALITY_ENDPOINT`
  - `LRCP_VERTEX_AI_ANOMALY_ENDPOINT`
  - `LRCP_VERTEX_AI_ROUTER_ENDPOINT`
- Files: `.env`, `env.template`

## 📊 Datadog RUM Configuration (Optional)

### 12. Datadog RUM Application ID
**Where to get**: https://app.datadoghq.com/rum/application/create
**Where used**:
- Environment variable: `NEXT_PUBLIC_DD_APPLICATION_ID`
- Files: `.env`, `env.template`, `failure-theater/` frontend code

### 13. Datadog RUM Client Token
**Where to get**: https://app.datadoghq.com/rum/application/create
**Where used**:
- Environment variable: `NEXT_PUBLIC_DD_CLIENT_TOKEN`
- Files: `.env`, `env.template`, `failure-theater/` frontend code

## 📞 On-Call Configuration

### 14. On-Call Email Addresses
**Where to update**: `datadog/oncall.json`
**Placeholders to replace**:
- `"oncall@example.com"` → Your actual on-call email
- `"team-lead@example.com"` → Your team lead email

### 15. On-Call Slack Channels
**Where to update**: `datadog/oncall.json`
**Placeholders to replace**:
- `"#llm-alerts"` → Your actual Slack channel
- `"#llm-cost-alerts"` → Your cost alerts channel
- `"#llm-quality-alerts"` → Your quality alerts channel

### 16. PagerDuty Service IDs (if using)
**Where to update**: `datadog/oncall.json`
**Placeholders to replace**:
- PagerDuty integration IDs → Your actual PagerDuty service IDs

## 🔄 Workflow Automation Configuration

### 17. Cloud Run Service URL
**Where to get**: After deploying to Cloud Run, get the service URL
**Format**: `https://llm-reliability-control-plane-xxxxx-uc.a.run.app`
**Where to update**: `datadog/workflows.json`
**Placeholders to replace**:
- `{{APP_URL}}` → Your actual Cloud Run service URL
- Example: `"url": "{{APP_URL}}/api/configure/model"` 
- Should become: `"url": "https://llm-reliability-control-plane-xxxxx-uc.a.run.app/api/configure/model"`

## 📝 Files That Need Updates

### Configuration Files
1. **`.env`** (create from `env.template`)
   - Fill in all environment variables

2. **`datadog/workflows.json`**
   - Replace `{{APP_URL}}` with Cloud Run URL

3. **`datadog/oncall.json`**
   - Replace email addresses
   - Replace Slack channels
   - Replace PagerDuty IDs (if using)

### Deployment Files
4. **`cloudbuild.yaml`**
   - Update `_REGION` if different from `us-central1`
   - Verify secret names match your Secret Manager

5. **`.github/workflows/deploy-cloud-run.yml`**
   - Update `REGION` if different
   - Verify secret names in GitHub Secrets

### Google Cloud Secrets
6. **Secret Manager** (create via `gcloud` commands)
   - `gemini-api-key`
   - `datadog-api-key`
   - `datadog-app-key`
   - `gcp-project-id` (optional)

## 🔍 How to Find Each Value

### Gemini API Key
1. Go to: https://aistudio.google.com/app/apikey
2. Click **Create API Key**
3. Copy the key

### Datadog API Key
1. Go to: https://app.datadoghq.com/organization-settings/api-keys
2. Click **New Key**
3. Name it: `LLM-Reliability-Control-Plane`
4. Copy the key

### Datadog Application Key
1. Go to: https://app.datadoghq.com/organization-settings/application-keys
2. Click **New Key**
3. Name it: `LLM-Reliability-Control-Plane`
4. Copy the key

### Google Cloud Project ID
1. Go to: https://console.cloud.google.com/
2. Select your project
3. Project ID is shown in the project selector dropdown

### Cloud Run Service URL
1. Deploy to Cloud Run (see `DEPLOYMENT_GUIDE.md`)
2. Run: `gcloud run services describe SERVICE_NAME --region REGION --format 'value(status.url)'`
3. Or find it in Cloud Console → Cloud Run → Your Service

## ✅ Verification Checklist

After filling in all placeholders, verify:

- [ ] `.env` file created with all values
- [ ] Google Cloud secrets created
- [ ] GitHub secrets created (if using GitHub Actions)
- [ ] `datadog/workflows.json` has real Cloud Run URL
- [ ] `datadog/oncall.json` has real emails and channels
- [ ] Application starts successfully
- [ ] Datadog receives metrics/logs/traces
- [ ] Monitors are evaluating
- [ ] Dashboard shows data

## 🐛 Common Issues

### "API key not found"
- Check environment variable is set
- Verify variable name matches (case-sensitive)
- Check `.env` file is in correct location

### "Secret not found in Secret Manager"
- Verify secret exists: `gcloud secrets list`
- Check secret name matches exactly
- Verify IAM permissions for service account

### "Invalid Datadog site"
- Check `DD_SITE` matches your Datadog organization
- Common values: `datadoghq.com`, `datadoghq.eu`, `us3.datadoghq.com`

### "Workflow API call fails"
- Verify `{{APP_URL}}` is replaced with actual URL
- Check Cloud Run service is deployed and accessible
- Verify endpoint exists: `{URL}/api/configure/model`

---

**📝 Next Steps**:
1. Fill in all placeholders in this document
2. Create `.env` file from `env.template`
3. Create Google Cloud secrets
4. Update JSON configuration files
5. Deploy and test

