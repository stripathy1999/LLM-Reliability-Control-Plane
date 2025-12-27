# 🧪 Complete Testing & Verification Guide

Step-by-step guide to test the project end-to-end and verify all functionality.

## 🚀 Quick Start - Get Everything Running

### Terminal 1: Start Backend

**Windows PowerShell:**
```powershell
cd "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
.\venv\Scripts\Activate.ps1
$env:LRCP_GEMINI_API_KEY = "AIzaSyCGMd-wESGb3PUKG_fOF2E2tSTmax40ke8"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Linux/macOS:**
```bash
cd LLM-Reliability-Control-Plane
source venv/bin/activate
export LRCP_GEMINI_API_KEY="your-api-key"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**✅ Verify:** Terminal shows `Uvicorn running on http://127.0.0.1:8000`

### Terminal 2: Start Frontend (Optional)

```bash
cd failure-theater
npm install  # First time only
npm run dev
```

**✅ Verify:** Terminal shows `Ready on http://localhost:3000`

---

## 📋 Step-by-Step Testing Guide

### Step 1: Verify Backend Health

**Test:** Open browser to http://127.0.0.1:8000/health

**Expected Result:**
```json
{
  "status": "ok"
}
```

**✅ Verification:**
- Status code: 200
- Response contains `"status": "ok"`

---

### Step 2: Test Swagger UI

**Test:** Open http://127.0.0.1:8000/docs

**✅ Visual Verification:**
- Modern dark theme loads
- Gradient backgrounds visible
- All endpoints listed
- Color-coded HTTP methods (GET=blue, POST=green, etc.)
- Smooth animations on hover

**✅ Functional Verification:**
1. Click on `POST /qa`
2. Click "Try it out"
3. Fill request body:
   ```json
   {
     "question": "What is artificial intelligence?",
     "document": "AI is the simulation of human intelligence by machines."
   }
   ```
4. Click "Execute"

**Expected Response:**
- Status: 200 OK
- Response body contains:
  - `answer`: Non-empty string (actual Gemini response)
  - `metadata`: Object with:
    - `latency_ms`: > 1000 (real API call)
    - `input_tokens`: > 0
    - `output_tokens`: > 0
    - `cost_usd`: > 0
    - `llm.semantic_similarity_score`: 0.0 to 1.0

**✅ Verification Checklist:**
- [ ] Answer is not empty
- [ ] Latency > 1000ms (real API call)
- [ ] Tokens counted correctly
- [ ] Cost calculated
- [ ] Quality score present

---

### Step 3: Test All Endpoints

#### Test `/qa` Endpoint

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/qa" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?", "document": "Python is a programming language."}'
```

**✅ Verify:**
- Returns 200 OK
- `answer` field has content
- `metadata` includes all required fields
- Quality metrics present

#### Test `/reason` Endpoint

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/reason" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain machine learning"}'
```

**✅ Verify:**
- Returns 200 OK
- Long-form answer (reasoning response)
- Latency metrics present

#### Test `/stress` Endpoint

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/stress" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Summarize", "repetitions": 50}'
```

**✅ Verify:**
- Returns 200 OK
- High `input_tokens` (due to repetitions)
- Higher `cost_usd` than other endpoints
- Cost anomaly should trigger

#### Test `/insights` Endpoint

**Request:**
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

**✅ Verify:**
- Returns 200 OK
- `health_summary.overall_health_score`: 0-100
- `recommendations`: Array with items
- `predictive_insights`: Array with items
- `priority_actions`: Array with 5 items

---

### Step 4: Test Failure Scenarios

#### Test Latency Simulation

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/reason?simulate_latency=true" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

**✅ Verify:**
- `latency_ms` > 2000ms (simulated delay)
- Should trigger latency SLO monitor if repeated

#### Test Retry Simulation

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/reason?simulate_retry=true" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

**✅ Verify:**
- `retry_count` > 0
- Should trigger error burst monitor if repeated

#### Test Cost Explosion

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/stress?simulate_long_context=true" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "repetitions": 100}'
```

**✅ Verify:**
- Very high `input_tokens`
- High `cost_usd`
- Should trigger cost anomaly monitor

#### Test Safety Blocks

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/qa?simulate_bad_prompt=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "document": "test"}'
```

**✅ Verify:**
- `safety_block` may be true
- Should trigger safety block monitor if repeated

---

### Step 5: Run Automated Test Suite

**Command:**
```bash
python test_end_to_end.py
```

**✅ Expected Output:**
```
✅ Health Endpoint: Returns 200 OK
✅ Root Endpoint: Returns 200 OK
✅ QA Endpoint: Answer length: 200+ chars, Latency: 3000+ms, Cost: $0.0002+
✅ QA Endpoint (latency): Simulation works
✅ QA Endpoint (retry): Simulation works
✅ QA Endpoint (bad_prompt): Simulation works
✅ Reason Endpoint: Answer length: 1000+ chars
✅ Stress Endpoint: Input tokens: 10+, Cost: $0.0001+
✅ Insights Endpoint: Health score: 50-100, Recommendations: 1+
✅ Error Handling: Returns 422 for invalid request

