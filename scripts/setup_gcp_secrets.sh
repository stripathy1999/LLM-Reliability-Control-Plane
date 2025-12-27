#!/bin/bash
# Setup Google Cloud Secrets with your credentials
# This script creates all required secrets in Google Secret Manager

set -e

# Your project ID
PROJECT_ID="llm-reliability-control"
REGION="us-central1"

echo "🚀 Setting up Google Cloud Secrets for project: $PROJECT_ID"

# Set project
gcloud config set project $PROJECT_ID

# Enable Secret Manager API
echo "📦 Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

# Get project number for service account
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
echo "📊 Project Number: $PROJECT_NUMBER"

# Prompt for credentials
echo ""
echo "Please provide the following credentials:"
echo ""

read -p "Gemini API Key: " GEMINI_API_KEY
read -p "Datadog API Key: " DATADOG_API_KEY
read -p "Datadog App Key: " DATADOG_APP_KEY
read -p "Datadog Site (datadoghq.com, datadoghq.eu, etc.): " DD_SITE

# Confluent credentials (already provided)
CONFLUENT_BOOTSTRAP="pkc-619z3.us-east1.gcp.confluent.cloud:9092"
CONFLUENT_API_KEY="53CGSDMC2E7HOPN3"
CONFLUENT_API_SECRET="cfltC5QSsc7nWwn7nA1v68Q8kdsBBVbst2n89xtQ2S3Srzf7r761vZjOStlyBqDg"

echo ""
echo "🔐 Creating secrets in Secret Manager..."

# Create secrets
echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
  echo -n "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=- --project=$PROJECT_ID

echo -n "$DATADOG_API_KEY" | gcloud secrets create datadog-api-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
  echo -n "$DATADOG_API_KEY" | gcloud secrets versions add datadog-api-key --data-file=- --project=$PROJECT_ID

echo -n "$DATADOG_APP_KEY" | gcloud secrets create datadog-app-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
  echo -n "$DATADOG_APP_KEY" | gcloud secrets versions add datadog-app-key --data-file=- --project=$PROJECT_ID

echo -n "$CONFLUENT_BOOTSTRAP" | gcloud secrets create confluent-bootstrap --data-file=- --project=$PROJECT_ID 2>/dev/null || \
  echo -n "$CONFLUENT_BOOTSTRAP" | gcloud secrets versions add confluent-bootstrap --data-file=- --project=$PROJECT_ID

echo -n "$CONFLUENT_API_KEY" | gcloud secrets create confluent-api-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
  echo -n "$CONFLUENT_API_KEY" | gcloud secrets versions add confluent-api-key --data-file=- --project=$PROJECT_ID

echo -n "$CONFLUENT_API_SECRET" | gcloud secrets create confluent-api-secret --data-file=- --project=$PROJECT_ID 2>/dev/null || \
  echo -n "$CONFLUENT_API_SECRET" | gcloud secrets versions add confluent-api-secret --data-file=- --project=$PROJECT_ID

echo -n "$PROJECT_ID" | gcloud secrets create gcp-project-id --data-file=- --project=$PROJECT_ID 2>/dev/null || \
  echo -n "$PROJECT_ID" | gcloud secrets versions add gcp-project-id --data-file=- --project=$PROJECT_ID

echo ""
echo "🔑 Granting Cloud Run service account access to secrets..."

# Grant Cloud Run service account access
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding datadog-api-key \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding datadog-app-key \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding confluent-bootstrap \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding confluent-api-key \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding confluent-api-secret \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

gcloud secrets add-iam-policy-binding gcp-project-id \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

echo ""
echo "✅ Secrets created and permissions granted!"
echo ""
echo "📋 Created secrets:"
echo "  - gemini-api-key"
echo "  - datadog-api-key"
echo "  - datadog-app-key"
echo "  - confluent-bootstrap"
echo "  - confluent-api-key"
echo "  - confluent-api-secret"
echo "  - gcp-project-id"
echo ""
echo "🚀 Next step: Run deployment script or deploy manually"

