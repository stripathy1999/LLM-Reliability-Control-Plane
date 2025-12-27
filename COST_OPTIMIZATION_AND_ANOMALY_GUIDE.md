# 💰 Cost Optimization & Anomaly Attribution - Quick Guide

## 🎯 What Was Implemented

✅ **Cost Optimization Engine with ROI Calculator**
- Track recommendations and their actual savings
- Calculate ROI: "This recommendation saved $1,234 in the last 7 days"
- Store optimization history

✅ **Anomaly Attribution Engine**
- Attribute anomalies to causes: "Anomaly caused by 23% increase in token usage from /stress endpoint"
- Provide confidence scores
- Causal analysis

## 🚀 Quick Start

### 1. Start the Server

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Access API Documentation

Open: http://127.0.0.1:8000/docs

Look for the `/optimization` endpoints section.

## 📊 Example: Track Cost Optimization

### Step 1: Create a Recommendation

```bash
curl -X POST "http://localhost:8000/optimization/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Switch to gemini-1.5-flash for /qa endpoint",
    "category": "model_switch",
    "description": "Use cheaper model for non-critical QA requests",
    "estimated_savings_per_request": 0.003,
    "estimated_savings_percentage": 40.0,
    "priority": "high"
  }'
```

**Response**:
```json
{
  "id": "opt-20240115-103000-0",
  "title": "Switch to gemini-1.5-flash for /qa endpoint",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00"
}
```

### Step 2: Implement the Recommendation

```bash
curl -X POST "http://localhost:8000/optimization/recommendations/opt-20240115-103000-0/implement" \
  -H "Content-Type: application/json" \
  -d '{
    "baseline_metrics": {
      "cost_per_request": 0.008,
      "avg_input_tokens": 1500,
      "avg_output_tokens": 500,
      "request_count": 1000,
      "period_start": "2024-01-15T00:00:00"
    }
  }'
```

### Step 3: Record Results (After 7 Days)

```bash
curl -X POST "http://localhost:8000/optimization/recommendations/opt-20240115-103000-0/record-result" \
  -H "Content-Type: application/json" \
  -d '{
    "period_days": 7,
    "before_cost": 56.0,
    "after_cost": 33.6,
    "request_count": 7000,
    "confidence_score": 0.90
  }'
```

**Response**:
```json
{
  "recommendation_id": "opt-20240115-103000-0",
  "recommendation_title": "Switch to gemini-1.5-flash for /qa endpoint",
  "actual_savings": 22.4,
  "roi_percentage": 1120.0,
  "message": "This recommendation saved $22.40 in the last 7 days"
}
```

### Step 4: Get ROI Report

```bash
curl "http://localhost:8000/optimization/roi-report?days=7"
```

**Response**:
```json
{
  "period_days": 7,
  "total_savings": 1234.56,
  "top_recommendations": [
    {
      "title": "Switch to gemini-1.5-flash for /qa endpoint",
      "savings": 22.40,
      "message": "This recommendation saved $22.40 in the last 7 days",
      "roi_percentage": 1120.0,
      "confidence": 0.90
    }
  ],
  "savings_by_category": {
    "model_switch": 22.40
  }
}
```

## 🔍 Example: Attribute Anomaly

### Attribute a Cost Spike

```bash
curl -X POST "http://localhost:8000/optimization/anomaly/attribute?metric_name=llm.cost.usd&anomaly_timestamp=2024-01-15T10:30:00"
```

**Response**:
```json
{
  "summary": "Anomaly caused by 300.0% increase in endpoint '/stress' (Confidence: 87.5%)",
  "primary_cause": {
    "description": "Anomaly caused by 300.0% increase in endpoint '/stress'",
    "dimension": "endpoint",
    "name": "/stress",
    "change_percentage": 300.0,
    "contribution_percentage": 45.0,
    "confidence": 0.875
  },
  "contributing_factors": [
    {
      "description": "/qa endpoint contributed 30.0% with 66.7% change",
      "dimension": "endpoint",
      "name": "/qa",
      "change_percentage": 66.7,
      "confidence": 0.65
    }
  ],
  "metrics": {
    "baseline_value": 0.008,
    "anomalous_value": 0.015,
    "change_percentage": 87.5
  },
  "affected_resources": {
    "endpoints": ["/stress", "/qa"],
    "models": ["gemini-2.5-flash"]
  }
}
```

## 📋 All Available Endpoints

### Cost Optimization

- `POST /optimization/recommendations` - Create recommendation
- `POST /optimization/recommendations/{id}/implement` - Implement recommendation
- `POST /optimization/recommendations/{id}/record-result` - Record results
- `GET /optimization/roi-report` - Get ROI report
- `GET /optimization/recommendations` - Get all recommendations
- `GET /optimization/recommendations/{id}` - Get specific recommendation

### Anomaly Attribution

- `POST /optimization/anomaly/attribute` - Attribute an anomaly
- `GET /optimization/anomaly/recent` - Get recent anomalies

## 💾 Data Storage

- **Location**: `data/optimization_history.json`
- **Format**: JSON with recommendations and results
- **Auto-saved**: After each operation

## 🔗 Integration with Datadog

Both engines integrate with Datadog:

1. **Fetches metrics** from Datadog for cost comparison
2. **Fetches breakdowns** by endpoint, model, request_type
3. **Emits metrics** to Datadog:
   - `llm.optimization.savings.total`
   - `llm.optimization.roi.percentage`
   - `llm.optimization.savings.confidence`

## 🎯 Use Cases

### Use Case 1: Track Model Switch Savings

1. Create recommendation to switch models
2. Implement the switch
3. Record results after a week
4. Get ROI report showing actual savings

### Use Case 2: Investigate Cost Spike

1. Detect cost spike in Datadog
2. Attribute anomaly to find cause
3. Get report: "Anomaly caused by 23% increase in token usage from /stress endpoint"
4. Take action based on attribution

## 📚 Full Documentation

See `IMPLEMENTATION_COST_OPTIMIZATION_AND_ANOMALY.md` for complete implementation details.

---

**✅ Ready to Use!** Both features are fully implemented and integrated.

