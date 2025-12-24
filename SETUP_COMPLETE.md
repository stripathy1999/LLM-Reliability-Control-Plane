# Complete Setup Guide - End-to-End Execution

## ✅ Prerequisites Completed
- [x] Datadog account created
- [x] API Key: `765bcbbb809c7cedda7e316fd2337d9c`
- [x] Application Key: `b9043f0e53a84f0b96b82b568a9ec5ee1bbeb28a`
- [x] Datadog Site: `datadoghq.com`

## Step 1: Set Environment Variables (PowerShell)

**For Current Session:**
```powershell
$env:LRCP_DATADOG_API_KEY = "765bcbbb809c7cedda7e316fd2337d9c"
$env:DD_APP_KEY = "b9043f0e53a84f0b96b82b568a9ec5ee1bbeb28a"
$env:DD_SITE = "datadoghq.com"
$env:DD_AGENT_HOST = "localhost"
$env:DD_TRACE_ENABLED = "true"
$env:DD_LOGS_ENABLED = "true"
```

**To Make Permanent (Optional):**
```powershell
[System.Environment]::SetEnvironmentVariable("LRCP_DATADOG_API_KEY", "765bcbbb809c7cedda7e316fd2337d9c", "User")
[System.Environment]::SetEnvironmentVariable("DD_APP_KEY", "b9043f0e53a84f0b96b82b568a9ec5ee1bbeb28a", "User")
[System.Environment]::SetEnvironmentVariable("DD_SITE", "datadoghq.com", "User")
```

## Step 2: Activate Virtual Environment

```powershell
cd "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
.\venv\bin\Activate.ps1
```

## Step 3: Import Datadog Resources

### Option A: Via Datadog UI (Easiest - Recommended)

