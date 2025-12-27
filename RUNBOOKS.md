# 📋 Runbooks - LLM Reliability Control Plane

Complete runbooks for all monitors and common failure scenarios.

---

## 🚨 Monitor Runbooks

### **1. LLM p95 Latency SLO Burn**

**Monitor**: `LLM p95 Latency SLO Burn`  
**Trigger**: p95 latency > 1500ms for 5 minutes  
**Severity**: SEV-2

#### **What Failed?**
p95 latency is breaching SLO threshold (1500ms).

#### **Why Did It Fail?**
Possible causes:
- Model overload or rate limiting
- Upstream Vertex AI latency spike
- Network issues
- Recent deployment or config change
- High traffic volume

#### **What Should the Engineer Do Next?**

1. **Check Datadog APM Traces**
   - Go to: APM → Traces
   - Filter: `service:llm-reliability-control-plane`
   - Look for: Slow spans, especially `llm.gemini.generate`
   - Action: Identify which endpoint/model is slow

2. **Review Recent Deployments**
   - Go to: Datadog → Events
   - Filter: `deployment` or `github-actions`
   - Action: Check if recent deployment caused the issue

3. **Check Vertex AI Service Status**
   - Go to: Google Cloud Console → Vertex AI
   - Check: Service status, quota limits
   - Action: Verify service is healthy

4. **Review Metrics Dashboard**
   - Go to: Dashboard → "LLM Reliability Control Plane"
   - Check: Latency trends, request rate, error rate
   - Action: Identify patterns

5. **Consider Remediation:**
   - **Downgrade Model**: Switch to faster model (gemini-2.5-flash)
   - **Enable Caching**: Cache responses for repeated queries
   - **Scale Up**: Increase instance count
   - **Rate Limiting**: Implement rate limits to reduce load

---

### **2. LLM Cost Anomaly Detection**

**Monitor**: `LLM Cost Anomaly Detection`  
**Trigger**: Cost > $0.00008 in 5 minutes  
**Severity**: SEV-3

#### **What Failed?**
LLM cost has spiked above the expected threshold while traffic remains stable.

#### **Why Did It Fail?**
Possible causes:
- Long context prompts consuming excessive tokens
- Model upgrade to more expensive tier
- Prompt engineering changes causing token bloat
- Token abuse or prompt injection attack
- Context window expansion

#### **What Should the Engineer Do Next?**

1. **Review Cost Breakdown by Endpoint**
   - Go to: Dashboard → Cost metrics
   - Filter: By `endpoint` tag
   - Action: Identify which endpoint is expensive

2. **Check Token Usage Trends**
   - Go to: Metrics Explorer
   - Query: `sum:llm.tokens.input{...}` and `sum:llm.tokens.output{...}`
   - Action: Compare input vs output tokens

3. **Investigate Recent Prompt Changes**
   - Go to: Logs Explorer
   - Filter: `service:llm-reliability-control-plane`
   - Look for: Long prompts, recent changes
   - Action: Review prompt engineering changes

4. **Check for Token Abuse**
   - Go to: Metrics Explorer
   - Query: `sum:llm.security.token_abuse{...}`
   - Action: Check if abuse detected

5. **Consider Remediation:**
   - **Downgrade Model Tier**: Use cheaper model for non-critical requests
   - **Enable Response Caching**: Cache responses to reduce API calls
   - **Implement Rate Limiting**: Limit requests per user/IP
   - **Add Prompt Length Limits**: Restrict input token count
   - **Review Cost Optimization Recommendations**: Call `/insights` endpoint

---

### **3. LLM Error Burst / Retry Storm**

**Monitor**: `LLM Error Burst / Retry Storm`  
**Trigger**: >10 errors in 5 minutes  
**Severity**: SEV-1

#### **What Failed?**
Error rate has spiked (>10 errors in 5 minutes).

#### **Why Did It Fail?**
Possible causes:
- Vertex AI service degradation
- Authentication/authorization failures
- Rate limit exceeded
- Network connectivity issues
- Invalid prompt format causing API errors
- API key expiration or rotation

#### **What Should the Engineer Do Next?**

