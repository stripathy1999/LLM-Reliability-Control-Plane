# 🎬 Demo Script - Step-by-Step Guide

This script provides exact commands and steps to demonstrate the LLM Reliability Control Plane for the Datadog hackathon submission.

---

## 📋 Pre-Demo Setup

### 1. Start Backend
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
# OR
source venv/bin/activate  # Linux/macOS

# Set environment variables
$env:LRCP_GEMINI_API_KEY = "your-gemini-api-key"
$env:LRCP_DATADOG_API_KEY = "your-datadog-api-key"
$env:DD_APP_KEY = "your-datadog-app-key"

# Start server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2. Start Frontend (Optional)
```bash
cd failure-theater
npm install  # First time only
npm run dev
```

**Expected Output:**
```
- ready started server on 0.0.0.0:3000
```

### 3. Validate Setup
```bash
python scripts/validate_setup.py
```

**Expected Output:**
```
✓ All critical checks passed! Ready for demo.
```

---

## 🎯 Demo Flow

### **Part 1: Show Healthy State**

#### Step 1.1: Open Swagger UI
- Navigate to: http://127.0.0.1:8000/docs
- **Say**: "This is our API documentation. All endpoints are working."

#### Step 1.2: Check Health Endpoint
```bash
curl http://127.0.0.1:8000/health
```

**Expected Response:**
```json
{"status": "healthy", "version": "0.1.0"}
```

#### Step 1.3: Show Datadog Dashboard
- Open Datadog → Dashboards → "LLM Reliability Control Plane"
- **Say**: "Here's our comprehensive dashboard. Health score is 85, all monitors are green."

**What to Show:**
- Health score widget (85)
- All monitors: green/OK
- Metrics: normal ranges
- No active incidents

---

### **Part 2: Trigger Failure Scenario**

#### Step 2.1: Trigger Cost Explosion
**Option A: Via Failure Theater UI**
- Open: http://localhost:3000
- Click: "🔴 Cost Explosion" button
- **Say**: "I'm triggering a cost explosion scenario."

**Option B: Via API**
```bash
curl -X POST "http://127.0.0.1:8000/stress?simulate_long_context=true" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Summarize", "repetitions": 50}'
```

**Repeat 10-20 times to exceed threshold:**
```bash
for i in {1..20}; do
  curl -X POST "http://127.0.0.1:8000/stress?simulate_long_context=true" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Summarize", "repetitions": 50}'
  sleep 1
done
```

#### Step 2.2: Show Monitor Triggering
- Go to Datadog → Monitors
- Find: "LLM Cost Anomaly Detection"
- **Say**: "The cost anomaly monitor has triggered. Health score dropped to 45."

**What to Show:**
- Monitor status: Alert
- Health score: 45 (degraded)
- Cost metrics: spiking
- Monitor message: visible

---

### **Part 3: Show Incident Creation**

#### Step 3.1: Check Incidents
- Go to Datadog → Incidents
- **Say**: "When the monitor triggered, Datadog automatically created an incident."

**What to Show:**
- Incident title: "LLM Cost Anomaly Detection - Cost has spiked..."
- Severity: SEV-3
- Status: Active
- Created: Just now

#### Step 3.2: Show Incident Details
- Click into the incident
- **Say**: "The incident includes a complete runbook that answers: What failed? Why did it fail? And what should the engineer do next?"

**What to Show:**
- Runbook in description (What failed? Why? What next?)
- Attached dashboard
- Attached logs (filtered by service)
- Attached traces (if available)

#### Step 3.3: Show Correlation
- Click "View Logs" in incident
- **Say**: "These logs are automatically correlated via trace IDs. We can see the exact requests that caused the cost spike."

**What to Show:**
- Logs filtered by service
- Trace IDs in logs
- Request details (tokens, cost)

---

### **Part 4: Show Insights and Recommendations**

