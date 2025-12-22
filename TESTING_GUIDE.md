# 🧪 Complete Testing Guide

This guide walks you through testing the entire LLM Reliability Control Plane project from start to finish.

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed (for Failure Theater)
- Datadog account (optional for full testing, but recommended)

## Step 1: Setup Backend (FastAPI)

### 1.1 Install Dependencies

```bash
cd LLM-Reliability-Control-Plane
pip install -r requirements.txt
```

### 1.2 Configure Environment (Optional)

Create `.env` file (optional for basic testing):

```bash
# .env
LRCP_DATADOG_API_KEY=your-key-here
DD_AGENT_HOST=localhost
DD_SITE=datadoghq.com
DD_TRACE_ENABLED=true
DD_LOGS_ENABLED=true
```

**Note**: You can test without Datadog - metrics will just log to console.

### 1.3 Start the API

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 1.4 Test Basic Endpoints

Open another terminal and test:

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# API docs
# Open http://localhost:8000/docs in browser
```

**Expected**: All should return 200 OK.

---

## Step 2: Test Individual Endpoints

### 2.1 Test `/qa` Endpoint

```bash
curl -X POST "http://localhost:8000/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Datadog?",
    "document": "Datadog is an observability platform for logs, metrics, and traces."
  }'
```

**Expected**: Returns answer with metadata including prompt_id, quality scores, etc.

### 2.2 Test `/qa` with Failure Toggles

```bash
# Trigger latency
curl -X POST "http://localhost:8000/qa?simulate_latency=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "document": "test"}'

# Trigger retry
curl -X POST "http://localhost:8000/qa?simulate_retry=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "document": "test"}'

# Trigger safety block
curl -X POST "http://localhost:8000/qa?simulate_bad_prompt=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "document": "test"}'
```

**Expected**: Each should return different behavior (higher latency, retry count, safety block).

### 2.3 Test `/reason` Endpoint

```bash
curl -X POST "http://localhost:8000/reason" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain the golden signals of SRE"
  }'
```

**Expected**: Returns reasoning response with metadata.

### 2.4 Test `/stress` Endpoint

```bash
curl -X POST "http://localhost:8000/stress" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Summarize incidents",
    "repetitions": 10
  }'
```

**Expected**: Returns response with higher token counts (due to repetitions).

### 2.5 Test `/insights` Endpoint (AI-Powered)

```bash
curl -X POST "http://localhost:8000/insights" \
  -H "Content-Type: application/json" \
  -d '{
    "avg_latency_ms": 1200,
    "error_rate": 0.02,
    "retry_rate": 0.05,
    "avg_cost_per_request": 0.008,
    "avg_input_tokens": 1500,
    "avg_output_tokens": 200,
    "avg_quality_score": 0.65,
    "ungrounded_rate": 0.08,
    "safety_block_rate": 0.03,
    "injection_risk_rate": 0.01,
    "token_abuse_rate": 0.005,
    "timeout_rate": 0.01,
    "latency_trend": "increasing",
    "cost_trend": "increasing",
    "error_trend": "stable"
  }'
```

**Expected**: Returns health score, recommendations, predictive insights, and priority actions.

---

## Step 3: Test Failure Theater UI

### 3.1 Install Dependencies

```bash
cd failure-theater
npm install
```

### 3.2 Start the UI

```bash
npm run dev
```

You should see:
```
- ready started server on 0.0.0.0:3000
- Local: http://localhost:3000
```

### 3.3 Test the UI

1. Open `http://localhost:3000` in browser
2. You should see:
   - Beautiful gradient UI
   - Health Score: 85 (green)
   - 4 colorful failure buttons
   - Status panel

### 3.4 Test Failure Scenarios

**Test Cost Explosion:**
1. Click the red "🔴 Cost Explosion" button
2. Watch for loading indicator
3. Health score should drop to ~45 (critical)
4. Recommendation should update
5. Incident count should increase

**Test Latency Spike:**
1. Click the orange "🟠 Latency Spike" button
2. Health score should drop to ~55 (degraded)
3. Recommendation should mention latency

**Test Quality Drop:**
1. Click the blue "🔵 Quality Drop" button
2. Health score should drop
3. Recommendation should mention quality

**Test Security Attack:**
1. Click the purple "⚫ Security Attack" button
2. Health score should drop significantly
3. Recommendation should mention security

**Test Reset:**
1. Click "🔄 Reset System" button
2. Health score should return to 85
3. Status should return to healthy

