# 📊 Datadog Import Guide - Step-by-Step Instructions

This guide provides exact steps to import all Datadog configurations (monitors, dashboards, SLOs, workflows, on-call, log pipelines) into your Datadog organization.

## 📋 Prerequisites

1. **Datadog Account** with Admin access
2. **Datadog API Key** and **Application Key**
3. **Python 3.9+** (for import script)
4. **All JSON files** in the `datadog/` folder

## 🔑 Step 1: Get Your Datadog API Keys

1. **Log in to Datadog**: https://app.datadoghq.com (or your site: datadoghq.eu, us3.datadoghq.com, etc.)

2. **Get API Key**:
   - Go to: **Organization Settings** → **API Keys**
   - Click **New Key**
   - Name it: `LLM-Reliability-Control-Plane`
   - Copy the key (you'll only see it once!)

3. **Get Application Key**:
   - Go to: **Organization Settings** → **Application Keys**
   - Click **New Key**
   - Name it: `LLM-Reliability-Control-Plane`
   - Copy the key (you'll only see it once!)

4. **Set Environment Variables**:
```bash
# Windows PowerShell
$env:DD_API_KEY = "your-api-key-here"
$env:DD_APP_KEY = "your-app-key-here"
$env:DD_SITE = "datadoghq.com"  # or datadoghq.eu, us3.datadoghq.com

# Linux/macOS
export DD_API_KEY="your-api-key-here"
export DD_APP_KEY="your-app-key-here"
export DD_SITE="datadoghq.com"
```

## 📥 Step 2: Import Monitors

### Option A: Using Datadog UI

1. **Navigate to Monitors**:
   - Go to: **Monitors** → **New Monitor** → **Import from JSON**

2. **Import Basic Monitors** (`datadog/monitors.json`):
   - Click **Import from JSON**
   - Copy contents of `datadog/monitors.json`
   - **7 monitors** (latency SLO, cost anomaly, error burst, quality degradation, safety blocks, health score, daily cost budget)

3. **Import ML-Based Anomaly Monitors** (`datadog/monitors_anomaly.json`):
   - Click **New Monitor** → **Import from JSON**
   - Copy contents of `datadog/monitors_anomaly.json`
   - **3 monitors** (ML-based cost, latency, and quality anomaly detection)

4. **Import Advanced Monitors** (`datadog/monitors_advanced.json`):
   - Click **New Monitor** → **Import from JSON**
   - Copy contents of `datadog/monitors_advanced.json`
   - **4 monitors** (composite, predictive, workflow triggers) + multi-alert grouping

5. **Import AI Engineer Critical Monitors** (`datadog/monitors_ai_engineer_critical.json`):
   - Click **New Monitor** → **Import from JSON**
   - Copy contents of `datadog/monitors_ai_engineer_critical.json`
   - **11 monitors** (token usage explosion, hallucination detection, context window exhaustion, rate limiting, response consistency, cost efficiency, prompt injection, model switching, availability, processing time, output truncation)
   - Paste into the import dialog
   - Click **Import**
   - **Repeat for each monitor** (if JSON contains array)

3. **Import Anomaly Monitors** (`datadog/monitors_anomaly.json`):
   - Same process as above

4. **Import Advanced Monitors** (`datadog/monitors_advanced.json`):
   - Same process as above

### Option B: Using Python Script

```bash
# Install required packages
pip install datadog-api-client

# Run import script
python scripts/import_datadog_resources.py --resource monitors --file datadog/monitors.json
python scripts/import_datadog_resources.py --resource monitors --file datadog/monitors_anomaly.json
python scripts/import_datadog_resources.py --resource monitors --file datadog/monitors_advanced.json
```

### Option C: Using Datadog API Directly

```bash
# For each monitor in monitors.json, use curl:
curl -X POST "https://api.datadoghq.com/api/v1/monitor" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @datadog/monitors.json
```

## 📊 Step 3: Import Dashboard

### Using Datadog UI

1. **Navigate to Dashboards**:
   - Go to: **Dashboards** → **New Dashboard** → **Import Dashboard JSON**

2. **Import Main Dashboard** (`datadog/dashboard.json`):
   - Click **Import Dashboard JSON**
   - Copy contents of `datadog/dashboard.json`
   - Paste into the import dialog
   - Click **Import**
   - **Note**: You may need to update widget queries to match your metric names

3. **Import Enhanced Dashboard** (`datadog/dashboard_enhanced.json`):
   - Same process as above

4. **Import Advanced Dashboard** (`datadog/dashboard_enhanced.json`):
   - Same process as above (if you have an enhanced version)

### Using Datadog API

```bash
curl -X POST "https://api.datadoghq.com/api/v1/dashboard" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @datadog/dashboard.json
```

## 🎯 Step 4: Import SLOs

### Using Datadog UI

1. **Navigate to SLOs**:
   - Go to: **Service Management** → **SLOs** → **New SLO**

2. **Import SLO** (`datadog/slo.json`):
   - Click **Import from JSON** (if available)
   - Or manually create SLO using the JSON as reference:
     - **Name**: From JSON `name` field
     - **Type**: From JSON `type` field
     - **Target**: From JSON `target_threshold` field
     - **Time Window**: From JSON `timeframe` field
     - **Metric Query**: From JSON `query` field

### Using Datadog API

```bash
curl -X POST "https://api.datadoghq.com/api/v1/slo" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @datadog/slo.json
```

## 🔄 Step 5: Import Workflows (Workflow Automation)

**Note**: Datadog Workflow Automation may require UI configuration. JSON import may not be available via API.

### Using Datadog UI

1. **Navigate to Workflows**:
   - Go to: **Workflow Automation** → **Workflows** → **New Workflow**

2. **Create Workflow Manually**:
   - For each workflow in `datadog/workflows.json`:
     - Click **New Workflow**
     - **Name**: Use `name` from JSON
     - **Trigger**: Configure based on `triggers` in JSON
       - Select **Monitor Alert** trigger
       - Choose the monitor name from `monitor_name`
     - **Steps**: Add steps based on `steps` array:
       - **Step 1**: Log action (if `type: "log"`)
       - **Step 2**: API call (if `type: "api"`)
         - **URL**: Replace `{{APP_URL}}` with your actual Cloud Run URL
       - **Step 3**: Create incident (if `type: "incident"`)
       - **Step 4**: Send notification (if `type: "notification"`)

3. **Important Placeholders to Replace**:
   - `{{APP_URL}}`: Replace with your Cloud Run service URL
   - Example: `https://llm-reliability-control-plane-xxxxx-uc.a.run.app`

### Using Datadog API (if available)

```bash
# Check if Workflow API is available in your Datadog plan
curl -X GET "https://api.datadoghq.com/api/v1/workflow" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}"
```

## 📞 Step 6: Configure On-Call

**Note**: Datadog On-Call requires UI configuration. JSON is for reference only.

### Using Datadog UI

1. **Navigate to On-Call**:
   - Go to: **On-Call** → **Settings**

2. **Create Escalation Policies** (`datadog/oncall.json` → `escalation_policies`):
   - For each policy:
     - Click **New Escalation Policy**
     - **Name**: Use `name` from JSON
     - **Steps**: Add steps based on `steps` array:
       - Configure notification channels (Slack, Email, PagerDuty)
       - Set timeout minutes
     - **Important**: Update email addresses, Slack channels, PagerDuty integration IDs

3. **Create On-Call Schedules** (`datadog/oncall.json` → `schedules`):
   - Click **New Schedule**
   - **Name**: Use `name` from JSON
   - **Users**: Add team members
   - **Rotation**: Configure based on `rotation` in JSON

4. **Create Auto-Paging Rules** (`datadog/oncall.json` → `auto_paging_rules`):
   - Click **New Auto-Paging Rule**
   - **Trigger**: Select monitor from `trigger.monitor_name`
   - **Action**: Select schedule and escalation policy
   - **Message**: Use `action.message` from JSON

### Placeholders to Update:
- `"oncall@example.com"` → Your actual on-call email
- `"#llm-alerts"` → Your actual Slack channel
- PagerDuty integration IDs → Your actual PagerDuty service IDs

## 📝 Step 7: Configure Log Pipelines

### Using Datadog UI

1. **Navigate to Log Pipelines**:
   - Go to: **Logs** → **Configuration** → **Pipelines**

2. **Create Pipeline** (`datadog/log_pipelines.json`):
   - For each pipeline:
     - Click **New Pipeline**
     - **Name**: Use `name` from JSON
     - **Filter**: Add filter based on `filter.query` in JSON
     - **Processors**: Add processors based on `processors` array:
       - **Grok Parser**: For parsing log format
       - **Attribute Remapper**: For remapping attributes
       - **URL Parser**: For parsing URLs
       - **User-Agent Parser**: For parsing user agents
     - **Enrichment**: Add enrichment tables if specified
     - **Redaction**: Add redaction rules if specified

3. **Configure Archives** (if specified in JSON):
   - Go to: **Logs** → **Configuration** → **Archives**
   - Create archive with retention period from JSON

### Using Datadog API

```bash
curl -X POST "https://api.datadoghq.com/api/v1/logs/config/pipelines" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @datadog/log_pipelines.json
```

## 📓 Step 8: Import Notebooks (Optional)

### Using Datadog UI

1. **Navigate to Notebooks**:
   - Go to: **Notebooks** → **New Notebook**

2. **Import Notebook**:
   - For `datadog/notebooks/root_cause_analysis.json`:
     - Click **Import from JSON** (if available)
     - Or manually recreate using JSON as reference
   - For `datadog/notebooks/cost_optimization.json`:
     - Same process

## ✅ Step 9: Verify Imports

### Verify Monitors
1. Go to: **Monitors** → **Manage Monitors**
2. Search for: `llm` or `LLM`
3. Verify all monitors are present and evaluating

### Verify Dashboard
1. Go to: **Dashboards** → **Dashboard List**
2. Find: **LLM Reliability Control Plane**
3. Open dashboard and verify widgets are showing data

### Verify SLOs
1. Go to: **Service Management** → **SLOs**
2. Verify SLO is present and calculating

### Verify Workflows
1. Go to: **Workflow Automation** → **Workflows**
2. Verify workflows are created and enabled

### Verify On-Call
1. Go to: **On-Call** → **Schedules**
2. Verify schedules are configured
3. Go to: **On-Call** → **Escalation Policies**
4. Verify policies are created

### Verify Log Pipelines
1. Go to: **Logs** → **Configuration** → **Pipelines**
2. Verify pipelines are processing logs

## 🔧 Step 10: Update Placeholders

After importing, update these placeholders in Datadog:

### In Workflows:
- `{{APP_URL}}` → Your Cloud Run URL
  - Example: `https://llm-reliability-control-plane-xxxxx-uc.a.run.app`

### In On-Call:
- `"oncall@example.com"` → Your actual email
- `"#llm-alerts"` → Your actual Slack channel
- PagerDuty service IDs → Your actual IDs

### In Monitors:
- Verify metric names match your actual metrics
- Update thresholds if needed
- Update notification channels

### In Dashboard:
- Verify metric queries match your metrics
- Update service names if different
- Update environment tags

## 🐛 Troubleshooting

### Monitors not evaluating
- Check metric names exist: **Metrics** → **Metrics Explorer**
- Verify monitor queries are correct
- Check evaluation window has data

### Dashboard shows "No Data"
- Verify metrics are being sent from application
- Check time range in dashboard
- Verify service tags match

### Workflows not triggering
- Verify monitors are triggering
- Check workflow trigger configuration
- Verify `{{APP_URL}}` is replaced with actual URL

### On-Call not paging
- Verify escalation policies are configured
- Check notification channels are connected
- Verify auto-paging rules are enabled

## 📝 Quick Import Script

Create a file `import_all.sh`:

```bash
#!/bin/bash
set -e

export DD_API_KEY="your-api-key"
export DD_APP_KEY="your-app-key"
export DD_SITE="datadoghq.com"

# Import monitors
echo "Importing monitors..."
python scripts/import_datadog_resources.py --resource monitors --file datadog/monitors.json

# Import dashboard
echo "Importing dashboard..."
curl -X POST "https://api.${DD_SITE}/api/v1/dashboard" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @datadog/dashboard.json

# Import SLO
echo "Importing SLO..."
curl -X POST "https://api.${DD_SITE}/api/v1/slo" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @datadog/slo.json

echo "✅ Import complete! Please configure Workflows and On-Call manually in UI."
```

---

**🎉 Import Complete!** All Datadog resources should now be configured.

**Next Steps**:
1. Update placeholders (APP_URL, emails, channels)
2. Test monitors by triggering them
3. Verify dashboard shows data
4. Test workflow automation
5. Test on-call paging

