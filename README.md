# LLM Reliability Control Plane (Datadog Hackathon)

Backend implementation for the **LLM Reliability Control Plane** challenge, built to make it easy to answer:

- **What failed?**
- **Why did it fail?**
- **What should the engineer do next?**

The focus is on **observability, failure modes, and runbooks**, not on fancy UI.

## Architecture

- **Backend**: FastAPI (Python)
- **LLM**: Gemini via Vertex AI (simulated locally for now)
- **Hosting target**: GCP Cloud Run
- **Observability**: Datadog APM, custom metrics, structured logs

Repo layout:

- `app/` – FastAPI app and supporting modules  
- `traffic-generator/` – load script to generate normal + failure traffic  
- `datadog/` – dashboard, monitors, SLO JSON exports  

## Endpoints

All endpoints accept **failure toggles** so you can deterministically trigger incidents:

- `simulate_latency=true`
- `simulate_retry=true`
- `simulate_bad_prompt=true`
- `simulate_long_context=true`

### `POST /qa`

- **Purpose**: Q&A over small static documents → used for **quality degradation** detection.
- Body:

```json
{
  "question": "What is Datadog?",
  "document": "Datadog is an observability platform..."
}
```

### `POST /reason`

- **Purpose**: Reasoning-style prompts → used for **latency** and **retry** behavior.

### `POST /stress`

- **Purpose**: Long-context prompts → used for **token & cost explosions**.
- Body includes `repetitions` to blow up context length.

## Telemetry Design

The app emits (via `app/telemetry.py`):

- **Performance**
  - `llm.request.latency_ms`
  - `llm.time_to_first_token_ms`
  - `llm.retry_count`
- **Reliability**
  - `llm.error.count`
  - `llm.timeout.count`
  - `llm.empty_response.count`
  - `llm.safety_block.count`
- **Cost**
  - `llm.tokens.input`
  - `llm.tokens.output`
  - `llm.cost.usd`
- **Quality**
  - `llm.response.length`
  - `llm.semantic_similarity_score`
  - `llm.ungrounded_answer_flag`

Structured logs include `prompt_id`, truncated prompt, response preview, and response/metric metadata.

## Running Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API

```bash
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` to explore the endpoints.

### 3. Run the traffic generator

In a separate terminal:

```bash
python traffic-generator/generate_load.py
```

This will run through:

1. **Normal traffic**
2. **Cost spike** (long prompts)
3. **Quality drop** (bad prompts / safety blocks)
4. **Latency + retry spike**

## Datadog Integration

This implementation provides **end-to-end observability** for LLM applications with:

1. **Streaming Telemetry**: LLM and runtime metrics streamed to Datadog via StatsD
2. **APM Auto-Instrumentation**: Distributed tracing via `ddtrace` for FastAPI
3. **Structured Logs**: JSON-formatted logs with correlation IDs for Datadog log ingestion
4. **Detection Rules**: 5 monitors with actionable incident creation
5. **Comprehensive Dashboard**: Single pane of truth answering the three judge questions

### Setup Instructions

#### 1. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Datadog credentials:

```bash
cp .env.example .env
```

Required variables:
- `LRCP_DATADOG_API_KEY`: Your Datadog API key
- `DD_AGENT_HOST`: Datadog agent host (use `localhost` for local, or agent hostname for remote)
- `DD_SITE`: Your Datadog site (e.g., `datadoghq.com`, `datadoghq.eu`)

#### 2. Install Datadog Agent (Local Development)

For local testing, install the Datadog agent:

```bash
# macOS
brew install datadog-agent

# Linux
# Follow: https://docs.datadog.com/agent/install/?tab=linux

# Windows
# Download from: https://docs.datadog.com/agent/install/?tab=windows
```

Start the agent:
```bash
datadog-agent start
```

#### 3. Import Datadog Resources

**Monitors** (`datadog/monitors.json`):
- Import via Datadog UI: Monitors → New Monitor → Import JSON
- Or use Datadog API: `POST /api/v1/monitor` with monitor definitions

**Dashboard** (`datadog/dashboard.json`):
- Import via Datadog UI: Dashboards → New Dashboard → Import JSON
- Or use Datadog API: `POST /api/v1/dashboard` with dashboard definition

**SLO** (`datadog/slo.json`):
- Import via Datadog UI: Service Management → SLOs → New SLO → Import JSON
- Or use Datadog API: `POST /api/v1/slo` with SLO definition

#### 4. Enable Incident Creation

Each monitor in `datadog/monitors.json` includes `incident_config` that specifies:
- Auto-create Datadog Incidents when triggered
- Attach dashboard, logs, and traces to incidents
- Include runbooks in incident messages

Configure incident rules in Datadog:
1. Go to **Incidents** → **Settings** → **Rules**
2. Create rules that match monitor tags (e.g., `llm`, `critical`)
3. Ensure incidents auto-attach dashboards and logs

### Monitor Details

1. **LLM p95 Latency SLO Burn** (Critical)
   - Triggers when p95 latency > 1500ms
   - Creates SEV-2 incident with latency traces

2. **LLM Cost Anomaly Detection** (Critical)
   - Triggers when cost spikes 2x above baseline
   - Creates SEV-3 incident with cost breakdown

3. **LLM Error Burst / Retry Storm** (Critical)
   - Triggers when >10 errors in 5 minutes
   - Creates SEV-1 incident with error logs and traces

4. **LLM Quality Degradation**
   - Triggers when semantic similarity < 0.4
   - Creates SEV-2 incident with quality metrics

5. **LLM Safety Block Surge**
   - Triggers when >5 safety blocks in 10 minutes
   - Creates SEV-2 incident with security logs

### Security Observability

The implementation includes security signals:
- `llm.security.prompt_injection_risk`: Detects suspicious prompt patterns
- `llm.security.token_abuse`: Flags unusually high token usage

These metrics appear in the dashboard's security section and can trigger additional monitors.

### Dashboard Features

The dashboard (`datadog/dashboard.json`) provides:

- **Golden Signals**: Latency, errors, throughput, saturation
- **Cost Tracking**: Real-time cost and token usage
- **Quality Metrics**: Semantic similarity trends
- **Security Signals**: Prompt injection and token abuse detection
- **SLO Status**: Current latency SLO compliance
- **Monitor Status**: Active incidents and thresholds

### Running with Datadog

1. Ensure Datadog agent is running
2. Set environment variables from `.env`
3. Start the API:

```bash
uvicorn app.main:app --reload
```

4. Run traffic generator to generate metrics:

```bash
python traffic-generator/generate_load.py
```

5. View in Datadog:
   - **APM**: Traces → Service: `llm-reliability-control-plane`
   - **Metrics**: Metrics Explorer → Search `llm.*`
   - **Logs**: Logs → Filter by `service:llm-reliability-control-plane`
   - **Dashboard**: Dashboards → "LLM Reliability Control Plane"
   - **Monitors**: Monitors → Filter by tag `llm`
   - **Incidents**: Incidents → View auto-created incidents with context

## Judge Questions Mapping

- **What failed?**
  - Check monitors: latency SLO, cost anomaly, error burst, quality degradation, safety surge.
  - Drill into Datadog dashboards and logs (endpoint, model, request type tags).
- **Why did it fail?**
  - Use tags (`endpoint`, `model`, `request_type`, `simulate_*`) and logs (prompt + metadata) to see if it was cost, latency, safety, or quality driven.
- **What should the engineer do next?**
  - Runbooks attached to monitors (e.g., downgrade model, enable caching, block abusive prompts).