**Expected**: All buttons should work, health scores update, recommendations change.

---

## Step 4: Test Traffic Generator

### 4.1 Run Traffic Generator

```bash
cd traffic-generator
python generate_load.py
```

**Expected Output**:
```
============================================================
LLM Reliability Control Plane - Traffic Generator
Demonstrating detection rules and AI-powered insights
============================================================

Phase 1: Normal traffic
🔍 Fetching AI-powered insights...
✅ Health Score: 75.5/100
   Status: degraded
   Top Priority Actions: 3 recommendations
   Predictive Insights: 2 alerts

Phase 2: Cost spike via long prompts
...
```

**Expected**: 
- All phases complete without errors
- Insights endpoint is called
- Health scores are displayed

### 4.2 Verify Metrics (Check Console)

In the FastAPI terminal, you should see:
```
metric_histogram llm.request.latency_ms=1234.5 tags=['env:local', 'service:llm-reliability-control-plane', ...]
metric_counter llm.error.count+=1 tags=[...]
metric_gauge llm.cost.usd=0.000123 tags=[...]
```

**Expected**: Metrics are being emitted (either to Datadog or console).

---

## Step 5: Test Complete Flow (End-to-End)

### 5.1 Start Everything

**Terminal 1 - FastAPI:**
```bash
cd LLM-Reliability-Control-Plane
uvicorn app.main:app --reload
```

**Terminal 2 - Failure Theater:**
```bash
cd failure-theater
npm run dev
```

**Terminal 3 - Monitor Logs:**
```bash
cd LLM-Reliability-Control-Plane
# Watch for metric emissions
```

### 5.2 Complete Demo Flow

1. **Open Failure Theater**: `http://localhost:8000`
2. **Show Initial State**: Health score 85, no incidents
3. **Trigger Cost Explosion**: Click red button
4. **Watch Health Score Drop**: 85 → 45
5. **Show Recommendation**: "Save 30% by downgrading model"
6. **Check API Logs**: Should see cost metrics
7. **Trigger Another Scenario**: Click latency spike
8. **Watch Health Score**: Drops further
9. **Show Incident Count**: Should increase
10. **Reset System**: Click reset button

**Expected**: Complete flow works smoothly, health scores update, recommendations appear.

---

## Step 6: Test with Datadog (Optional but Recommended)

### 6.1 Setup Datadog Agent

Follow `DATADOG_SETUP.md` to:
1. Install Datadog agent
2. Configure API keys
3. Import monitors, dashboard, SLO

### 6.2 Verify Metrics in Datadog

1. Go to **Metrics Explorer**
2. Search for `llm.request.latency_ms`
3. You should see metrics appearing

**Expected**: Metrics visible in Datadog.

### 6.3 Trigger Monitor

1. Use Failure Theater to trigger cost explosion
2. Wait 5 minutes (monitor evaluation window)
3. Check **Monitors** in Datadog
4. Monitor should trigger (if threshold exceeded)

**Expected**: Monitor triggers, incident created (if configured).

### 6.4 Check Dashboard

1. Go to **Dashboards** → "LLM Reliability Control Plane"
2. You should see:
   - Health score widget
   - Latency metrics
   - Cost metrics
   - Quality metrics
   - Security signals

**Expected**: Dashboard shows data.

---

## Step 7: Test Health Score Calculation

### 7.1 Test Different Scenarios

```bash
# Healthy scenario
curl -X POST "http://localhost:8000/insights" \
  -H "Content-Type: application/json" \
  -d '{
    "avg_latency_ms": 200,
    "error_rate": 0.001,
    "retry_rate": 0.001,
    "avg_cost_per_request": 0.0005,
    "avg_input_tokens": 100,
    "avg_output_tokens": 50,
    "avg_quality_score": 0.9,
    "ungrounded_rate": 0.01,
    "safety_block_rate": 0.001,
    "injection_risk_rate": 0.0,
    "token_abuse_rate": 0.0,
    "timeout_rate": 0.0,
    "latency_trend": "stable",
    "cost_trend": "stable",
    "error_trend": "stable"
  }'
```

**Expected**: Health score should be high (80+).

