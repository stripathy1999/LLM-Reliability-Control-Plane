# 🏗️ Architecture - LLM Reliability Control Plane

Complete architecture documentation with system diagrams and component descriptions.

---

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Reliability Control Plane                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         FastAPI Backend (Python)         │
        │  - LLM Client (Gemini/Vertex AI)        │
        │  - Telemetry (Metrics, Logs, Traces)     │
        │  - ML Models (Cost, Quality, Router)     │
        │  - Incident Manager                      │
        └─────────────────────────────────────────┘
                    │                    │
                    ▼                    ▼
        ┌──────────────────┐
        │   Datadog Agent   │
        │  (StatsD, APM)    │
        └──────────────────┘
                    │
                    ▼
        ┌──────────────────┐
        │   Datadog Cloud   │
        │  (Observability)  │
        └──────────────────┘
                    │
                    ▼
        ┌──────────────────┐
        │  Unified Dashboard│
        │  (Datadog)        │
        └──────────────────┘
```

---

## 🔄 Data Flow

### **Request Flow:**

```
1. Client Request
   │
   ▼
2. FastAPI Endpoint (/qa, /reason, /stress)
   │
   ▼
3. LLM Client (Gemini API)
   │
   ▼
4. Telemetry Emission
   ├─→ Metrics (StatsD)
   ├─→ Logs (JSON)
   └─→ Traces (APM)
   │
   ▼
5. Datadog Processing
   ├─→ APM (Distributed Tracing)
   ├─→ Metrics (Custom LLM Metrics)
   ├─→ Logs (Structured Logging)
   └─→ LLM Observability (Native)
   │
   ▼
6. ML-Powered Analysis
   ├─→ Cost Optimization Engine
   ├─→ Anomaly Attribution
   └─→ Predictive Monitors
   │
   ▼
7. Dashboard Update
```

### **Incident Flow:**

```
1. Monitor Trigger
   │
   ▼
2. Incident Manager (API)
   │
   ▼
3. Create Incident (Datadog API)
   ├─→ Attach Dashboard
   ├─→ Attach Logs
   └─→ Attach Traces
   │
   ▼
4. Incident Created
   └─→ Runbook Visible
   └─→ Full Context Available