1. **Check Error Logs**
   - Go to: Logs Explorer
   - Filter: `service:llm-reliability-control-plane` AND `status:error`
   - Look for: Specific error messages
   - Action: Identify error patterns

2. **Review APM Traces for Failed Requests**
   - Go to: APM → Traces
   - Filter: `service:llm-reliability-control-plane` AND `status:error`
   - Action: Identify which requests are failing

3. **Verify Vertex AI Service Status**
   - Go to: Google Cloud Console → Vertex AI
   - Check: Service status, incident history
   - Action: Verify service is operational

4. **Check Authentication Credentials**
   - Go to: Environment variables
   - Verify: `LRCP_GEMINI_API_KEY` is valid
   - Action: Rotate key if expired

5. **Review Retry Logic and Backoff Strategy**
   - Go to: Code → `app/llm_client.py`
   - Check: Retry configuration
   - Action: Adjust retry limits/backoff if needed

6. **Consider Remediation:**
   - **Implement Circuit Breaker**: Stop requests if error rate too high
   - **Add Retry Limits**: Prevent retry storms
   - **Failover to Backup Model**: Switch to alternative model
   - **Scale Down**: Reduce load if service degraded

---

### **4. LLM Quality Degradation**

**Monitor**: `LLM Quality Degradation`  
**Trigger**: Semantic similarity < 0.4 for 10 minutes  
**Severity**: SEV-2

#### **What Failed?**
Semantic similarity score has dropped below acceptable threshold (0.4).

#### **Why Did It Fail?**
Possible causes:
- Model drift or degradation
- Prompt engineering changes causing poor responses
- Context quality issues
- Model version change
- Training data contamination
- Hallucination increase

#### **What Should the Engineer Do Next?**

1. **Review Quality Metrics Dashboard**
   - Go to: Dashboard → Quality metrics
   - Check: Semantic similarity trends
   - Action: Identify when degradation started

2. **Sample Recent Responses from Logs**
   - Go to: Logs Explorer
   - Filter: `service:llm-reliability-control-plane`
   - Look for: Recent responses
   - Action: Review response quality manually

3. **Compare Current vs Baseline Similarity Scores**
   - Go to: Metrics Explorer
   - Query: `avg:llm.semantic_similarity_score{...}`
   - Action: Compare to historical baseline

4. **Check for Recent Model or Prompt Changes**
   - Go to: Events → Deployments
   - Check: Recent model version changes
   - Action: Identify if change caused issue

5. **Consider Remediation:**
   - **Rollback Model Version**: Revert to previous version
   - **Update Prompts**: Improve prompt engineering
   - **Retrain Model**: If model drift detected
   - **Adjust Quality Thresholds**: If false positives

---

### **5. LLM Safety Block Surge**

**Monitor**: `LLM Safety Block Surge`  
**Trigger**: >5 safety blocks in 10 minutes  
**Severity**: SEV-2

#### **What Failed?**
Safety intervention blocks have surged (>5 in 10 minutes).

#### **Why Did It Fail?**
Possible causes:
- Prompt injection attacks
- Malicious user input
- Misconfigured safety filters
- False positives from safety policies
- Content policy violations

#### **What Should the Engineer Do Next?**

1. **Review Blocked Prompts in Logs**
   - Go to: Logs Explorer
   - Filter: `service:llm-reliability-control-plane` AND `llm.safety_block:true`
   - Action: Review blocked prompts

2. **Check for Patterns Indicating Attack**
   - Look for: Prompt injection patterns, jailbreak attempts
   - Action: Identify if attack or false positives

3. **Verify Safety Filter Configuration**
   - Go to: Code → `app/llm_client.py`
   - Check: Safety filter settings
   - Action: Verify configuration

4. **Consider Remediation:**
   - **Tighten Input Validation**: Add stricter validation
   - **Update Safety Policies**: Adjust safety thresholds
   - **Investigate User Behavior**: Check if specific users causing issues
   - **If False Positives**: Adjust safety thresholds

---

### **6. LLM Health Score Degradation**