```bash
# Critical scenario
curl -X POST "http://localhost:8000/insights" \
  -H "Content-Type: application/json" \
  -d '{
    "avg_latency_ms": 2000,
    "error_rate": 0.1,
    "retry_rate": 0.2,
    "avg_cost_per_request": 0.05,
    "avg_input_tokens": 5000,
    "avg_output_tokens": 100,
    "avg_quality_score": 0.3,
    "ungrounded_rate": 0.2,
    "safety_block_rate": 0.1,
    "injection_risk_rate": 0.05,
    "token_abuse_rate": 0.02,
    "timeout_rate": 0.05,
    "latency_trend": "increasing",
    "cost_trend": "increasing",
    "error_trend": "increasing"
  }'
```

**Expected**: Health score should be low (<60), many recommendations.

---

## Step 8: Test Error Handling

### 8.1 Test Invalid Requests

```bash
# Missing required fields
curl -X POST "http://localhost:8000/qa" \
  -H "Content-Type: application/json" \
  -d '{}'

# Invalid endpoint
curl http://localhost:8000/invalid
```

**Expected**: Should return appropriate error messages (400, 404, etc.).

### 8.2 Test with Backend Down

1. Stop FastAPI server
2. Try to use Failure Theater
3. Check error handling

**Expected**: UI should show error message, not crash.

---

## Step 9: Performance Testing

### 9.1 Load Test

```bash
# Send 100 requests rapidly
for i in {1..100}; do
  curl -X POST "http://localhost:8000/qa" \
    -H "Content-Type: application/json" \
    -d '{"question": "test", "document": "test"}' &
done
wait
```

**Expected**: All requests complete, no crashes.

### 9.2 Concurrent Requests

Use Failure Theater to click multiple buttons rapidly.

**Expected**: All scenarios trigger, no race conditions.

---

## Step 10: Verify All Features

### Checklist

- [ ] FastAPI starts without errors
- [ ] All endpoints return 200 OK
- [ ] Failure toggles work (latency, retry, bad prompt, long context)
- [ ] Health score calculates correctly
- [ ] Insights endpoint returns recommendations
- [ ] Failure Theater UI loads
- [ ] All 4 failure buttons work
- [ ] Health score updates in real-time
- [ ] Recommendations appear
- [ ] Reset button works
- [ ] Traffic generator runs all phases
- [ ] Metrics are emitted (check logs)
- [ ] Datadog integration works (if configured)
- [ ] Monitors trigger (if configured)
- [ ] Dashboard shows data (if configured)

---

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.9+)
- Check dependencies: `pip list | grep fastapi`
- Check port 8000 is free: `netstat -an | grep 8000`

### Failure Theater won't start
- Check Node version: `node --version` (need 18+)
- Check dependencies: `cd failure-theater && npm list`
- Check port 3000 is free

### No metrics appearing
- Check Datadog agent is running (if using Datadog)
- Check environment variables are set
- Check console logs for metric emissions

### Health score not updating
- Check API URL in Failure Theater: `NEXT_PUBLIC_API_URL`
- Check browser console for errors
- Check network tab for API calls

### Monitors not triggering
- Wait 5 minutes (evaluation window)
- Check metrics exist in Datadog
- Check monitor query syntax
- Verify thresholds are realistic

---

## Quick Test Script

Save this as `quick_test.sh`:

```bash
#!/bin/bash

echo "🧪 Testing LLM Reliability Control Plane"
echo ""

echo "1. Testing health endpoint..."
curl -s http://localhost:8000/health | grep -q "ok" && echo "✅ Health check passed" || echo "❌ Health check failed"

echo "2. Testing /qa endpoint..."
curl -s -X POST "http://localhost:8000/qa" \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "document": "test"}' | grep -q "answer" && echo "✅ /qa endpoint works" || echo "❌ /qa endpoint failed"

echo "3. Testing /insights endpoint..."
curl -s -X POST "http://localhost:8000/insights" \
  -H "Content-Type: application/json" \
  -d '{"avg_latency_ms": 1000, "error_rate": 0.01, "avg_cost_per_request": 0.001, "avg_quality_score": 0.8, "latency_trend": "stable", "cost_trend": "stable", "error_trend": "stable"}' | grep -q "health_summary" && echo "✅ /insights endpoint works" || echo "❌ /insights endpoint failed"

echo ""
echo "✅ Basic tests complete!"
```

Run with: `bash quick_test.sh`

---

## Next Steps

Once all tests pass:
1. Deploy to Cloud Run (or preferred hosting)
2. Configure Datadog in production
3. Test with real traffic
4. Capture screenshots for submission
5. Record video walkthrough

---

**Remember**: The goal is to demonstrate that everything works end-to-end, from clicking a button to seeing incidents created in Datadog!

