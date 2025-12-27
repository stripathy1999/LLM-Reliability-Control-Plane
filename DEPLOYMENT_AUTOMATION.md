# 🤖 Deployment Automation Guide

This guide covers setting up automated deployment pipelines for the LLM Reliability Control Plane.

## 🎯 Overview

We'll set up automated deployment using:
1. **GitHub Actions** - For CI/CD from GitHub
2. **Google Cloud Build** - For GCP-native CI/CD
3. **Cloud Build Triggers** - For automatic deployments

## 🔧 Option 1: GitHub Actions (Recommended for GitHub Repos)

### Step 1: Set Up GitHub Secrets

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:

#### Required Secrets:
- `GCP_PROJECT_ID`: Your Google Cloud project ID
- `GCP_SA_KEY`: Service account key JSON (see below)
- `DD_API_KEY`: Datadog API key (optional, for deployment notifications)
- `DD_APP_KEY`: Datadog App key (optional)

#### Create Service Account for GitHub Actions

```bash
export PROJECT_ID=YOUR_PROJECT_ID
export SA_NAME=github-actions-sa

# Create service account
gcloud iam service-accounts create $SA_NAME \
    --display-name="GitHub Actions Service Account" \
    --project=$PROJECT_ID

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com

# Copy the entire contents of github-actions-key.json
# Paste into GitHub secret: GCP_SA_KEY
```

### Step 2: Workflow File Already Created

The workflow file `.github/workflows/deploy-cloud-run.yml` is already created. It will:
- Trigger on push to `main` or `master` branch
- Build Docker image
- Push to Google Container Registry
- Deploy to Cloud Run
- Use secrets from Secret Manager

### Step 3: Test Deployment

```bash
# Push to main branch
git add .
git commit -m "Setup automated deployment"
git push origin main

# Check GitHub Actions tab for deployment status
```

## 🔧 Option 2: Google Cloud Build

### Step 1: Enable Cloud Build API

```bash
gcloud services enable cloudbuild.googleapis.com
```

### Step 2: Grant Cloud Build Permissions

```bash
export PROJECT_ID=YOUR_PROJECT_ID
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Grant Cloud Build service account necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Step 3: Create Cloud Build Trigger

#### Option A: Using gcloud CLI

```bash
# Create trigger for GitHub
gcloud builds triggers create github \
    --name="deploy-llm-control-plane" \
    --repo-name="YOUR_REPO_NAME" \
    --repo-owner="YOUR_GITHUB_USERNAME" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml" \
    --region=us-central1

# Or create trigger for Cloud Source Repositories
gcloud builds triggers create cloud-source-repositories \
    --name="deploy-llm-control-plane" \
    --repo="YOUR_REPO_NAME" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml" \
    --region=us-central1
```

#### Option B: Using Cloud Console

1. Go to: **Cloud Build** → **Triggers**
2. Click **Create Trigger**
3. Configure:
   - **Name**: `deploy-llm-control-plane`
   - **Event**: Push to a branch
   - **Branch**: `^main$`
   - **Configuration**: Cloud Build configuration file
   - **Location**: `cloudbuild.yaml`
4. Click **Create**

### Step 4: Test Cloud Build

```bash
# Manually trigger build
gcloud builds submit --config cloudbuild.yaml

# Or trigger via API
gcloud builds triggers run deploy-llm-control-plane --branch=main
```

## 🔧 Option 3: Cloud Build with GitHub Integration

### Step 1: Connect GitHub Repository

1. Go to: **Cloud Build** → **Triggers** → **Connect Repository**
2. Select **GitHub (Cloud Build GitHub App)**
3. Authenticate with GitHub
4. Select your repository
5. Click **Connect**

### Step 2: Create Trigger

1. Click **Create Trigger**
2. Configure:
   - **Name**: `deploy-on-push`
   - **Event**: Push to a branch
   - **Branch**: `^main$`
   - **Configuration**: Cloud Build configuration file
   - **Location**: `cloudbuild.yaml`
3. Click **Create**

## 🔐 Step 4: Set Up Secrets in Secret Manager

Cloud Build and Cloud Run need access to secrets:

```bash
export PROJECT_ID=YOUR_PROJECT_ID

# Create secrets (if not already created)
echo -n "your-gemini-api-key" | gcloud secrets create gemini-api-key --data-file=-
echo -n "your-datadog-api-key" | gcloud secrets create datadog-api-key --data-file=-
echo -n "your-datadog-app-key" | gcloud secrets create datadog-app-key --data-file=-

# Grant Cloud Build access
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding datadog-api-key \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding datadog-app-key \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## 🚀 Step 5: Customize Deployment

### Update cloudbuild.yaml

