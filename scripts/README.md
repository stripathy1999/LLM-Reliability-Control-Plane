# Deployment Scripts

## Quick Start

1. **Install Google Cloud SDK** (if not installed):
   - Windows: Download from https://cloud.google.com/sdk/docs/install
   - Or: `winget install Google.CloudSDK`

2. **Authenticate**:
   ```powershell
   gcloud auth login
   ```

3. **Run Setup Script**:
   ```powershell
   .\setup_secrets_with_credentials.ps1
   ```

4. **Deploy**:
   ```powershell
   .\deploy_to_cloud_run_with_credentials.ps1
   ```

## Scripts

### `setup_secrets_with_credentials.ps1`
- Creates all secrets in Google Secret Manager
- Uses your actual credentials (already configured)
- Grants Cloud Run access to secrets

### `deploy_to_cloud_run_with_credentials.ps1`
- Enables required APIs
- Builds Docker image
- Deploys to Cloud Run
- Shows service URL

### `setup_gcp_secrets.ps1` / `setup_gcp_secrets.sh`
- Interactive version (prompts for credentials)
- Use if you want to enter credentials manually

### `deploy_to_cloud_run.ps1` / `deploy_to_cloud_run.sh`
- Generic deployment script
- Uses project ID: `llm-reliability-control`

## Notes

- All credentials are already configured in `setup_secrets_with_credentials.ps1`
- Datadog site is set to: `us5.datadoghq.com`
- Project ID is: `llm-reliability-control`
- All Datadog credentials configured