✅ Passed: 10
❌ Failed: 0
⚠️  Warnings: 0
✅ All critical tests passed!
```

**✅ Verification:**
- All tests pass
- No failures
- Real API calls working (latency > 1000ms)

---

### Step 6: Test Failure Theater UI

**Access:** http://localhost:3000

**✅ Visual Verification:**
- Dark gradient background
- Health Score displays prominently (0-100)
- Real-time stats bar shows:
  - Active Requests: 0 (initially)
  - Total Requests: 0 (initially)
  - Avg Latency: N/A (initially)
  - Total Cost: $0.0000 (initially)
- Health Score Chart visible (area chart)
- Four failure scenario buttons visible

**✅ Functional Testing:**

1. **Click "🔴 Cost Explosion"**
   - Watch loading indicator appear
   - Active Requests counter increases to 15
   - Health Score drops from 85 → 45
   - Status changes to "Critical"
   - Recommendation appears: "Cost spike detected!..."
   - Incident count increases
   - Recent Incidents panel shows new incident
   - Chart updates with new data point

2. **Click "🟠 Latency Spike"**
   - Health Score drops to 55
   - Status changes to "Degraded"
   - Recommendation: "Latency SLO breach!..."
   - Another incident appears

3. **Click "🔵 Quality Drop"**
   - Health Score drops to 50
   - Status: "Critical"
   - Recommendation about quality degradation

4. **Click "⚫ Security Attack"**
   - Health Score drops to 40
   - Status: "Critical"
   - Security alert recommendation

5. **Click "🔄 Reset System"**
   - Health Score returns to 85
   - Status: "Healthy"
   - Incident count resets
   - Recent Incidents cleared

**✅ Verification Checklist:**
- [ ] All buttons work
- [ ] Health scores update correctly
- [ ] Chart animates smoothly
- [ ] Incidents appear in panel
- [ ] Metrics update in real-time
- [ ] Reset button works

---

### Step 7: Test Traffic Generator

**Command:**
```bash
python traffic-generator/generate_load.py
```

**✅ Expected Behavior:**
1. **Normal Traffic Phase**
   - Sends normal requests
   - Metrics should be baseline

2. **Cost Spike Phase**
   - Sends requests with long context
   - Cost metrics spike
   - Should trigger cost anomaly monitor

3. **Quality Drop Phase**
   - Sends bad prompts
   - Quality scores drop
   - Should trigger quality degradation monitor

4. **Latency Spike Phase**
   - Sends requests with latency simulation
   - Latency metrics spike
   - Should trigger latency SLO monitor

**✅ Verification:**
- Script runs without errors
- All phases complete
- Metrics sent to Datadog (if agent running)

---

### Step 8: Verify Datadog Integration

#### Check Metrics in Datadog

1. **Go to Metrics → Explorer**
2. **Search for:** `llm.request.latency_ms`
3. **Filter by:** `service:llm-reliability-control-plane`

**✅ Verify:**
- Metrics appear in graph
- Data points visible
- Tags are correct

**Repeat for:**
- `llm.cost.usd`
- `llm.tokens.input`
- `llm.tokens.output`
- `llm.error.count`
- `llm.semantic_similarity_score`
- `llm.health_score`

#### Check APM Traces

1. **Go to APM → Traces**
2. **Filter by:** `service:llm-reliability-control-plane`

**✅ Verify:**
- Traces appear for each request
- Spans show endpoint names
- Tags include: `endpoint`, `model`, `request_type`
- Latency visible in trace timeline

#### Check Logs

1. **Go to Logs**
2. **Filter by:** `service:llm-reliability-control-plane`

**✅ Verify:**
- Structured JSON logs appear
- `prompt_id` present for correlation
- Request/response metadata included
- Error messages clear (if any)

#### Check Dashboard

1. **Go to Dashboards → "LLM Reliability Control Plane"**
2. **Verify widgets show data:**
   - Latency graphs populated
   - Cost graphs populated
   - Token usage graphs populated
   - Quality metrics visible
   - Monitor status visible

**✅ Verification:**
- All widgets show data
- Graphs update over time
- No empty widgets

#### Check Monitors

1. **Go to Monitors**
2. **Filter by tag:** `llm`

**✅ Verify:**
- 5 monitors visible:
  1. LLM p95 Latency SLO Burn
  2. LLM Cost Anomaly Detection
  3. LLM Error Burst / Retry Storm
  4. LLM Quality Degradation
  5. LLM Safety Block Surge
- Monitor status: OK (if thresholds not exceeded)
- Monitor queries are correct

#### Test Monitor Triggering

**Trigger Latency Monitor:**
```bash
# Send 20 requests with latency simulation
for i in {1..20}; do
  curl -X POST "http://127.0.0.1:8000/reason?simulate_latency=true" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "test"}'
