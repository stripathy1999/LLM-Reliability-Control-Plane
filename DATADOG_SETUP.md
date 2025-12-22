# Datadog Setup Guide for LLM Reliability Control Plane

This guide walks through setting up Datadog observability for the hackathon submission.

## Prerequisites

1. Datadog account (sign up at https://www.datadoghq.com/)
2. Datadog API key and Application key
3. Datadog agent installed (for local development) or access to remote agent

## Step 1: Get Datadog Credentials

1. Log into Datadog
2. Go to **Organization Settings** → **API Keys**
3. Create a new API key (or use existing)
4. Go to **Organization Settings** → **Application Keys**
5. Create a new Application key (needed for API imports)

## Step 2: Configure Environment

1. Copy `.env.example` to `.env`
2. Fill in your credentials:

```bash
LRCP_DATADOG_API_KEY=your-api-key-here
DD_APP_KEY=your-app-key-here
DD_SITE=datadoghq.com  # or datadoghq.eu, us3.datadoghq.com
DD_AGENT_HOST=localhost  # or your agent hostname
```

## Step 3: Install Datadog Agent (Local)

### macOS
```bash
brew install datadog-agent
datadog-agent start
```

### Linux
```bash
DD_API_KEY=your-api-key DD_SITE=datadoghq.com bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)"
sudo systemctl start datadog-agent
```

### Windows
Download installer from: https://docs.datadog.com/agent/install/?tab=windows

## Step 4: Import Monitors

### Option A: Via Datadog UI

1. Go to **Monitors** → **New Monitor**
2. Click **Import** (or use JSON editor)
3. Copy contents of `datadog/monitors.json`
4. Import each monitor definition

### Option B: Via Datadog API

```bash
# Install datadog CLI or use curl
curl -X POST "https://api.datadoghq.com/api/v1/monitor" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${LRCP_DATADOG_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @datadog/monitors.json
```

**Note**: The monitors JSON contains an array. You'll need to import each monitor individually or write a script to loop through them.

## Step 5: Import Dashboard

### Option A: Via Datadog UI

1. Go to **Dashboards** → **New Dashboard**
2. Click **Import** (or use JSON editor)
3. Paste contents of `datadog/dashboard.json`
4. Save dashboard

### Option B: Via Datadog API

```bash
curl -X POST "https://api.datadoghq.com/api/v1/dashboard" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${LRCP_DATADOG_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @datadog/dashboard.json
```

## Step 6: Import SLO

1. Go to **Service Management** → **SLOs** → **New SLO**
2. Click **Import** (or use JSON editor)
3. Paste contents of `datadog/slo.json`
4. Save SLO

## Step 7: Configure Incident Rules

1. Go to **Incidents** → **Settings** → **Rules**
2. Create incident rules that:
   - Match monitors with tag `critical`
   - Auto-attach dashboard: "LLM Reliability Control Plane"
   - Auto-attach logs filtered by `service:llm-reliability-control-plane`
   - Auto-attach traces for the service

Example incident rule:
- **Trigger**: Monitor alert with tag `critical`
- **Actions**: 
  - Create incident
  - Attach dashboard: "LLM Reliability Control Plane"
  - Attach logs: `service:llm-reliability-control-plane`
  - Attach traces: `service:llm-reliability-control-plane`

## Step 8: Verify Setup

1. Start the API:
```bash
uvicorn app.main:app --reload
```

2. Run traffic generator:
```bash
python traffic-generator/generate_load.py
```

3. Check Datadog:
   - **APM Traces**: Should see traces for `/qa`, `/reason`, `/stress`
   - **Metrics**: Search for `llm.request.latency_ms`, `llm.cost.usd`, etc.
   - **Logs**: Filter by `service:llm-reliability-control-plane`
   - **Dashboard**: Should populate with metrics
   - **Monitors**: Should evaluate (may trigger if thresholds exceeded)

## Step 9: Test Incident Creation

Trigger a monitor intentionally:

1. Call an endpoint with failure toggles:
```bash
curl -X POST "http://localhost:8000/qa?simulate_latency=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "document": "test"}'
```

2. Repeat multiple times to exceed monitor thresholds

3. Check **Incidents** in Datadog - should see auto-created incident with:
   - Monitor details
   - Attached dashboard
   - Relevant logs
   - Traces (if configured)

## Troubleshooting

### Metrics not appearing
- Check Datadog agent is running: `datadog-agent status`
- Verify `DD_AGENT_HOST` and `DD_DOGSTATSD_PORT` in `.env`
- Check agent logs: `datadog-agent status`

### Traces not appearing
- Verify `DD_TRACE_ENABLED=true` in environment
- Check APM is enabled in agent config
- Verify `DD_AGENT_HOST` and `DD_TRACE_AGENT_PORT` are correct

### Logs not appearing
- Ensure `DD_LOGS_ENABLED=true`
- Check log ingestion is enabled in Datadog account
- Verify service tags in log payloads

### Monitors not triggering
- Verify metrics exist in Datadog Metrics Explorer
- Check monitor query syntax matches metric names
- Ensure monitor evaluation window has data

## Production Deployment (GCP Cloud Run)

For Cloud Run deployment:

1. Set environment variables in Cloud Run service configuration
2. Install Datadog agent as sidecar or use Datadog Cloud Run integration
3. Update `DD_AGENT_HOST` to point to agent endpoint
4. Ensure APM and log ingestion are enabled

See: https://docs.datadog.com/integrations/google_cloud_run/

