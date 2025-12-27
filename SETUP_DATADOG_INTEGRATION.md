# 🚀 Datadog Integration Setup Guide

Complete step-by-step guide to import and configure all Datadog resources for the LLM Reliability Control Plane.

---

## 📋 Prerequisites

1. **Datadog Account**: Active Datadog trial or account
2. **API Keys**: 
   - `DD_API_KEY` - Datadog API key
   - `DD_APP_KEY` - Datadog Application key
3. **Datadog Agent**: Running on your host (optional but recommended)

---

## 1. Import Workflows (Workflow Automation)

### Via Datadog UI:

1. Navigate to **Workflow Automation** → **New Workflow**
2. Click **Import JSON**
3. Select file: `datadog/workflows.json`
4. **Replace placeholders:**
   - `{{APP_URL}}` → Your deployed application URL (e.g., `https://your-app.run.app`)
5. **Review and update:**
   - API endpoints in workflow steps
   - Notification channels (Slack, email)
6. **Publish** each workflow

### Workflows Included:

1. **Auto-Remediate Cost Spike with Auto-Scale Down**
   - Switches to lower-cost model
   - Scales down non-critical workloads
   - Creates incident
   - Notifies team

2. **Auto-Remediate Latency Spike**
   - Enables response caching
   - Scales up cache infrastructure
   - Creates incident

3. **Auto-Remediate Quality Degradation**
   - Switches to higher-quality model
   - Enables quality-based routing
   - Creates incident

4. **Runbook Execution: Error Burst**
   - Checks Vertex AI status
   - Verifies authentication
   - Creates incident with runbook
   - Pages on-call

### Verification:

- Go to **Workflow Automation** → **Workflows**
- Verify all 4 workflows are listed and enabled
- Test by triggering a monitor manually

---

## 2. Configure On-Call

### Via Datadog UI:

1. Navigate to **On-Call** → **Settings**

2. **Import Escalation Policies:**
   - Go to **Escalation Policies** → **New Policy** → **Import JSON**
   - Select file: `datadog/oncall.json`
   - Extract escalation policies section
   - **Update:**
     - Email addresses
     - Slack channel names
     - PagerDuty integration (if used)

3. **Create On-Call Schedules:**
   - Go to **On-Call** → **Schedules** → **New Schedule**
   - **Update:**
     - User email addresses
     - Rotation type (weekly/daily)
     - Start date/time
     - Timezone

4. **Configure On-Call Rules:**
   - Go to **On-Call** → **Rules** → **New Rule**
   - Create rules for:
     - Auto-page on critical error
     - Notify cost team on budget alert

### Configuration Details:

**Escalation Policies:**
- `LLM Critical Errors`: Slack → Email → PagerDuty
- `LLM Cost Alerts`: Slack → Email
- `LLM Quality Degradation`: Slack only

**On-Call Schedules:**
- `Primary LLM On-Call`: Weekly rotation
- `LLM Cost Team On-Call`: Daily rotation

**On-Call Rules:**
- Auto-page on `LLM Error Burst / Retry Storm` (SEV-1)
- Notify on `LLM Daily Cost Budget Alert`

### Verification:

- Go to **On-Call** → **Schedules**
- Verify schedules are active with correct users
- Test by triggering a monitor that should page

---

## 3. Set Up Log Pipelines

### Via Datadog UI:

1. Navigate to **Logs** → **Configuration** → **Pipelines**

2. **Import Each Pipeline:**
   - Click **New Pipeline** → **Import JSON**
   - For each pipeline in `datadog/log_pipelines.json`:
     - LLM Request Logs Pipeline
     - LLM Error Logs Pipeline
     - LLM Cost Logs Pipeline
     - LLM Security Logs Pipeline

3. **Configure Pipeline Order:**
   - Drag pipelines to set processing order
   - Request Logs → Error Logs → Cost Logs → Security Logs

4. **Set Up Archive Configurations:**
   - Go to **Logs** → **Configuration** → **Archives**
   - Create archives:
     - LLM Logs Archive (30-day retention)
     - LLM Error Logs Archive (90-day retention)

### Pipeline Details:

**LLM Request Logs Pipeline:**
- Filters: `service:llm-reliability-control-plane source:python`
- Processors: Trace ID remapping, Grok parsing, categorization, enrichment

