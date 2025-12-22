# ⚡ Quick Start - Get Everything Running in 5 Minutes

## Fastest Way to Test Everything

### Step 1: Start Backend (2 minutes)

```bash
cd LLM-Reliability-Control-Plane

# Install dependencies
pip install -r requirements.txt

# Start API
uvicorn app.main:app --reload
```

✅ **Verify**: Open http://localhost:8000/docs - should see API docs

---

### Step 2: Start Failure Theater (2 minutes)

```bash
# In a new terminal
cd failure-theater

# Install dependencies
npm install

# Start UI
npm run dev
```

✅ **Verify**: Open http://localhost:3000 - should see beautiful UI

---

### Step 3: Test It! (1 minute)

1. **Click "🔴 Cost Explosion"** button
2. **Watch** health score drop from 85 → 45
3. **See** recommendation appear
4. **Check** API terminal for metrics being logged

✅ **Success**: If health score updates, everything works!

---

## What You Should See

### In Failure Theater:
- Health Score: 85 → 45 (after clicking)
- Status: Healthy → Critical
- Recommendation: "Cost spike detected! Consider downgrading model..."
- Incident Count: Increases

### In API Terminal:
```
metric_histogram llm.request.latency_ms=1234.5 tags=[...]
metric_gauge llm.cost.usd=0.000123 tags=[...]
metric_counter llm.error.count+=1 tags=[...]
```

---

## Quick Test Commands

```bash
# Test health
curl http://localhost:8000/health

# Test QA endpoint
curl -X POST "http://localhost:8000/qa" \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "document": "test"}'

# Test insights
curl -X POST "http://localhost:8000/insights" \
  -H "Content-Type: application/json" \
  -d '{"avg_latency_ms": 1000, "error_rate": 0.01, "avg_cost_per_request": 0.001, "avg_quality_score": 0.8, "latency_trend": "stable", "cost_trend": "stable", "error_trend": "stable"}'
```

---

## Troubleshooting

**Backend won't start?**
- Check Python: `python --version` (need 3.9+)
- Install deps: `pip install -r requirements.txt`

**Failure Theater won't start?**
- Check Node: `node --version` (need 18+)
- Install deps: `cd failure-theater && npm install`

**Buttons not working?**
- Check backend is running on port 8000
- Check browser console for errors
- Verify API URL: Should be `http://localhost:8000`

---

## Full Testing

For complete testing guide, see [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

**That's it!** You should now have:
- ✅ Backend running
- ✅ Failure Theater UI running
- ✅ Ability to trigger failure scenarios
- ✅ Health scores updating in real-time

Ready to demo! 🎭

