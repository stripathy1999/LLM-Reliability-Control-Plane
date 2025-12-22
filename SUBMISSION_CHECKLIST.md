# Datadog Hackathon Submission Checklist

## ✅ Implementation Complete

### Phase 1: Architecture & Repo Setup ✓
- [x] Repo structure matches specification
- [x] FastAPI app with 3 endpoints (`/qa`, `/reason`, `/stress`)
- [x] Failure toggles for deterministic incident triggering
- [x] Traffic generator script

### Phase 2: LLM App Design ✓
- [x] FastAPI endpoints implemented
- [x] LLM client with synthetic responses (Vertex AI ready)
- [x] Quality signals computation
- [x] Failure simulation capabilities

### Phase 3: Telemetry Design ✓
- [x] Performance metrics (latency, time-to-first-token, retry count)
- [x] Reliability metrics (errors, timeouts, empty responses, safety blocks)
- [x] Cost metrics (input/output tokens, USD cost)
- [x] Quality metrics (response length, semantic similarity, ungrounded flag)
- [x] Security signals (prompt injection risk, token abuse)

### Phase 4: Datadog Instrumentation ✓
- [x] Datadog APM auto-instrumentation (ddtrace)
- [x] Custom metrics via StatsD
- [x] Structured JSON logging for Datadog ingestion
- [x] Rich tagging (endpoint, model, model_version, request_type)

### Phase 5: Detection Rules (Monitors) ✓
- [x] 5 monitors defined in `datadog/monitors.json`:
  1. LLM p95 Latency SLO Burn
  2. LLM Cost Anomaly Detection
  3. LLM Error Burst / Retry Storm
  4. LLM Quality Degradation
  5. LLM Safety Block Surge
- [x] Each monitor includes actionable runbooks answering:
  - What failed?
  - Why did it fail?
  - What should the engineer do next?

### Phase 6: Incident Management ✓
- [x] Monitor configurations include incident creation settings
- [x] Incident messages include context and runbooks
- [x] Instructions for attaching dashboards, logs, and traces

### Phase 7: Dashboard ✓
- [x] Comprehensive dashboard in `datadog/dashboard.json`
- [x] Golden signals visualization
- [x] SLO status indicators
- [x] Cost and token usage tracking
- [x] Quality metrics visualization
- [x] Security signals section
- [x] Monitor status summary

### Phase 8: Traffic Generator ✓
- [x] Load generation script
- [x] Deterministic failure scenarios:
  - Normal traffic
  - Cost spike (long prompts)
  - Quality drop (bad prompts)
  - Latency + retry spike

### Phase 9: Submission Materials ✓
- [x] README with run instructions
- [x] Datadog setup guide (DATADOG_SETUP.md)
- [x] Datadog JSON exports (monitors, dashboard, SLO)
- [x] Traffic generator script
- [x] Helper script for importing Datadog resources

## 🚀 Pre-Submission Steps

### 1. Deploy Application
- [ ] Deploy to GCP Cloud Run (or preferred hosting)
- [ ] Configure environment variables
- [ ] Verify Datadog agent/integration is active
- [ ] Test endpoints are accessible

### 2. Configure Datadog
- [ ] Import monitors from `datadog/monitors.json`
- [ ] Import dashboard from `datadog/dashboard.json`
- [ ] Import SLO from `datadog/slo.json`
- [ ] Configure incident rules to auto-attach context
- [ ] Verify metrics are flowing (check Metrics Explorer)

### 3. Test End-to-End
- [ ] Run traffic generator to generate metrics
- [ ] Verify metrics appear in Datadog
- [ ] Verify traces appear in APM
- [ ] Verify logs appear in Logs Explorer
- [ ] Trigger a monitor intentionally
- [ ] Verify incident is created with context
- [ ] Verify dashboard shows all signals

### 4. Capture Evidence
- [ ] Screenshot of dashboard showing healthy state
- [ ] Screenshot of dashboard showing incident state
- [ ] Screenshot of monitor configuration
- [ ] Screenshot of incident with attached context
- [ ] Screenshot of APM traces
- [ ] Screenshot of logs with correlation

### 5. Prepare Submission
- [ ] Push code to GitHub repo
- [ ] Update README with hosted URL
- [ ] Document any additional setup steps
- [ ] Prepare demo script/narrative

## 📋 Submission Requirements

### Required Items
1. **Hosted App URL**: Publicly accessible endpoint
2. **Public GitHub Repo**: Link to repository
3. **README**: Run instructions and architecture overview
4. **Datadog JSON Exports**: Monitors, dashboard, SLO
5. **Traffic Generator Script**: Included in repo
6. **Screenshots**: Dashboard, incidents, monitors
7. **Incident Evidence**: Show auto-created incidents with context

### Key Differentiators
- ✅ **Cost observability**: Token and USD tracking
- ✅ **Quality metrics**: Semantic similarity and ungrounded detection
- ✅ **Security signals**: Prompt injection and token abuse detection
- ✅ **Actionable incidents**: Clear runbooks answering judge questions
- ✅ **End-to-end observability**: APM, metrics, logs, incidents

## 🎯 Judge Questions (Always Answerable)

### What failed?
- Dashboard shows monitor status
- Incident title clearly states the failure
- Metrics show the breach

### Why did it fail?
- Tags show endpoint/model/request_type
- Logs show prompt and response context
- Traces show slow spans or errors
- Runbook lists possible causes

### What should the engineer do next?
- Runbook in incident message
- Attached dashboard for investigation
- Attached logs for context
- Attached traces for root cause

## 🔍 Demo Flow

1. **Start**: Show healthy dashboard
2. **Trigger**: Run traffic generator with failure scenarios
3. **Observe**: Show metrics changing in real-time
4. **Alert**: Show monitor triggering
5. **Incident**: Show auto-created incident with context
6. **Investigate**: Use attached dashboard, logs, traces
7. **Resolve**: Follow runbook steps

## 📝 Notes

- All code is production-ready structure
- Synthetic LLM responses for demo (easily swapped for real Vertex AI)
- Comprehensive telemetry covers all judge requirements
- Security observability adds differentiation
- Incident workflow is fully automated