**LLM Error Logs Pipeline:**
- Filters: `service:llm-reliability-control-plane status:error`
- Processors: Error classification, severity mapping

**LLM Cost Logs Pipeline:**
- Filters: `service:llm-reliability-control-plane cost_usd:*`
- Processors: Cost calculation, timestamp parsing

**LLM Security Logs Pipeline:**
- Filters: `service:llm-reliability-control-plane security:* OR safety_block:true`
- Processors: Data redaction, security event classification

### Verification:

- Go to **Logs** → **Explorer**
- Verify logs are being processed and enriched
- Check that tags are correctly applied
- Verify redaction is working for security logs

---

## 4. Import Monitors

### Via Datadog UI:

1. Navigate to **Monitors** → **New Monitor**

2. **Import Basic Monitors:**
   - Click **Import JSON**
   - Select file: `datadog/monitors.json`
   - Review each monitor configuration
   - **Save** all monitors

3. **Import Advanced Monitors:**
   - Click **Import JSON**
   - Select file: `datadog/monitors_advanced.json`
   - Review advanced monitor types:
     - Composite monitor (health score + multiple dimensions)
     - Predictive monitor (cost forecast)
     - Workflow trigger monitors
   - **Save** all monitors

4. **Configure Alert Groups:**
   - Go to **Monitors** → **Alert Groups**
   - Create alert groups from `monitors_advanced.json`:
     - LLM Multi-Dimension Failure Group
     - LLM Cost and Quality Correlation Group

### Monitor Types:

**Basic Monitors (7):**
- Latency SLO Burn
- Cost Anomaly Detection
- Error Burst / Retry Storm
- Quality Degradation
- Safety Block Surge
- Health Score Degradation
- Daily Cost Budget Alert

**Advanced Monitors (4):**
- Composite: Health Score + Multiple Dimensions
- Predictive: Cost Spike Forecast
- Workflow Trigger: Latency SLO Breach
- Workflow Trigger: Cost Spike

### Verification:

- Go to **Monitors** → **Manage Monitors**
- Verify all monitors are listed and enabled
- Check monitor evaluation status
- Test by triggering a monitor manually

---

## 5. Import Dashboard

### Via Datadog UI:

1. Navigate to **Dashboards** → **New Dashboard**

2. **Import Dashboard:**
   - Click **Import JSON**
   - Select file: `datadog/dashboard.json`
   - **Update:**
     - `{{SLO_ID}}` → Your SLO ID (from step 6)
     - Dashboard name (if desired)

3. **Verify Widgets:**
   - Service Map widget (ID 16)
   - LLM Observability native widgets (ID 17, 18)
   - SLO burn widget (ID 19)
   - Predictive forecast widget (ID 20)
   - Monitor status grid (ID 21)

### Dashboard Features:

- **17+ widgets** including:
  - Latency, error, cost, quality metrics
  - Security signals
  - Health score
  - Service Map
  - LLM Observability native widgets
  - SLO burn widget
  - Predictive forecasts
  - Monitor status grid

### Verification:

- Open dashboard and verify all widgets are loading
- Check that metrics are appearing
- Verify Service Map shows dependencies
- Test template variables (service, env)

---

## 6. Import SLO

### Via Datadog UI:

1. Navigate to **Service Management** → **SLOs** → **New SLO**

2. **Import SLO:**
   - Click **Import JSON**
   - Select file: `datadog/slo.json`
   - Review configuration:
     - Target: 99% uptime
     - Time window: 30 days
     - Metric: p95 latency < 1500ms

3. **Note the SLO ID:**
   - Copy the SLO ID from the SLO details page
   - Update dashboard JSON: Replace `{{SLO_ID}}` in `datadog/dashboard.json`

### Verification:

- Go to **Service Management** → **SLOs**
- Verify SLO is tracking correctly
- Check SLO burn widget in dashboard

---

## 7. Import Synthetics Tests

### Via Datadog UI:

1. Navigate to **Synthetics** → **New Test**

2. **Import Each Test:**
   - Click **Import JSON**
   - For each test in `datadog/synthetics.json`:
     - LLM API Health Check
     - LLM QA Endpoint Test
     - LLM Insights Endpoint Test
     - LLM API Latency Test
   - **Replace:**
     - `{{APP_URL}}` → Your deployed application URL