Edit `cloudbuild.yaml` to customize:
- **Region**: Change `_REGION` substitution
- **Memory/CPU**: Update Cloud Run resource limits
- **Environment Variables**: Add/remove env vars
- **Secrets**: Add/remove secrets

### Update GitHub Actions Workflow

Edit `.github/workflows/deploy-cloud-run.yml` to customize:
- **Triggers**: Change branch patterns
- **Deployment settings**: Update memory, CPU, etc.
- **Notifications**: Add Slack/Datadog notifications

## 📊 Step 6: Add Deployment Notifications

### Datadog Events

Add to your workflow/cloudbuild:

```yaml
# In cloudbuild.yaml or GitHub Actions
- name: 'Send Datadog Event'
  run: |
    curl -X POST "https://api.datadoghq.com/api/v1/events" \
      -H "Content-Type: application/json" \
      -H "DD-API-KEY: ${DD_API_KEY}" \
      -d '{
        "title": "Deployment Successful",
        "text": "LLM Reliability Control Plane deployed to Cloud Run",
        "tags": ["deployment", "cloud-run"]
      }'
```

### Slack Notifications

```yaml
- name: 'Notify Slack'
  run: |
    curl -X POST "${{ secrets.SLACK_WEBHOOK_URL }}" \
      -H "Content-Type: application/json" \
      -d '{
        "text": "✅ Deployment successful: ${{ steps.service-url.outputs.url }}"
      }'
```

## 🔄 Step 7: Set Up Staging/Production Environments

### Create Separate Cloud Run Services

```bash
# Deploy to staging
gcloud run deploy llm-reliability-control-plane-staging \
  --image gcr.io/$PROJECT_ID/llm-reliability-control-plane:$GITHUB_SHA \
  --region us-central1 \
  --set-env-vars "DD_ENV=staging"

# Deploy to production (manual approval)
gcloud run deploy llm-reliability-control-plane \
  --image gcr.io/$PROJECT_ID/llm-reliability-control-plane:$GITHUB_SHA \
  --region us-central1 \
  --set-env-vars "DD_ENV=production"
```

### Update Workflow for Multi-Environment

Edit `.github/workflows/deploy-cloud-run.yml`:

```yaml
jobs:
  deploy-staging:
    # Deploy to staging automatically
    if: github.ref == 'refs/heads/main'
  
  deploy-production:
    # Deploy to production with manual approval
    needs: deploy-staging
    if: github.event_name == 'workflow_dispatch'
```

## ✅ Step 8: Verify Automated Deployment

### Check Deployment Status

```bash
# View Cloud Build history
gcloud builds list --limit=10

# View Cloud Run revisions
gcloud run revisions list --service=llm-reliability-control-plane --region=us-central1

# View service URL
gcloud run services describe llm-reliability-control-plane --region=us-central1 --format='value(status.url)'
```

### Test Deployment

```bash
# Get service URL
export SERVICE_URL=$(gcloud run services describe llm-reliability-control-plane --region=us-central1 --format='value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Test API docs
curl $SERVICE_URL/docs
```

## 🐛 Troubleshooting

### Build Fails

```bash
# Check build logs
gcloud builds log BUILD_ID

# Common issues:
# - Missing permissions: Grant necessary IAM roles
# - Invalid secrets: Verify secrets exist in Secret Manager
# - Docker build fails: Check Dockerfile syntax
```

### Deployment Fails

```bash
# Check Cloud Run logs
gcloud run services logs read llm-reliability-control-plane --region=us-central1 --limit=50

# Common issues:
# - Missing environment variables: Check cloudbuild.yaml
# - Invalid secrets: Verify secret names and access
# - Port issues: Cloud Run uses PORT env var automatically
```

### Secrets Not Accessible

```bash
# Verify secrets exist
gcloud secrets list

# Check IAM bindings
gcloud secrets get-iam-policy SECRET_NAME

# Grant access
gcloud secrets add-iam-policy-binding SECRET_NAME \
    --member="serviceAccount:SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
```

## 📝 Best Practices

1. **Use Secrets**: Never hardcode API keys in code
2. **Tag Images**: Use commit SHA for image tags
3. **Rollback Strategy**: Keep previous revisions for quick rollback
4. **Monitor Deployments**: Set up alerts for failed deployments
5. **Test Before Deploy**: Run tests in CI before deployment
6. **Gradual Rollout**: Use traffic splitting for safe deployments

## 🔗 Useful Commands

```bash
# View build history
gcloud builds list

# View trigger details
gcloud builds triggers describe TRIGGER_NAME

# Manually trigger build
gcloud builds triggers run TRIGGER_NAME --branch=main

# View Cloud Run service details
gcloud run services describe SERVICE_NAME --region=REGION

# Rollback to previous revision
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions=REVISION_NAME=100 \
  --region=REGION
```

---

**🎉 Deployment Automation Complete!** Your application will now automatically deploy on every push to main.