#### Step 4.1: Call Insights Endpoint
```bash
curl -X POST "http://127.0.0.1:8000/insights" \
  -H "Content-Type: application/json" \
  -d '{
    "avg_latency_ms": 1200.0,
    "error_rate": 0.02,
    "avg_cost_per_request": 0.008,
    "avg_quality_score": 0.65,
    "latency_trend": "increasing",
    "cost_trend": "increasing"
  }'
```

**Expected Response:**
```json
{
  "health_summary": {
    "overall_health_score": 65,
    "component_scores": {...},
    "status": "degraded"
  },
  "recommendations": [...],
  "predictive_insights": [...],
  "priority_actions": [...]
}
```

**Say**: "Our insights endpoint provides AI-powered recommendations. It suggests downgrading to a cheaper model, implementing caching, or adding prompt length limits. It even estimates 30% cost savings."

#### Step 4.2: Show Recommendations
- Highlight specific recommendations in response
- **Say**: "Each recommendation includes specific actions and estimated savings."

**What to Show:**
- Cost optimization recommendations
- Estimated savings
- Predictive insights
- Priority actions

---

### **Part 5: Highlight Innovation Features**

#### Step 5.1: Show ML Anomaly Detection
- Go to Datadog → Monitors
- Find: "LLM Cost Anomaly Detection (ML)"
- **Say**: "We use ML-based anomaly detection, not just thresholds. This adapts to baseline patterns automatically."

**What to Show:**
- Anomaly detection query: `anomalies(...)`
- ML confidence scores
- Adaptive thresholds

#### Step 5.2: Show Custom Spans
- Go to Datadog → APM → Traces
- Filter: `service:llm-reliability-control-plane`
- Click on a trace
- **Say**: "We have custom spans for LLM-specific operations: token counting, cost calculation, quality scoring."

**What to Show:**
- Custom spans: `llm.token_counting`, `llm.cost_calculation`
- LLM-specific tags
- Span breakdown

#### Step 5.3: Show Quality Metrics
- Go to Datadog → Metrics Explorer
- Search: `llm.semantic_similarity_score`
- **Say**: "We track quality metrics like semantic similarity and hallucination detection, not just performance."

**What to Show:**
- Quality metrics
- Security signals
- Cost metrics

#### Step 5.4: Show Predictive Insights
- Call insights endpoint again
- **Say**: "Our ML models predict costs 24 hours ahead with 85% accuracy. We can forecast issues before they happen."

**What to Show:**
- Predictive insights in response
- Forecast timeframes
- Confidence scores

---

## 🎬 Video Recording Tips

### Before Recording:
1. Close unnecessary applications
2. Set screen resolution to 1920x1080
3. Test microphone
4. Prepare all browser tabs
5. Practice script 2-3 times

### During Recording:
1. Speak clearly
2. Pause when showing UI elements
3. Use cursor to highlight
4. Don't rush

### After Recording:
1. Edit out long pauses
2. Add text overlays (optional)
3. Export in 1080p
4. Upload to YouTube/Vimeo

---

## ✅ Verification Checklist

After demo, verify:
- [ ] All endpoints return 200 OK
- [ ] Health score updates correctly
- [ ] Monitors trigger when thresholds exceeded
- [ ] Incidents auto-create
- [ ] Runbooks visible in incidents
- [ ] Logs/traces attached to incidents
- [ ] Insights endpoint returns recommendations
- [ ] ML models provide predictions
- [ ] Dashboard shows all metrics
- [ ] Custom spans visible in APM

---

## 🚨 Troubleshooting

### Monitors Not Triggering
- Verify metrics are flowing: Check Metrics Explorer
- Trigger more requests to exceed threshold
- Check monitor query syntax

### Incidents Not Creating
- Verify Incident Rules are configured
- Check monitor tags match rule conditions
- Verify API keys are set

### Insights Not Working
- Check ML models are trained: `ls models/*.pkl`
- Run training script if needed: `python scripts/train_models.py`
- Verify Gemini API key is set

---

**Ready for Demo!** 🚀