```

---

## 🧩 Component Architecture

### **Backend Components:**

#### **1. FastAPI Application (`app/main.py`)**
- **Purpose**: Main application entry point
- **Features**: 
  - API routing
  - Swagger UI customization
  - Health checks
- **Dependencies**: FastAPI, uvicorn

#### **2. LLM Client (`app/llm_client.py`)**
- **Purpose**: Interface with Gemini/Vertex AI
- **Features**:
  - Request handling
  - Token counting
  - Cost calculation
  - Quality scoring
  - Custom spans
- **Dependencies**: google-generativeai, ddtrace

#### **3. Telemetry (`app/telemetry.py`)**
- **Purpose**: Emit metrics, logs, traces
- **Features**:
  - StatsD metrics
  - JSON logs
  - Trace correlation
  - Custom tags
- **Dependencies**: datadog, pythonjsonlogger

#### **4. Incident Manager (`app/incident_manager.py`)**
- **Purpose**: Programmatic incident creation
- **Features**:
  - Create incidents via API
  - Attach resources
  - Include runbooks
- **Dependencies**: datadog

#### **5. ML Models:**
- **Cost Predictor** (`app/ml_cost_predictor.py`): Gradient Boosting, 24h forecast
- **Quality Predictor** (`app/ml_quality_predictor.py`): Sentence Transformers
- **Model Router** (`app/model_router.py`): ML-based routing

#### **6. Health Score (`app/health_score.py`)**
- **Purpose**: Calculate composite health score
- **Input**: Performance, reliability, cost, quality, security metrics
- **Output**: 0-100 score

#### **7. Insights Engine (`app/ml_insights.py`)**
- **Purpose**: Generate AI-powered recommendations
- **Features**:
  - Cost optimization
  - Predictive alerts
  - Security recommendations
  - Quality improvements

---

## 🌐 Integration Points

### **Datadog Integration:**

```
┌─────────────────────────────────────────┐
│           Datadog Platform               │
├─────────────────────────────────────────┤
│  APM (Traces)                           │
│  ├─ Custom Spans                        │
│  ├─ Trace Correlation                   │
│  └─ Service Map                         │
│                                          │
│  Metrics                                │
│  ├─ Custom llm.* metrics                │
│  ├─ Histograms (latency)                │
│  ├─ Gauges (health, cost)               │
│  └─ Counters (errors)                   │
│                                          │
│  Logs                                   │
│  ├─ Structured JSON                     │
│  ├─ Trace Correlation                   │
│  └─ Service Tags                        │
│                                          │
│  Incidents                              │
│  ├─ Automated Creation                  │
│  ├─ Runbooks                            │
│  └─ Resource Attachments                │
│                                          │
│  Monitors                               │
│  ├─ Threshold Monitors (5)               │
│  └─ ML Anomaly Detection (3)            │
│                                          │
│  Dashboard                              │
│  ├─ Health Score Widget                 │
│  ├─ Metrics Visualization              │
│  └─ Monitor Status                      │
│                                          │
│  Notebooks                              │
│  ├─ Root Cause Analysis                 │
│  └─ Cost Optimization                   │
│                                          │
│  RUM                                    │
│  └─ Frontend Observability              │
└─────────────────────────────────────────┘
```

---

## 🔌 API Endpoints

### **Core LLM Endpoints:**

- **`POST /qa`**: Question & Answer (quality detection)
- **`POST /reason`**: Reasoning (latency monitoring)
- **`POST /stress`**: Stress testing (cost scenarios)

### **Observability Endpoints:**

- **`POST /insights`**: AI-powered insights
- **`GET /health`**: Health check
- **`POST /incidents/create`**: Create incident
- **`GET /incidents/status`**: Incident manager status

### **Optimization Endpoints:**

- **`POST /optimization/recommendations`**: Cost optimization recommendations
- **`POST /optimization/roi-report`**: ROI calculation report
- **`POST /optimization/attribute-anomaly`**: Anomaly attribution analysis

### **Datadog Integration Endpoints:**

- **`GET /datadog/products`**: List integrated Datadog products
- **`POST /datadog/synthetics/create`**: Create Synthetics test
- **`POST /datadog/notebooks/create`**: Create Notebook
- **`POST /datadog/workflows/trigger`**: Trigger Workflow Automation

---

## 🗄️ Data Storage

### **Models:**
- **Location**: `models/`
- **Files**: 
  - `cost_predictor.pkl` - Cost prediction model
  - `cost_scaler.pkl` - Feature scaler

### **Configuration:**
- **Environment Variables**: `.env` file
- **Datadog Resources**: `datadog/*.json` (monitors, dashboards, SLOs, workflows, on-call, log pipelines)

---

## 🚀 Deployment Architecture

### **Local Development:**
```
┌──────────────┐
│  FastAPI     │
│  (localhost) │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Datadog Agent│
│  (localhost) │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Datadog     │
│   Cloud      │
└──────────────┘
```

### **Production (GCP Cloud Run):**
```
┌──────────────────┐
│  Cloud Run       │
│  (FastAPI)       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Datadog Agent    │
│  (Sidecar)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Datadog Cloud   │
└──────────────────┘
```

---

## 🔐 Security Architecture

### **API Keys:**
- Stored in environment variables
- Never committed to repository
- Rotated regularly

### **Data Privacy:**
- Logs truncated (prompts/responses limited to 200 chars)
- PII not logged
- Secure transmission (HTTPS)

---

## 📊 Monitoring Architecture

### **Three-Layer Monitoring:**

1. **Application Layer**: Custom metrics, logs, traces
2. **Infrastructure Layer**: Datadog agent, system metrics
3. **Business Layer**: Health score, cost, quality metrics

### **Alerting Strategy:**

- **Threshold Monitors**: 5 monitors for specific metrics
- **ML Anomaly Detection**: 3 monitors using ML
- **Budget Alerts**: Daily cost budget monitor
- **SLO Monitoring**: Latency SLO with burn rate

---

## 🔄 Error Handling

### **Graceful Degradation:**

- **Datadog API Failure**: Falls back to logging
- **ML Model Failure**: Falls back to rule-based
- **LLM API Failure**: Returns error with context
- **Datadog Failure**: Graceful degradation with local logging

---

## 📈 Scalability

### **Horizontal Scaling:**
- Stateless FastAPI application
- Datadog agent per instance
- Shared Datadog backend

### **Performance:**
- Async request handling
- Connection pooling
- Caching (future enhancement)

---

**For more details, see:**
- [README.md](README.md) - Project overview
- [DATADOG_SETUP.md](DATADOG_SETUP.md) - Setup guide
- [DATADOG_IMPORT_GUIDE.md](DATADOG_IMPORT_GUIDE.md) - Datadog resource import guide

