# 🚀 Deployment Guide - Google Cloud Run

This guide provides step-by-step instructions to deploy the LLM Reliability Control Plane to Google Cloud Run.

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK (gcloud)** installed and configured
3. **Docker** installed (for local testing)
4. **API Keys Ready**:
   - Gemini API Key
   - Datadog API Key & App Key
   - (Optional) Vertex AI endpoints
   - (Optional) Vertex AI credentials

## 🔧 Step 1: Install Google Cloud SDK

### Windows (PowerShell)
```powershell
# Download and install from:
# https://cloud.google.com/sdk/docs/install

# Verify installation
gcloud --version
```

### macOS
```bash
# Using Homebrew
brew install --cask google-cloud-sdk

# Verify installation
gcloud --version
```

### Linux
```bash
# Add Cloud SDK repository
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Install
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt-get update && sudo apt-get install google-cloud-cli

# Verify installation
gcloud --version
```

## 🔐 Step 2: Authenticate and Configure GCP

```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com

# Verify project
gcloud config get-value project
```

## 🔑 Step 3: Create Google Cloud Secrets

Store sensitive credentials in Google Secret Manager:

```bash
# Set your project ID
export PROJECT_ID=YOUR_PROJECT_ID

# Create secrets
echo -n "your-gemini-api-key" | gcloud secrets create gemini-api-key --data-file=-
echo -n "your-datadog-api-key" | gcloud secrets create datadog-api-key --data-file=-
echo -n "your-datadog-app-key" | gcloud secrets create datadog-app-key --data-file=-

# Optional: GCP Project ID (if different from current)
echo -n "your-gcp-project-id" | gcloud secrets create gcp-project-id --data-file=-

# Grant Cloud Run service account access to secrets
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
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

## 🐳 Step 4: Build and Test Docker Image Locally (Optional)

```bash
# Build the image
docker build -t llm-reliability-control-plane:local .

# Test locally (set environment variables)
docker run -p 8000:8000 \
  -e LRCP_GEMINI_API_KEY="your-key" \
  -e LRCP_DATADOG_API_KEY="your-key" \
  -e DD_APP_KEY="your-key" \
  -e DD_SITE="datadoghq.com" \
  -e DD_SERVICE="llm-reliability-control-plane" \
  -e DD_ENV="local" \
  -e DD_LLMOBS_AGENTLESS_ENABLED=1 \
  llm-reliability-control-plane:local

# Test in browser: http://localhost:8000/docs
```

## 🚀 Step 5: Deploy to Cloud Run (Manual)

### Option A: Using gcloud CLI

```bash
# Set variables
export PROJECT_ID=YOUR_PROJECT_ID
export REGION=us-central1
export SERVICE_NAME=llm-reliability-control-plane

# Build and push to Container Registry
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars "DD_SERVICE=llm-reliability-control-plane,DD_ENV=production,DD_VERSION=1.0.0,DD_LLMOBS_AGENTLESS_ENABLED=1,DD_TRACE_ENABLED=true,DD_LOGS_ENABLED=true,DD_SITE=datadoghq.com" \
  --set-secrets "LRCP_GEMINI_API_KEY=gemini-api-key:latest,LRCP_DATADOG_API_KEY=datadog-api-key:latest,DD_APP_KEY=datadog-app-key:latest"

# Get the service URL
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
```

### Option B: Using Cloud Build (Automated)

```bash
# Submit build using cloudbuild.yaml
gcloud builds submit --config cloudbuild.yaml

# The build will automatically:
# 1. Build Docker image
# 2. Push to Container Registry
# 3. Deploy to Cloud Run
```

## 🔄 Step 6: Set Up Continuous Deployment (Optional)

### Using GitHub Actions

1. **Add GitHub Secrets**:
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `GCP_PROJECT_ID`: Your GCP project ID
     - `GCP_SA_KEY`: Service account key JSON (see below)

2. **Create Service Account for GitHub Actions**:
```bash
# Create service account
gcloud iam service-accounts create github-actions-sa \
    --display-name="GitHub Actions Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com

# Copy the contents of github-actions-key.json to GitHub secret GCP_SA_KEY
```

3. **Push to main branch** - GitHub Actions will automatically deploy!

### Using Cloud Build Triggers

```bash
# Connect repository to Cloud Build
gcloud builds triggers create github \
  --name="deploy-on-push" \
  --repo-name="YOUR_REPO_NAME" \
  --repo-owner="YOUR_GITHUB_USERNAME" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml"
```

## ✅ Step 7: Verify Deployment

```bash
# Get service URL
export SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Test API docs
# Open in browser: $SERVICE_URL/docs

# Check logs
gcloud run services logs read $SERVICE_NAME --region $REGION --limit 50
```

## 🔧 Step 8: Update Environment Variables

To update environment variables or secrets after deployment:

```bash
# Update environment variables
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --update-env-vars "DD_ENV=production,DD_VERSION=1.1.0"

# Update secrets
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --update-secrets "LRCP_GEMINI_API_KEY=gemini-api-key:latest"
```

## 📊 Step 9: Monitor in Datadog

1. **Verify Datadog Integration**:
   - Go to Datadog → APM → Services
   - Look for `llm-reliability-control-plane`
   - Check that traces are appearing

2. **Check Metrics**:
   - Go to Datadog → Metrics Explorer
   - Search for `llm.*` metrics
   - Verify metrics are being sent

3. **View Logs**:
   - Go to Datadog → Logs
   - Filter by `service:llm-reliability-control-plane`
   - Verify logs are appearing

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
gcloud run services logs read $SERVICE_NAME --region $REGION --limit 100

# Common issues:
# - Missing secrets: Verify secrets exist and are accessible
# - Invalid API keys: Check secret values
# - Port issues: Cloud Run uses PORT env var automatically
```

### Datadog not receiving data
```bash
# Verify environment variables
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)"

# Check DD_LLMOBS_AGENTLESS_ENABLED=1 is set
# Check DD_API_KEY is set correctly
```

### High latency
```bash
# Increase memory/CPU
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --memory 4Gi \
  --cpu 4
```

## 📝 Next Steps

1. **Import Datadog Resources**: See [DATADOG_IMPORT_GUIDE.md](DATADOG_IMPORT_GUIDE.md)
2. **Set Up Vertex AI**: See [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md)
3. **Configure Monitoring**: Import monitors and dashboards from `datadog/` folder

## 🔗 Useful Commands

```bash
# List all Cloud Run services
gcloud run services list

# View service details
gcloud run services describe $SERVICE_NAME --region $REGION

# Delete service
gcloud run services delete $SERVICE_NAME --region $REGION

# View service URL
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'

# Stream logs
gcloud run services logs tail $SERVICE_NAME --region $REGION
```

---

**🎉 Deployment Complete!** Your service should now be accessible at the Cloud Run URL.