1. **Import Monitors:**
   - Go to https://app.datadoghq.com/monitors/manage
   - Click "New Monitor" → "Import JSON"
   - Open `datadog/monitors.json`
   - Copy each monitor (remove `incident_config` field - it's not part of API)
   - Create each monitor individually

2. **Import Dashboard:**
   - Go to https://app.datadoghq.com/dashboard/lists
   - Click "New Dashboard" → "Import JSON"
   - Copy entire contents of `datadog/dashboard.json`
   - Paste and save

3. **Import SLO:**
   - Go to https://app.datadoghq.com/slo
   - Click "New SLO" → "Import JSON"
   - Copy contents of `datadog/slo.json`
   - Save

### Option B: Via API (If Application Key has proper permissions)

```powershell
python scripts/import_datadog_resources.py
```

**Note:** If you get 403 Forbidden, ensure your Application Key has:
- Monitors Write permission
- Dashboards Write permission  
- SLOs Write permission

## Step 4: Start the Application

```powershell
# Make sure you're in the project directory and venv is activated
cd "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
.\venv\bin\Activate.ps1

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## Step 5: Test the API Endpoints

### Test Basic Endpoint
```powershell
$body = @{question="What is Datadog?"; document="Datadog is an observability platform."} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/qa" -Method POST -ContentType "application/json" -Body $body
```

### Test with Latency Simulation
```powershell
$body = @{question="test"; document="test"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/qa?simulate_latency=true" -Method POST -ContentType "application/json" -Body $body
```

### Test Insights Endpoint
```powershell
$body = @{
    avg_latency_ms=1200
    error_rate=0.02
    retry_rate=0.05
    avg_cost_per_request=0.008
    avg_input_tokens=1500
    avg_output_tokens=200
    avg_quality_score=0.65
    ungrounded_rate=0.08
    safety_block_rate=0.03
    injection_risk_rate=0.01
    token_abuse_rate=0.005
    timeout_rate=0.01
    latency_trend="increasing"
    cost_trend="increasing"
    error_trend="stable"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/insights" -Method POST -ContentType "application/json" -Body $body
```

## Step 6: Verify Datadog Integration

### Check Metrics in Datadog

1. **Metrics Explorer:**
   - Go to https://app.datadoghq.com/metric/explorer
   - Search for: `llm.request.latency_ms`
   - Search for: `llm.cost.usd`
   - Search for: `llm.tokens.input`

2. **APM Traces:**
   - Go to https://app.datadoghq.com/apm/traces
   - Filter by: `service:llm-reliability-control-plane`
   - You should see traces for `/qa`, `/reason`, `/stress`, `/insights`

3. **Logs:**
   - Go to https://app.datadoghq.com/logs
   - Filter by: `service:llm-reliability-control-plane`
   - You should see structured JSON logs

4. **Dashboard:**
   - Open your imported dashboard
   - Metrics should populate as you make API calls

## Step 7: Test Monitor Triggers

### Trigger Latency Monitor
```powershell
# Make multiple requests with latency simulation
1..20 | ForEach-Object {
    $body = @{question="test"; document="test"} | ConvertTo-Json
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/qa?simulate_latency=true" -Method POST -ContentType "application/json" -Body $body
    Start-Sleep -Seconds 1
}
```

### Trigger Cost Anomaly Monitor
```powershell
# Make requests with high token usage
1..30 | ForEach-Object {
    $body = @{question="test"; document="test"} | ConvertTo-Json
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/stress?repetitions=10" -Method POST -ContentType "application/json" -Body $body
    Start-Sleep -Seconds 1
}
```

## Step 8: Configure Incident Rules (Optional but Recommended)

1. Go to **Incidents** → **Settings** → **Rules**
2. Create incident rule:
   - **Trigger**: Monitor alert with tag `critical`
   - **Actions**: 
     - Create incident
     - Attach dashboard: "LLM Reliability Control Plane"
     - Attach logs: `service:llm-reliability-control-plane`
     - Attach traces: `service:llm-reliability-control-plane`

## Troubleshooting

### Metrics Not Appearing
- **Without Datadog Agent:** Metrics will still be logged to console (check application logs)
- **With Datadog Agent:** Ensure agent is running and `DD_AGENT_HOST` is correct
- **Direct API:** Metrics can be sent directly to Datadog API (configured in `telemetry.py`)

### Traces Not Appearing
- Ensure `DD_TRACE_ENABLED=true`
- Check that `ddtrace` package is installed (optional - app works without it)
- Verify `DD_AGENT_HOST` and `DD_TRACE_AGENT_PORT` are correct

### 403 Forbidden on Import
- Verify Application Key has proper permissions
- Use UI import method instead
- Check API key and App key are correct

## Quick Start Commands (Copy-Paste Ready)

```powershell
# 1. Navigate and activate venv
cd "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
.\venv\bin\Activate.ps1

# 2. Set environment variables
$env:LRCP_DATADOG_API_KEY = "765bcbbb809c7cedda7e316fd2337d9c"
$env:DD_APP_KEY = "b9043f0e53a84f0b96b82b568a9ec5ee1bbeb28a"
$env:DD_SITE = "datadoghq.com"
$env:DD_AGENT_HOST = "localhost"
$env:DD_TRACE_ENABLED = "true"
$env:DD_LOGS_ENABLED = "true"

# 3. Start application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. In another terminal, test the API
$body = @{question="What is Datadog?"; document="Datadog is an observability platform."} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/qa" -Method POST -ContentType "application/json" -Body $body
```

## Success Criteria

✅ Application starts without errors  
✅ API endpoints respond correctly  
✅ Metrics appear in Datadog (or console logs)  
✅ Dashboard shows data  
✅ Monitors are evaluating  
✅ Logs are structured and searchable  

## Next Steps

1. Import Datadog resources via UI
2. Start the application
3. Make test API calls
4. Verify metrics in Datadog
5. Test monitor triggers
6. Configure incident rules (optional)

Your project is ready to run end-to-end! 🚀