done
```

**✅ Verify:**
1. Monitor status changes to Alert
2. Alert notification appears
3. Incident is auto-created (if rules configured)
4. Incident includes:
   - Monitor details
   - Runbook message
   - Attached dashboard
   - Attached logs
   - Attached traces

---

## ✅ Complete Verification Checklist

### Backend Verification
- [ ] Server starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] Swagger UI loads at /docs
- [ ] All endpoints return 200 OK
- [ ] Real Gemini API responses (not empty)
- [ ] Metadata includes tokens, cost, latency
- [ ] Failure simulation parameters work

### Frontend Verification
- [ ] Failure Theater loads at localhost:3000
- [ ] Health score displays correctly
- [ ] Real-time stats update
- [ ] Chart animates smoothly
- [ ] Failure buttons trigger API calls
- [ ] Incidents appear in panel
- [ ] Reset button works

### Swagger UI Verification
- [ ] Modern dark theme loads
- [ ] All endpoints visible
- [ ] "Try it out" works
- [ ] Request/response examples work
- [ ] Copy buttons work
- [ ] Search functionality works
- [ ] Animations smooth

### Datadog Verification
- [ ] Metrics appear in Metrics Explorer
- [ ] APM traces appear
- [ ] Logs appear in Logs Explorer
- [ ] Dashboard populates with data
- [ ] Monitors configured and evaluating
- [ ] Incidents auto-create when monitors trigger
- [ ] Incident context attached correctly

### Automated Tests
- [ ] All 10 tests pass
- [ ] No failures
- [ ] Real API calls working

---

## 🎯 What Judges Should See

### 1. Dashboard (Datadog)
- **Healthy State**: All metrics normal, monitors OK
- **Incident State**: Monitors alerting, metrics showing anomalies
- **Link**: Share dashboard URL

### 2. Monitors
- **Configuration**: Query, threshold, runbook visible
- **Status**: OK or Alert
- **Message**: Complete runbook answering judge questions

### 3. Incidents
- **Auto-Creation**: Triggered automatically
- **Context**: Dashboard, logs, traces attached
- **Runbook**: Visible in incident message
- **Severity**: Appropriate level (SEV-1, SEV-2, SEV-3)

### 4. Application
- **Swagger UI**: Modern, professional, interactive
- **Failure Theater**: Beautiful, real-time, engaging
- **Endpoints**: All working, returning real data

---

## 📸 Screenshots to Capture

1. **Dashboard - Healthy State**
2. **Dashboard - Incident State**
3. **Monitor Configuration** (showing query and runbook)
4. **Monitor Alert** (triggered state)
5. **Incident Created** (with runbook visible)
6. **Incident with Attachments** (dashboard, logs, traces)
7. **APM Traces** (service overview and trace detail)
8. **Metrics Explorer** (showing llm.* metrics)
9. **Swagger UI** (showing modern design)
10. **Failure Theater** (showing health score and incidents)

---

## 🚀 Quick Test Commands

### Test All Endpoints (PowerShell)
```powershell
# Health
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"

# QA
$body = @{question="What is AI?"; document="AI is intelligence"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/qa" -Method Post -ContentType "application/json" -Body $body

# Insights
$body = @{avg_latency_ms=1200; error_rate=0.02; avg_cost_per_request=0.008; avg_quality_score=0.65; latency_trend="increasing"; cost_trend="increasing"; error_trend="stable"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/insights" -Method Post -ContentType "application/json" -Body $body
```

### Trigger Monitor (PowerShell)
```powershell
# Trigger latency monitor (send 20 requests)
1..20 | ForEach-Object {
  Invoke-RestMethod -Uri "http://127.0.0.1:8000/reason?simulate_latency=true" -Method Post -ContentType "application/json" -Body '{"prompt":"test"}' | Out-Null
  Start-Sleep -Milliseconds 100
}
```

---

## ✅ Final Verification

Before submission, ensure:

- [ ] All endpoints tested and working
- [ ] Swagger UI looks professional
- [ ] Failure Theater works end-to-end
- [ ] Datadog metrics flowing
- [ ] Monitors configured correctly
- [ ] Incidents auto-create with context
- [ ] Dashboard shows all data
- [ ] Screenshots captured
- [ ] Video walkthrough recorded

---

**You're ready for submission!** 🎉


