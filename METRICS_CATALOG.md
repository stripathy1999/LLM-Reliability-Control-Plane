# 📊 Metrics Catalog - LLM Reliability Control Plane

Complete catalog of all custom metrics emitted by the LLM Reliability Control Plane.

---

## 🎯 Core Metrics

### **Health Score**
- **Metric Name**: `llm.health_score`
- **Type**: Gauge (0-100)
- **Description**: Composite health score combining performance, reliability, cost, quality, and security
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: 80-100 (healthy), 60-79 (degraded), <60 (critical)
- **Alert Threshold**: <60 triggers "LLM Health Score Degradation" monitor

---

## ⚡ Performance Metrics

### **Request Latency**
- **Metric Name**: `llm.request.latency_ms`
- **Type**: Histogram
- **Description**: End-to-end request latency in milliseconds
- **Tags**: `service`, `env`, `endpoint`, `model`, `request_type`, `dd.trace_id`, `dd.span_id`
- **Normal Range**: <500ms (excellent), <1000ms (good), <1500ms (acceptable), >1500ms (poor)
- **Alert Threshold**: p95 > 1500ms triggers "LLM p95 Latency SLO Burn" monitor
- **SLO**: p95 < 1500ms

### **Time to First Token**
- **Metric Name**: `llm.time_to_first_token_ms`
- **Type**: Histogram
- **Description**: Time to first token in response (synthetic, same as latency for demo)
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: <500ms

### **Retry Count**
- **Metric Name**: `llm.retry_count`
- **Type**: Gauge
- **Description**: Number of retries for a request
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: 0 (no retries), >0 indicates issues

---

## 🔄 Reliability Metrics

### **Error Count**
- **Metric Name**: `llm.error.count`
- **Type**: Counter
- **Description**: Number of errors encountered
- **Tags**: `service`, `env`, `endpoint`, `model`, `error_type`
- **Normal Range**: 0
- **Alert Threshold**: >10 errors in 5 minutes triggers "LLM Error Burst / Retry Storm" monitor

### **Timeout Count**
- **Metric Name**: `llm.timeout.count`
- **Type**: Counter
- **Description**: Number of requests that timed out (>10 seconds)
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: 0

### **Empty Response Count**
- **Metric Name**: `llm.empty_response.count`
- **Type**: Counter
- **Description**: Number of requests with empty responses (0 tokens)
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: 0

### **Safety Block Count**
- **Metric Name**: `llm.safety_block.count`
- **Type**: Counter
- **Description**: Number of requests blocked by safety filters
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: <5 in 10 minutes
- **Alert Threshold**: >5 in 10 minutes triggers "LLM Safety Block Surge" monitor

---

## 💰 Cost Metrics

### **Cost (USD)**
- **Metric Name**: `llm.cost.usd`
- **Type**: Gauge
- **Description**: Cost per request in USD
- **Tags**: `service`, `env`, `endpoint`, `model`, `dd.trace_id`
- **Normal Range**: <$0.001 (excellent), <$0.01 (good), <$0.1 (acceptable), >$0.1 (poor)
- **Alert Threshold**: >$0.00008 in 5 minutes triggers "LLM Cost Anomaly Detection" monitor
- **Budget Alert**: >$1.00 in 24 hours triggers "LLM Daily Cost Budget Alert" monitor

### **Input Tokens**
- **Metric Name**: `llm.tokens.input`
- **Type**: Gauge
- **Description**: Number of input tokens per request
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: 10-1000 tokens

### **Output Tokens**
- **Metric Name**: `llm.tokens.output`
- **Type**: Gauge
- **Description**: Number of output tokens per request
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: 50-500 tokens

---

## 🎨 Quality Metrics

### **Semantic Similarity Score**
- **Metric Name**: `llm.semantic_similarity_score`
- **Type**: Gauge (0-1)
- **Description**: Semantic similarity between prompt and response (0 = no similarity, 1 = identical)
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: >0.7 (excellent), >0.5 (good), >0.4 (acceptable), <0.4 (poor)
- **Alert Threshold**: <0.4 triggers "LLM Quality Degradation" monitor

