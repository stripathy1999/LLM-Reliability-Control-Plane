# 🤖 Vertex AI Setup Guide

This guide provides step-by-step instructions to set up Google Cloud Vertex AI for ML model deployment and inference.

## 📋 Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Vertex AI API** enabled
3. **Google Cloud SDK** installed and authenticated
4. **Python 3.9+** with `google-cloud-aiplatform` installed

## 🔧 Step 1: Install Vertex AI SDK

### Install Python Package

```bash
# Install the Vertex AI SDK
pip install google-cloud-aiplatform==1.38.1

# Verify installation
python -c "import google.cloud.aiplatform; print(google.cloud.aiplatform.__version__)"
```

### Install Google Cloud CLI (if not already installed)

```bash
# Windows (PowerShell)
# Download from: https://cloud.google.com/sdk/docs/install

# macOS
brew install --cask google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

## 🔐 Step 2: Authenticate with Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Verify authentication
gcloud auth application-default login
```

## 🏗️ Step 3: Set Up Service Account (Recommended)

### Create Service Account

```bash
export PROJECT_ID=YOUR_PROJECT_ID
export SERVICE_ACCOUNT_NAME=vertex-ai-service-account

# Create service account
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="Vertex AI Service Account" \
    --project=$PROJECT_ID

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Create and download key
gcloud iam service-accounts keys create vertex-ai-key.json \
    --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/vertex-ai-key.json
```

### For Cloud Run Deployment

```bash
# Grant Cloud Run service account access
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

## 🚀 Step 4: Deploy ML Models to Vertex AI

### Option A: Deploy Pre-trained Models (Cost Predictor, Quality Predictor, etc.)

Create a deployment script `scripts/deploy_vertex_ai_models.py`:

```python
"""Deploy ML models to Vertex AI Endpoints"""
from google.cloud import aiplatform
import os

PROJECT_ID = os.getenv("LRCP_GCP_PROJECT_ID", "your-project-id")
REGION = os.getenv("LRCP_GCP_REGION", "us-central1")
MODEL_DISPLAY_NAME = "llm-cost-predictor"

# Initialize Vertex AI
aiplatform.init(project=PROJECT_ID, location=REGION)

# Upload model (if you have a saved model)
# model = aiplatform.Model.upload(
#     display_name=MODEL_DISPLAY_NAME,
#     artifact_uri="gs://your-bucket/models/cost_predictor",
#     serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest"
# )

# Create endpoint
endpoint = aiplatform.Endpoint.create(display_name=f"{MODEL_DISPLAY_NAME}-endpoint")

print(f"Endpoint created: {endpoint.resource_name}")
print(f"Endpoint ID: {endpoint.name}")
```

### Option B: Use Vertex AI Pre-built Models

For this project, we can use Vertex AI's pre-built models or deploy custom models:

```python
from google.cloud import aiplatform

# Initialize
aiplatform.init(project=PROJECT_ID, location=REGION)

# Use Vertex AI's AutoML or custom models
# This is where you'd deploy your cost predictor, quality predictor, etc.
```

## 🔗 Step 5: Configure Application to Use Vertex AI

### Update Environment Variables

Add to your `.env` or Cloud Run secrets:

```bash
# Vertex AI Configuration
LRCP_GCP_PROJECT_ID=your-project-id
LRCP_GCP_REGION=us-central1

# Vertex AI Endpoints (if using deployed models)
LRCP_VERTEX_AI_COST_ENDPOINT=https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT/locations/us-central1/endpoints/YOUR_ENDPOINT_ID:predict
LRCP_VERTEX_AI_QUALITY_ENDPOINT=https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT/locations/us-central1/endpoints/YOUR_ENDPOINT_ID:predict
LRCP_VERTEX_AI_ANOMALY_ENDPOINT=https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT/locations/us-central1/endpoints/YOUR_ENDPOINT_ID:predict
LRCP_VERTEX_AI_ROUTER_ENDPOINT=https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT/locations/us-central1/endpoints/YOUR_ENDPOINT_ID:predict
```

### Update Application Code

The application already has Vertex AI integration in:
- `app/ml_cost_predictor.py` - Cost prediction
- `app/ml_quality_predictor.py` - Quality prediction
- `app/model_router.py` - Model routing

These files will automatically use Vertex AI if endpoints are configured.

## 🧪 Step 6: Test Vertex AI Integration

### Test Cost Predictor

```python
from app.ml_cost_predictor import MLCostPredictor

