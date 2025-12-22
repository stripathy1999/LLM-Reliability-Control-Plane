# 3-Minute Video Walkthrough Script

Use this as a guide for your submission video. Aim for 3 minutes total.

## Structure (3 minutes)

**Key Message**: "This isn't just observability - it's an AI-powered reliability control plane that monitors everything, predicts issues, and recommends solutions."

### 1. Introduction & The Innovation (30 seconds)

**Script:**
"Hi, I'm [your name] and this is my LLM Reliability Control Plane for the Datadog hackathon. 

Traditional observability shows you 20+ metrics but doesn't tell you what to do. I've built something different - an **AI-powered reliability control plane** that:

1. Combines all metrics into a single **health score** (0-100)
2. Provides **AI-powered recommendations** with estimated savings
3. **Predicts issues** before they happen
4. Monitors **cost, quality, and security** - not just latency and errors

Every feature answers three questions: What failed? Why did it fail? What should the engineer do next?"

**Visuals:**
- Show Datadog dashboard overview
- Highlight different sections (latency, cost, quality, security)

---

### 2. Detection Rules & Thought Process (60 seconds)

**Script:**
"I've defined 5 detection rules, each targeting a specific failure mode:

First, **Latency SLO Burn** - monitors p95 latency exceeding 1500ms. This catches performance degradation before users notice.

Second, **Cost Anomaly Detection** - alerts when cost spikes 2x above baseline. This is critical for LLM apps where token usage can explode unexpectedly.

Third, **Error Burst Monitor** - detects when error rates spike, indicating upstream service issues or authentication problems.

Fourth, **Quality Degradation** - tracks semantic similarity scores. If responses drift from expected quality, we know immediately.

And fifth, **Safety Block Surge** - monitors when safety filters trigger frequently, indicating potential attacks or misconfiguration.

Each monitor includes a complete runbook in the alert message, so engineers know exactly what to do."

**Visuals:**
- Show monitor configuration screen
- Highlight each monitor's query and threshold
- Show monitor message with runbook

---

### 3. Innovation Deep Dive (60 seconds)

**Script:**
"Five innovations make this solution stand out:

**First, Composite Health Score** - Instead of 20+ separate metrics, one number (0-100) tells you everything. It combines performance, reliability, cost, quality, and security. When it drops below 60, you know immediately something is wrong.

**Second, AI-Powered Recommendations** - We don't just alert, we analyze and suggest. Cost spike? We tell you to downgrade the model and save 30%. Quality dropping? We suggest prompt improvements. Every recommendation includes estimated impact.

**Third, Predictive Alerts** - We forecast issues 24 hours before they happen. Latency trending up? We warn you before the SLO breach. This lets engineers fix issues proactively, not reactively.

**Fourth, Cost Observability** - Most solutions ignore cost. We track every token and dollar, detect anomalies, and suggest optimizations. This prevents budget overruns before they happen.

**Fifth, Quality & Security** - We monitor response quality with semantic similarity and detect attacks with prompt injection detection. This ensures responses are accurate and secure, not just fast.

When any detection rule triggers, Datadog automatically creates an incident with the dashboard, logs, traces, and AI recommendations attached. Engineers know exactly what to do."

**Visuals:**
- Show cost metrics on dashboard
- Show quality metrics
- Show security signals
- Show incident creation with attachments

---

### 4. Challenges & Solution (30 seconds)

**Script:**
"The main challenge was creating actionable incidents with context. Datadog's Incident Rules solved this - they automatically attach dashboards, logs, and traces when monitors trigger.

For the demo, I'm using synthetic LLM responses, but the code is structured to easily swap in real Vertex AI integration. All the observability instrumentation works the same way.

The result is a complete observability strategy that makes LLM applications reliable, cost-effective, and secure."

**Visuals:**
- Show code structure (brief)
- Show incident with all attachments
- Show dashboard in action

---

## Key Points to Emphasize

1. **End-to-End Observability**: APM + Metrics + Logs + Incidents
2. **Actionable Incidents**: Full context and runbooks
3. **Innovation**: Cost, quality, and security observability
4. **Production Ready**: Code structure supports real Vertex AI

## Visual Checklist

- [ ] Dashboard overview (healthy state)
- [ ] Monitor configurations (show queries and thresholds)
- [ ] Monitor messages with runbooks
- [ ] Cost metrics visualization
- [ ] Quality metrics visualization
- [ ] Security signals
- [ ] Incident creation (trigger → incident)
- [ ] Incident with attachments (dashboard, logs, traces)
- [ ] Dashboard during incident (showing triggered monitors)

## Tips

- **Practice**: Rehearse to stay within 3 minutes
- **Screen Recording**: Use clear, high-quality screen capture
- **Narration**: Speak clearly, pause between sections
- **Transitions**: Smooth transitions between Datadog views
- **Highlight**: Use mouse cursor or annotations to highlight key elements

## Example Flow

1. Start: Dashboard overview (5s)
2. Navigate: Monitors list (10s)
3. Show: One monitor detail with runbook (15s)
4. Navigate: Dashboard showing cost/quality/security (20s)
5. Trigger: Show incident creation (15s)
6. Show: Incident with attachments (20s)
7. End: Dashboard during incident (15s)

Total: ~90 seconds for visuals + 90 seconds for narration = 3 minutes

