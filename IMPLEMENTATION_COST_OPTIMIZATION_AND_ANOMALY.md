# 💰 Cost Optimization Engine & Anomaly Attribution - Implementation Complete

## ✅ What Was Implemented

### 1. **LLM Cost Optimization Engine with ROI Calculator** ✅

**Location**: `app/cost_optimization_engine.py`

**Features**:
- ✅ Track optimization recommendations over time
- ✅ Calculate before/after costs
- ✅ Generate ROI reports with actual savings
- ✅ Show messages like: "This recommendation saved $1,234 in the last 7 days"
- ✅ Store optimization history in JSON file
- ✅ Integrate with Datadog for metric tracking

**Key Classes**:
- `OptimizationRecommendation`: Represents a cost optimization recommendation
- `OptimizationResult`: Tracks actual results of implemented optimizations
- `CostOptimizationEngine`: Main engine for tracking and calculating ROI

**API Endpoints** (in `app/routes/optimization.py`):
- `POST /optimization/recommendations` - Create a new recommendation
- `POST /optimization/recommendations/{id}/implement` - Mark as implemented
- `POST /optimization/recommendations/{id}/record-result` - Record actual results
- `GET /optimization/roi-report` - Get ROI report (shows actual savings)
- `GET /optimization/recommendations` - Get all recommendations history

### 2. **Anomaly Attribution Engine** ✅

**Location**: `app/anomaly_attribution_engine.py`

**Features**:
- ✅ Not just detecting anomalies, but attributing them to causes
- ✅ Provides confidence scores for attributions
- ✅ Example: "Anomaly caused by 23% increase in token usage from /stress endpoint"
- ✅ Causal analysis with confidence scores
- ✅ Breakdown by endpoint, model, request type
- ✅ Identifies primary cause and contributing factors

**Key Classes**:
- `AnomalyAttribution`: Represents an anomaly with its attributed causes
- `AnomalyAttributionEngine`: Main engine for attributing anomalies

**API Endpoints**:
- `POST /optimization/anomaly/attribute` - Attribute an anomaly to causes
- `GET /optimization/anomaly/recent` - Get recent anomalies

## 📊 How It Works

### Cost Optimization Engine Flow

1. **Create Recommendation**:
   ```python
   POST /optimization/recommendations
   {
     "title": "Switch to gemini-1.5-flash for non-critical requests",
     "category": "model_switch",
     "estimated_savings_per_request": 0.003,
     "estimated_savings_percentage": 40.0
   }
   ```

2. **Implement Recommendation**:
   ```python
   POST /optimization/recommendations/{id}/implement
   {
     "baseline_metrics": {
       "cost_per_request": 0.008,
       "avg_input_tokens": 1500,
       "request_count": 1000
     }
   }
   ```

3. **Record Results** (after some time):
   ```python
   POST /optimization/recommendations/{id}/record-result
   {
     "period_days": 7,
     "before_cost": 56.0,  # Optional, can fetch from Datadog
     "after_cost": 33.6,   # Optional, can fetch from Datadog
     "confidence_score": 0.85
   }
   ```

4. **Get ROI Report**:
   ```python
   GET /optimization/roi-report?days=7
   
   Response:
   {
     "total_savings": 1234.56,
     "top_recommendations": [
       {
         "title": "Switch to gemini-1.5-flash",
         "savings": 567.89,
         "message": "This recommendation saved $567.89 in the last 7 days"
       }
     ]
   }
   ```

### Anomaly Attribution Engine Flow

1. **Attribute Anomaly**:
   ```python
   POST /optimization/anomaly/attribute?metric_name=llm.cost.usd&anomaly_timestamp=2024-01-15T10:30:00
   
   Response:
   {
     "summary": "Anomaly caused by 300.0% increase in endpoint '/stress' (Confidence: 87.5%)",
     "primary_cause": {
       "description": "Anomaly caused by 300.0% increase in endpoint '/stress'",
       "dimension": "endpoint",
       "name": "/stress",
       "change_percentage": 300.0,
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
     ]
   }
   ```

## 🔧 Integration Points

### Datadog Integration

Both engines integrate with Datadog:

1. **Cost Optimization Engine**:
   - Fetches cost metrics from Datadog for before/after comparison
   - Emits metrics: `llm.optimization.savings.total`, `llm.optimization.roi.percentage`
   - Tracks recommendation creation and implementation

2. **Anomaly Attribution Engine**:
   - Fetches metric breakdowns by dimension (endpoint, model, request_type)
   - Compares baseline vs anomaly period
   - Uses Datadog API to query metrics

### Storage

- **Optimization History**: Stored in `data/optimization_history.json`
- **Format**: JSON with recommendations and results
- **Persistence**: Automatically saved after each operation