**Monitor**: `LLM Health Score Degradation`  
**Trigger**: Health score < 60 for 10 minutes  
**Severity**: SEV-2

#### **What Failed?**
Composite health score has dropped below 60 (degraded threshold).

#### **Why Did It Fail?**
The health score combines performance, reliability, cost, quality, and security metrics. A low score indicates multiple issues across these dimensions.

#### **What Should the Engineer Do Next?**

1. **Call `/insights` Endpoint**
   - Endpoint: `POST http://127.0.0.1:8000/insights`
   - Action: Get AI-powered recommendations

2. **Review Component Scores**
   - Go to: Dashboard → Health Score widget
   - Check: Performance, reliability, cost, quality, security scores
   - Action: Identify which dimension is causing issues

3. **Check Individual Monitors**
   - Go to: Monitors
   - Filter: Tag `llm`
   - Action: See which specific monitors are alerting

4. **Review Predictive Insights**
   - Go to: `/insights` endpoint response
   - Check: `predictive_insights` field
   - Action: Review forecasted issues

5. **Implement Top Priority Recommendations**
   - Go to: `/insights` endpoint response
   - Check: `priority_actions` field
   - Action: Implement top 5 actions

---

### **7. LLM Daily Cost Budget Alert**

**Monitor**: `LLM Daily Cost Budget Alert`  
**Trigger**: Daily cost > $1.00  
**Severity**: SEV-2

#### **What Failed?**
Daily LLM cost budget exceeded ($1.00).

#### **Why Did It Fail?**
Possible causes:
- Unusually high traffic volume
- Cost spike from long context prompts
- Model upgrade to more expensive tier
- Token abuse or prompt injection attack

#### **What Should the Engineer Do Next?**

1. **Review Cost Breakdown by Endpoint and Time Period**
   - Go to: Dashboard → Cost metrics
   - Filter: Last 24 hours, by endpoint
   - Action: Identify cost drivers

2. **Check for Unusual Traffic Patterns**
   - Go to: Metrics Explorer
   - Query: `sum:llm.request.latency_ms{...}.as_rate()`
   - Action: Compare to baseline

3. **Investigate Recent Model or Prompt Changes**
   - Go to: Events → Deployments
   - Check: Recent changes
   - Action: Identify if change caused cost increase

4. **Consider Remediation:**
   - **Implement Rate Limiting**: Limit requests per user/IP
   - **Downgrade Model Tier**: Use cheaper model
   - **Enable Caching**: Cache responses
   - **Add Cost Controls**: Implement cost limits

5. **Review Cost Optimization Recommendations**
   - Call: `/insights` endpoint
   - Check: Cost optimization recommendations
   - Action: Implement recommendations

---

## 🔧 Common Troubleshooting Steps

### **General Troubleshooting:**

1. **Check Health Score**
   - Go to: Dashboard → Health Score widget
   - Action: Identify overall system health

2. **Review Recent Events**
   - Go to: Datadog → Events
   - Filter: Last 1 hour
   - Action: Identify recent changes

3. **Check All Monitors**
   - Go to: Monitors
   - Filter: Tag `llm`
   - Action: See all alerting monitors

4. **Review Logs**
   - Go to: Logs Explorer
   - Filter: `service:llm-reliability-control-plane`
   - Action: Check for errors or warnings

5. **Check Traces**
   - Go to: APM → Traces
   - Filter: `service:llm-reliability-control-plane`
   - Action: Identify slow or failed requests

---

## 📞 Escalation

### **SEV-1 (Critical):**
- Immediate response required
- Affects production users
- Example: Error burst, service down

### **SEV-2 (High):**
- Response within 1 hour
- Degraded performance
- Example: Latency SLO breach, health score degradation

### **SEV-3 (Medium):**
- Response within 4 hours
- Non-critical issues
- Example: Cost anomaly, quality degradation

---

**For more information, see:**
- [README.md](README.md) - Project overview
- [INCIDENT_CREATION_GUIDE.md](INCIDENT_CREATION_GUIDE.md) - Incident setup
- [DATADOG_SETUP.md](DATADOG_SETUP.md) - Datadog configuration