### **Ungrounded Answer Flag**
- **Metric Name**: `llm.ungrounded_answer_flag`
- **Type**: Gauge (0 or 1)
- **Description**: Boolean flag indicating potential hallucination (1 = ungrounded, 0 = grounded)
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: 0 (all answers grounded)

---

## 🛡️ Security Metrics

### **Prompt Injection Risk**
- **Metric Name**: `llm.security.prompt_injection_risk`
- **Type**: Counter
- **Description**: Number of requests with potential prompt injection patterns
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: 0
- **Detection**: Heuristic-based (very long prompts, suspicious patterns)

### **Token Abuse**
- **Metric Name**: `llm.security.token_abuse`
- **Type**: Counter
- **Description**: Number of requests with unusually high token usage (>5000 tokens)
- **Tags**: `service`, `env`, `endpoint`, `model`
- **Normal Range**: 0
- **Detection**: Total tokens > 5000

---

## 📈 Derived Metrics

### **Token Efficiency Ratio**
- **Calculation**: `output_tokens / input_tokens`
- **Description**: Efficiency of token usage (higher = more output per input)
- **Normal Range**: >0.5 (good efficiency)

### **Cost per Token**
- **Calculation**: `cost_usd / (input_tokens + output_tokens)`
- **Description**: Cost efficiency per token
- **Normal Range**: <$0.00001 per token

### **Request Rate**
- **Calculation**: `sum(llm.request.latency_ms) / time_window`
- **Description**: Requests per second
- **Tags**: `service`, `env`, `endpoint`

---

## 🏷️ Standard Tags

All metrics include these standard tags:

- **`service`**: `llm-reliability-control-plane`
- **`env`**: `local`, `staging`, `production`
- **`endpoint`**: `/qa`, `/reason`, `/stress`
- **`model`**: `gemini-2.5-flash`, `gemini-1.5-pro`, etc.
- **`model_version`**: `0.1.0`, etc.
- **`request_type`**: `qa`, `reason`, `stress`

### **Correlation Tags** (for trace-log-metric correlation):

- **`dd.trace_id`**: Datadog trace ID
- **`dd.span_id`**: Datadog span ID

---

## 📊 Metric Aggregations

### **Recommended Aggregations:**

- **Health Score**: `avg:llm.health_score{service:llm-reliability-control-plane}`
- **Latency (p50, p95, p99)**: `p50:llm.request.latency_ms{...}`, `p95:...`, `p99:...`
- **Error Rate**: `sum:llm.error.count{...}.as_rate()`
- **Cost (Total)**: `sum:llm.cost.usd{...}`
- **Cost (Average)**: `avg:llm.cost.usd{...}`
- **Quality (Average)**: `avg:llm.semantic_similarity_score{...}`

---

## 🔍 Metric Queries

### **Example Queries:**

```datadog
# Health score over time
avg:llm.health_score{service:llm-reliability-control-plane}

# Latency by endpoint
p95:llm.request.latency_ms{service:llm-reliability-control-plane} by {endpoint}

# Cost trend
sum:llm.cost.usd{service:llm-reliability-control-plane}

# Error rate
sum:llm.error.count{service:llm-reliability-control-plane}.as_rate()

# Quality by model
avg:llm.semantic_similarity_score{service:llm-reliability-control-plane} by {model}
```

---

## 📝 Notes

- All metrics are emitted via Datadog StatsD
- Metrics include trace correlation tags for seamless investigation
- Custom spans in APM provide additional context
- Logs include metric values for correlation
- Monitors use these metrics for alerting

---

**For more information, see:**
- [README.md](README.md) - Project overview
- [DATADOG_SETUP.md](DATADOG_SETUP.md) - Setup instructions
- [DATADOG_ADVANCED_FEATURES.md](DATADOG_ADVANCED_FEATURES.md) - Advanced features