### Verification:

- Go to **Synthetics** → **Tests**
- Verify all tests are running
- Check test results
- Verify locations are correct

---

## 8. Verify Service Map

### Automatic Generation:

Service Map is automatically generated from traces. Verify:

1. **Service Tags:**
   - Ensure service is tagged: `service:llm-reliability-control-plane`
   - Environment tags: `env:production`, `env:staging`, `env:local`

2. **Trace Propagation:**
   - Verify traces are being collected
   - Check APM → Service Map
   - Verify dependencies are shown

3. **Dashboard Widget:**
   - Check Service Map widget in dashboard (ID 16)
   - Verify it shows LLM service and dependencies

---

## 9. Configure Environment Variables

### Application Environment Variables:

```bash
# Datadog Configuration
export DD_API_KEY="your-datadog-api-key"
export DD_APP_KEY="your-datadog-app-key"
export DD_SITE="datadoghq.com"  # or datadoghq.eu, us3.datadoghq.com
export DD_AGENT_HOST="localhost"  # or your agent hostname
export DD_DOGSTATSD_PORT="8125"
export DD_TRACE_AGENT_PORT="8126"

# Enable Features
export DD_TRACE_ENABLED="true"
export DD_LOGS_ENABLED="true"

# Service Metadata
export DD_SERVICE="llm-reliability-control-plane"
export DD_ENV="production"  # or staging, local
export DD_VERSION="0.1.0"

# LLM Observability
export DD_LLMOBS_AGENTLESS_ENABLED="1"
export DD_LLMOBS_ML_APP="llm-reliability-control-plane"
```

---

## 10. Verification Checklist

### ✅ All Components:

- [ ] Workflows imported and enabled (4 workflows)
- [ ] On-Call schedules created and active
- [ ] Escalation policies configured
- [ ] Log pipelines processing logs (4 pipelines)
- [ ] Archive configurations set up (2 archives)
- [ ] Basic monitors imported (7 monitors)
- [ ] Advanced monitors imported (4 monitors)
- [ ] Alert groups configured (2 groups)
- [ ] Dashboard imported and widgets loading
- [ ] SLO imported and tracking
- [ ] Synthetics tests running (4 tests)
- [ ] Service Map showing dependencies
- [ ] Environment variables configured
- [ ] Application sending telemetry to Datadog

### ✅ Test Scenarios:

- [ ] Trigger a monitor and verify workflow executes
- [ ] Trigger critical error and verify on-call pages
- [ ] Check logs are being processed by pipelines
- [ ] Verify Service Map shows in dashboard
- [ ] Check LLM Observability metrics are appearing
- [ ] Test predictive monitor (cost forecast)
- [ ] Verify composite monitor triggers correctly

---

## 🔧 Troubleshooting

### Workflows Not Triggering:

1. Check monitor is enabled and evaluating
2. Verify workflow is enabled
3. Check workflow trigger conditions match monitor name
4. Review workflow execution logs

### Service Map Not Showing:

1. Verify service tags are correct
2. Check traces are being sent to Datadog
3. Ensure APM is enabled (`DD_TRACE_ENABLED=true`)
4. Check Datadog Agent is running

### Logs Not Processing:

1. Verify pipelines are enabled
2. Check pipeline filters match log tags
3. Review pipeline processing order
4. Check for pipeline errors in logs

### Monitors Not Evaluating:

1. Verify metrics exist in Metrics Explorer
2. Check monitor query syntax
3. Ensure evaluation window has data
4. Review monitor status in UI

---

## 📚 Additional Resources

- [Datadog Workflow Automation Docs](https://docs.datadoghq.com/workflow_automation/)
- [Datadog On-Call Docs](https://docs.datadoghq.com/on_call/)
- [Datadog Log Pipelines Docs](https://docs.datadoghq.com/logs/processing/pipelines/)
- [Datadog LLM Observability Docs](https://docs.datadoghq.com/llm_observability/)
- [Datadog Service Map Docs](https://docs.datadoghq.com/infrastructure/service_map/)

---

**🎉 Setup Complete!** Your LLM Reliability Control Plane is now fully integrated with Datadog's comprehensive observability platform.

