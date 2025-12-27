# Datadog Incident Creation Guide

This guide explains how to configure Datadog to automatically create incidents when monitors trigger, with full context attached.

## Overview

Our monitors are configured to create actionable incidents, but Datadog requires **Incident Rules** to be set up in the UI. The `incident_config` in `monitors.json` is documentation - actual incident creation happens via Datadog's Incident Management feature.

## Step 1: Import Monitors

First, import the monitors from `datadog/monitors.json`:

1. Go to **Monitors** → **New Monitor**
2. For each monitor in the JSON:
   - Click **Import** or use JSON editor
   - Paste monitor definition (remove `incident_config` field - it's not part of Datadog API)
   - Save monitor

Or use the import script:
```bash
python scripts/import_datadog_resources.py
```

## Step 2: Configure Incident Rules

Incident Rules automatically create incidents when monitors trigger. Configure them in Datadog UI:

### Navigate to Incident Rules

1. Go to **Incidents** → **Settings** → **Rules**
2. Click **New Rule**

### Create Rule for Critical Monitors

**Rule Name**: `LLM Critical Alerts → Incident`

**Conditions**:
- **Trigger**: Monitor alert
- **Tags**: `llm` AND `critical`
- **Severity**: Any

**Actions**:
- **Create Incident**: Yes
- **Severity**: Use monitor severity (SEV-1, SEV-2, SEV-3)
- **Title**: `{monitor_name} - {alert_message}`
- **Description**: Include monitor message (runbook)

**Attachments**:
- **Dashboard**: "LLM Reliability Control Plane"
- **Logs Query**: `service:llm-reliability-control-plane`
- **Traces Query**: `service:llm-reliability-control-plane` (for latency/error incidents)

### Create Rule for All LLM Monitors

**Rule Name**: `LLM Alerts → Incident`

**Conditions**:
- **Trigger**: Monitor alert
- **Tags**: `llm`

**Actions**:
- **Create Incident**: Yes
- **Severity**: Based on monitor tag (`critical` = SEV-1/SEV-2, others = SEV-3)
- **Attachments**: Dashboard and logs

## Step 3: Test Incident Creation

### Method 1: Trigger via Traffic Generator

1. Start the API:
```bash
uvicorn app.main:app --reload
```

2. Run traffic generator with failure scenarios:
```bash
python traffic-generator/generate_load.py
```

3. The generator will:
   - Phase 1: Normal traffic
   - Phase 2: Cost spike (long prompts) → May trigger cost anomaly monitor
   - Phase 3: Quality drop (bad prompts) → May trigger quality/safety monitors
   - Phase 4: Latency spike → Will trigger latency monitor

### Method 2: Manual Trigger

Trigger latency monitor intentionally:

```bash
# Send multiple requests with latency simulation
for i in {1..20}; do
  curl -X POST "http://localhost:8000/qa?simulate_latency=true" \
    -H "Content-Type: application/json" \
    -d '{"question": "test", "document": "test"}'
  sleep 1
done
```

This will:
1. Generate high latency metrics
2. Trigger "LLM p95 Latency SLO Burn" monitor
3. Create incident via Incident Rule
4. Attach dashboard, logs, and traces

## Step 4: Verify Incident Creation

1. Go to **Incidents** in Datadog
2. You should see a new incident with:
   - **Title**: Monitor name + alert message
   - **Severity**: SEV-1, SEV-2, or SEV-3
   - **Status**: Active
   - **Attachments**:
     - Dashboard: "LLM Reliability Control Plane"
     - Logs: Filtered by service
     - Traces: (if configured)

3. Click into the incident to see:
   - Full runbook in description
   - Attached dashboard showing metrics
   - Relevant logs with context
   - Traces (for latency/error incidents)

## Step 5: Capture Evidence

For submission, capture screenshots of:

### 1. Monitor Alert
- Go to **Monitors** → Find triggered monitor
- Screenshot showing:
  - Monitor name
  - Alert status
  - Query and threshold
  - Timeframe

### 2. Incident Creation
- Go to **Incidents** → Open incident
- Screenshot showing:
  - Incident title and severity
  - Description with runbook
  - Attached resources (dashboard, logs, traces)
  - Timeline showing creation time

### 3. Incident Context
- Within incident, screenshot:
  - Attached dashboard (showing metrics)
  - Logs panel (showing relevant logs)
  - Traces panel (if available)

### 4. Dashboard During Incident
- Go to **Dashboards** → "LLM Reliability Control Plane"
- Screenshot showing:
  - Triggered monitor status
  - Metrics showing the issue
  - Timeframe of incident

## Example Incident Flow

1. **Trigger**: Traffic generator sends requests with `simulate_latency=true`
2. **Metric**: `llm.request.latency_ms` exceeds 1500ms p95
3. **Monitor**: "LLM p95 Latency SLO Burn" triggers
4. **Incident Rule**: Matches tag `llm` AND `critical`
5. **Incident Created**: 
   - Title: "LLM p95 Latency SLO Burn - p95 latency is breaching SLO threshold"
   - Severity: SEV-2
   - Description: Full runbook (What failed? Why? What next?)
   - Attachments: Dashboard, logs, traces
6. **Engineer Action**: Follows runbook steps from incident description

## Troubleshooting

### Incidents Not Creating

1. **Check Incident Rules**: Verify rules are active and match monitor tags
2. **Check Monitor Tags**: Ensure monitors have `llm` tag (and `critical` for critical rules)
3. **Check Monitor Status**: Verify monitor actually triggered (not just warning)
4. **Check Permissions**: Ensure you have Incident Management permissions

### Missing Attachments

1. **Dashboard**: Verify dashboard name matches exactly in Incident Rule
2. **Logs**: Check log query syntax and ensure logs are flowing
3. **Traces**: Verify APM is enabled and traces are being collected

### Monitor Not Triggering

1. **Check Metrics**: Verify metrics are flowing to Datadog (Metrics Explorer)
2. **Check Query**: Verify monitor query matches metric names exactly
3. **Check Threshold**: Ensure threshold is realistic (test with traffic generator)

## Advanced: Custom Incident Fields

You can enhance incidents with custom fields:

1. Go to **Incidents** → **Settings** → **Fields**
2. Add custom fields:
   - **Endpoint**: Which endpoint triggered the issue
   - **Model**: Which model was affected
   - **Request Type**: Type of request (qa, reason, stress)
3. Update Incident Rules to populate these fields from monitor tags

## Summary

- Monitors trigger based on metrics
- Incident Rules create incidents automatically
- Incidents include full context (dashboard, logs, traces)
- Runbooks are in monitor messages (visible in incidents)
- All configured to answer: What failed? Why? What next?