predictor = MLCostPredictor()
prediction = predictor.predict_cost(
    input_tokens=1000,
    output_tokens=500,
    model="gemini-2.5-flash"
)
print(f"Predicted cost: ${prediction}")
```

### Test Quality Predictor

```python
from app.ml_quality_predictor import MLQualityPredictor

predictor = MLQualityPredictor()
quality_score = predictor.predict_quality(
    prompt="Test prompt",
    response="Test response",
    document="Test document"
)
print(f"Quality score: {quality_score}")
```

### Test Model Router

```python
from app.model_router import ModelRouter

router = ModelRouter()
decision = router.route(
    prompt="Test prompt",
    request_type="qa",
    user_id="test-user"
)
print(f"Routing decision: {decision}")
```

## 📊 Step 7: Monitor Vertex AI Usage

### View in Google Cloud Console

1. Go to: **Vertex AI** → **Endpoints**
2. View endpoint usage, latency, and errors
3. Check **Vertex AI** → **Models** for deployed models

### View Costs

1. Go to: **Billing** → **Reports**
2. Filter by **Vertex AI** service
3. Monitor prediction costs

## 🔄 Step 8: Deploy Models via Cloud Build (Optional)

Create `cloudbuild-models.yaml`:

```yaml
steps:
  # Train and deploy cost predictor
  - name: 'gcr.io/cloud-builders/python'
    args:
      - 'python'
      - 'scripts/train_models.py'
      - '--model'
      - 'cost_predictor'
    env:
      - 'LRCP_GCP_PROJECT_ID=$PROJECT_ID'
      - 'LRCP_GCP_REGION=us-central1'

  # Deploy to Vertex AI
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'gcloud'
    args:
      - 'ai-platform'
      - 'models'
      - 'create'
      - '--model=llm-cost-predictor'
      - '--regions=us-central1'
```

## 🐛 Troubleshooting

### Authentication Errors

```bash
# Re-authenticate
gcloud auth application-default login

# Verify credentials
gcloud auth list

# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID
```

### API Not Enabled

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Verify
gcloud services list --enabled | grep aiplatform
```

### Endpoint Not Found

- Verify endpoint ID is correct
- Check endpoint exists in Vertex AI console
- Verify region matches

### High Latency

- Use regional endpoints (same region as Cloud Run)
- Consider batch predictions for non-real-time use cases
- Optimize model size

## 📝 Next Steps

1. **Deploy Models**: Use the deployment script to deploy your ML models
2. **Update Endpoints**: Update environment variables with actual endpoint URLs
3. **Test Integration**: Run test scripts to verify Vertex AI integration
4. **Monitor Usage**: Set up billing alerts for Vertex AI costs

## 🔗 Useful Commands

```bash
# List all endpoints
gcloud ai endpoints list --region=us-central1

# Describe endpoint
gcloud ai endpoints describe ENDPOINT_ID --region=us-central1

# List models
gcloud ai models list --region=us-central1

# Predict using endpoint
gcloud ai endpoints predict ENDPOINT_ID \
  --region=us-central1 \
  --json-request=request.json
```

## 📚 Additional Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Vertex AI Python SDK](https://cloud.google.com/python/docs/reference/aiplatform/latest)
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)
- [Vertex AI Best Practices](https://cloud.google.com/vertex-ai/docs/general/best-practices)

---

**🎉 Vertex AI Setup Complete!** Your application can now use Vertex AI for ML inference.