## 📝 Example Usage

### Example 1: Track Model Switch Optimization

```python
# 1. Create recommendation
POST /optimization/recommendations
{
  "title": "Switch to gemini-1.5-flash for /qa endpoint",
  "category": "model_switch",
  "description": "Use cheaper model for non-critical QA requests",
  "estimated_savings_per_request": 0.003,
  "estimated_savings_percentage": 40.0,
  "priority": "high"
}

# Response: { "id": "opt-20240115-103000-0", ... }

# 2. Implement it
POST /optimization/recommendations/opt-20240115-103000-0/implement
{
  "baseline_metrics": {
    "cost_per_request": 0.008,
    "avg_input_tokens": 1500,
    "avg_output_tokens": 500,
    "request_count": 1000,
    "period_start": "2024-01-15T00:00:00"
  }
}

# 3. After 7 days, record results
POST /optimization/recommendations/opt-20240115-103000-0/record-result
{
  "period_days": 7,
  "before_cost": 56.0,
  "after_cost": 33.6,
  "request_count": 7000,
  "confidence_score": 0.90
}

# Response:
{
  "actual_savings": 22.4,
  "roi_percentage": 1120.0,  # (22.4 / 2.0 implementation_cost) * 100
  "message": "This recommendation saved $22.40 in the last 7 days"
}

# 4. Get ROI report
GET /optimization/roi-report?days=7

# Response:
{
  "total_savings": 1234.56,
  "top_recommendations": [
    {
      "title": "Switch to gemini-1.5-flash for /qa endpoint",
      "savings": 22.40,
      "message": "This recommendation saved $22.40 in the last 7 days",
      "roi_percentage": 1120.0,
      "confidence": 0.90
    }
  ]
}
```

### Example 2: Attribute Cost Spike Anomaly

```python
# Detect cost spike and attribute it
POST /optimization/anomaly/attribute?metric_name=llm.cost.usd&anomaly_timestamp=2024-01-15T10:30:00

# Response:
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

## 🎯 Key Features

### Cost Optimization Engine

1. **Recommendation Tracking**:
   - Create recommendations with estimated savings
   - Track implementation status
   - Record actual results

2. **ROI Calculation**:
   - Calculate actual savings (before_cost - after_cost)
   - Calculate ROI percentage
   - Confidence scores for attribution

3. **Reporting**:
   - ROI reports by time period
   - Top performing recommendations
   - Savings by category
   - Total savings summary

### Anomaly Attribution Engine

1. **Anomaly Analysis**:
   - Fetch metrics from Datadog
   - Compare baseline vs anomaly period
   - Breakdown by dimensions (endpoint, model, request_type)

2. **Attribution**:
   - Identify primary cause with confidence
   - Find contributing factors
   - Calculate total confidence score

3. **Reporting**:
   - Human-readable attribution reports
   - Causal analysis
   - Affected resources list

## 📊 Datadog Metrics Emitted

### Cost Optimization Metrics

- `llm.optimization.recommendation.created` - When recommendation is created
- `llm.optimization.recommendation.implemented` - When recommendation is implemented
- `llm.optimization.savings.total` - Total savings from optimization
- `llm.optimization.roi.percentage` - ROI percentage
- `llm.optimization.savings.confidence` - Confidence in savings attribution

### Anomaly Attribution Metrics

- Attribution results are returned in API responses
- Can be logged to Datadog as events or custom metrics

## 🔄 Next Steps

1. **Integrate with Insights Endpoint**:
   - Automatically create recommendations from insights
   - Link anomaly attributions to insights

2. **Dashboard Integration**:
   - Create Datadog dashboard widgets for ROI
   - Show anomaly attributions in dashboards

3. **Automation**:
   - Auto-create recommendations from cost predictions
   - Auto-attribute anomalies when detected

4. **Enhanced Reporting**:
   - Export ROI reports to CSV/PDF
   - Create visualizations

## 🧪 Testing

### Test Cost Optimization

```bash
# 1. Create recommendation
curl -X POST "http://localhost:8000/optimization/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Optimization",
    "category": "model_switch",
    "description": "Test description",
    "estimated_savings_per_request": 0.003,
    "estimated_savings_percentage": 40.0
  }'

# 2. Get ROI report
curl "http://localhost:8000/optimization/roi-report?days=7"
```

### Test Anomaly Attribution

```bash
# Attribute an anomaly
curl -X POST "http://localhost:8000/optimization/anomaly/attribute?metric_name=llm.cost.usd"
```

## 📚 API Documentation

Full API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Look for the `/optimization` endpoints section.

---

**✅ Implementation Complete!** Both features are fully implemented and ready to use.

