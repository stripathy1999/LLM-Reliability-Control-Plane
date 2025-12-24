# Complete Testing Guide - LLM Reliability Control Plane

## 🚀 Quick Start

### 1. Start the Server

Open PowerShell in the project directory and run:

```powershell
cd "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
.\venv\Scripts\Activate.ps1
$env:LRCP_GEMINI_API_KEY = "AIzaSyCGMd-wESGb3PUKG_fOF2E2tSTmax40ke8"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The `--reload` flag enables auto-reload on code changes.

### 2. Access Swagger UI (Interactive API Documentation)

Once the server is running, open your browser and go to:

**👉 http://127.0.0.1:8000/docs**

This is the **Swagger UI** where you can:
- See all available endpoints
- Test each endpoint interactively
- View request/response schemas
- See example requests

### 3. Alternative: ReDoc Documentation

For a cleaner documentation view:

**👉 http://127.0.0.1:8000/redoc**

---

## 📋 End-to-End Testing Methods

### Method 1: Automated Test Suite (Recommended)

Run the comprehensive test script:

```powershell
# In a new PowerShell window (keep server running in first window)
cd "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
.\venv\Scripts\Activate.ps1
$env:LRCP_GEMINI_API_KEY = "AIzaSyCGMd-wESGb3PUKG_fOF2E2tSTmax40ke8"
$env:PYTHONIOENCODING = "utf-8"
python test_end_to_end.py
```

**Expected Output:**
```
✅ Passed: 10
❌ Failed: 0
⚠️  Warnings: 0
✅ All critical tests passed!
```

### Method 2: Swagger UI Interactive Testing

1. Open **http://127.0.0.1:8000/docs** in your browser
2. Click on any endpoint (e.g., `POST /qa`)
3. Click "Try it out"
4. Fill in the request body:
   ```json
   {
     "question": "What is artificial intelligence?",
     "document": "AI is the simulation of human intelligence by machines."
   }
   ```
5. Click "Execute"
6. See the response with:
   - Status code
   - Response body (with real Gemini answer!)
   - Response headers
   - Execution time

### Method 3: Manual API Testing with PowerShell

#### Test Health Endpoint
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

#### Test QA Endpoint
```powershell
$body = @{
    question = "What is Python?"
    document = "Python is a programming language."
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/qa" -Method Post -ContentType "application/json" -Body $body
$response | ConvertTo-Json -Depth 5
```

#### Test Reason Endpoint
```powershell
$body = @{
    prompt = "Explain machine learning in simple terms"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/reason" -Method Post -ContentType "application/json" -Body $body
Write-Host "Answer: $($response.answer)"
Write-Host "Tokens: $($response.metadata.input_tokens) / $($response.metadata.output_tokens)"
Write-Host "Cost: `$$($response.metadata.cost_usd)"
```

#### Test Stress Endpoint
```powershell
$body = @{
    prompt = "Summarize"
    repetitions = 5
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/stress" -Method Post -ContentType "application/json" -Body $body
$response | ConvertTo-Json -Depth 3
```

#### Test Insights Endpoint
```powershell
$body = @{
    avg_latency_ms = 1200.0
    error_rate = 0.02
    retry_rate = 0.05
    avg_cost_per_request = 0.008
    avg_input_tokens = 1500.0
    avg_output_tokens = 200.0
    avg_quality_score = 0.65
    ungrounded_rate = 0.08
    safety_block_rate = 0.03
    injection_risk_rate = 0.01
    token_abuse_rate = 0.005
    timeout_rate = 0.01
    latency_trend = "increasing"
    cost_trend = "increasing"
    error_trend = "stable"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/insights" -Method Post -ContentType "application/json" -Body $body
$response | ConvertTo-Json -Depth 5
```

### Method 4: Using curl (if available)

```bash
# Health check
curl http://127.0.0.1:8000/health

# QA endpoint
curl -X POST http://127.0.0.1:8000/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?", "document": "AI is artificial intelligence."}'

# Reason endpoint
curl -X POST http://127.0.0.1:8000/reason \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing"}'
```

---

## ✅ Verification Checklist

### 1. Server Health
- [ ] Server starts without errors
- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] Swagger UI loads at `/docs`

### 2. Real Gemini API Integration
- [ ] QA endpoint returns actual text (not empty)
- [ ] Response contains `answer` field with content
- [ ] Metadata shows `input_tokens > 0` and `output_tokens > 0`
- [ ] `cost_usd > 0` in metadata
- [ ] `latency_ms > 0` in metadata

### 3. All Endpoints Working
- [ ] `/qa` - Returns Q&A response
- [ ] `/reason` - Returns reasoning response
- [ ] `/stress` - Handles multiple repetitions
- [ ] `/insights` - Returns health analysis
- [ ] `/health` - Returns status

### 4. Error Handling
- [ ] Invalid requests return 422 status
- [ ] Missing fields are caught
- [ ] Error messages are clear

---

## 🔍 What to Look For in Responses

### Successful QA Response Example:
```json
{
  "answer": "Artificial intelligence (AI) is the simulation of human intelligence...",
  "metadata": {
    "text": "...",
    "latency_ms": 3517.89,
    "retry_count": 0,
    "safety_block": false,
    "input_tokens": 11,
    "output_tokens": 32,
    "cost_usd": 0.000276,
    "model": "gemini-2.5-flash",
    "prompt_id": "uuid-here",
    "llm.semantic_similarity_score": 0.85,
    "llm.ungrounded_answer_flag": false
  }
}
```

### Key Metrics to Verify:
- ✅ `answer` is not empty (real Gemini response)
- ✅ `input_tokens` > 0 (tokens were counted)
- ✅ `output_tokens` > 0 (response tokens counted)
- ✅ `cost_usd` > 0 (cost calculated)
- ✅ `latency_ms` > 1000 (real API call took time)
- ✅ `model` = "gemini-2.5-flash"

---

## 🐛 Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Verify virtual environment is activated
- Check API key is set: `$env:LRCP_GEMINI_API_KEY`

### Empty responses
- Verify API key is valid
- Check server logs for errors
- Ensure model name is correct (gemini-2.5-flash)

### Swagger UI not loading
- Verify server is running
- Check URL: http://127.0.0.1:8000/docs
- Try http://localhost:8000/docs

### Tests failing
- Ensure server is running before running tests
- Check API key is set in test environment
- Verify all dependencies are installed

---

## 📊 Expected Test Results

When running `test_end_to_end.py`, you should see:

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
```

---

## 🎯 Quick Test Commands

**One-liner to test everything:**
```powershell
# Terminal 1: Start server
cd "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
.\venv\Scripts\Activate.ps1
$env:LRCP_GEMINI_API_KEY = "AIzaSyCGMd-wESGb3PUKG_fOF2E2tSTmax40ke8"
python -m uvicorn app.main:app --reload

# Terminal 2: Run tests
cd "C:\Users\strip\Documents\Cursor\AI Accelerate Hackathon\LLM-Reliability-Control-Plane"
.\venv\Scripts\Activate.ps1
$env:LRCP_GEMINI_API_KEY = "AIzaSyCGMd-wESGb3PUKG_fOF2E2tSTmax40ke8"
$env:PYTHONIOENCODING = "utf-8"
python test_end_to_end.py
```

**Then open browser:** http://127.0.0.1:8000/docs
