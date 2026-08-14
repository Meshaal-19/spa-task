# ProcessAI — Agentic Process Monitor

A full-stack AI-powered system that monitors OS processes in real time, detects CPU/memory anomalies, and triggers a two-agent investigation pipeline to analyze and report on suspicious activity.

Built as the Phase 3 capstone project for the Arbisoft AI Internship 2026.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    React Frontend                    │
│  ProcessTable │ AnomalyFeed │ CpuChart │ LoginView  │
└──────────────────────┬──────────────────────────────┘
                       │ REST (JWT)
┌──────────────────────▼──────────────────────────────┐
│                  FastAPI Backend                     │
│                                                      │
│  ┌─────────────┐   ┌──────────────────────────────┐ │
│  │   Monitor   │   │       Agent Pipeline         │ │
│  │  (Thread)   │   │                              │ │
│  │  psutil 2s  │   │  Triage Agent (OpenRouter)   │ │
│  │  sampling   │   │  Llama 3.1 8B · fast pass    │ │
│  └──────┬──────┘   │         ↓                    │ │
│         │          │  Investigator (Claude Haiku) │ │
│  ┌──────▼──────┐   │  Deep analysis + report      │ │
│  │   SQLite    │   │         ↓                    │ │
│  │  Processes  │   │  Tracer Hook (ToolCallLog)   │ │
│  │  Anomalies  │   └──────────────────────────────┘ │
│  │  Investig.  │                                     │
│  │  ToolCalls  │   ┌──────────────────────────────┐ │
│  └─────────────┘   │       MCP Server             │ │
│                    │  get_live_processes          │ │
│                    │  get_active_anomalies        │ │
│                    │  get_anomaly_detail          │ │
│                    └──────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## Features

**Process Monitoring**
- Polls all running OS processes every 2 seconds via psutil
- Tracks CPU%, memory%, PID, username per process
- Qualifies anomalies after 5 consecutive samples above threshold (CPU > 60% or memory > 80%)
- Groups processes by category: SYSTEM / BROWSER / USER APPS

**Anomaly Detection & Grouping**
- Severity tiers: HIGH (CPU ≥ 80%) / MEDIUM (CPU ≥ 70%) / LOW (everything else)
- Email alert via Gmail SMTP when a HIGH anomaly is first detected
- Live anomaly feed updates every 2 seconds

**Two-Agent Investigation Pipeline**
- **Triage agent** (Llama 3.1 8B via OpenRouter): fast first-pass classification, 3s timeout
- **Investigator agent** (Claude Haiku via Anthropic): deep analysis with findings, recommendation, confidence score
- **Tool call tracer hook**: every agent invocation logged to DB with duration in ms
- **MCP server**: investigator can cross-reference live process data via MCP tools

**Dashboard**
- Live CPU chart (recharts): top 8 processes, 30-sample rolling window
- Process table with category grouping
- Anomaly feed with severity grouping
- JWT-authenticated login/register

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, SQLite, psutil |
| AI — Triage | Llama 3.1 8B Instruct (OpenRouter, free tier) |
| AI — Investigator | claude-haiku-4-5-20251001 (Anthropic API) |
| AI — Coding | Claude Code (all scaffolding, refactoring, tests) |
| Protocol | MCP (FastMCP), JWT (python-jose + bcrypt) |
| Frontend | React 18, Vite, recharts |
| Container | Docker, nginx, docker-compose |
| Tests | pytest, pytest-asyncio, httpx, SQLite StaticPool |

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node 20+
- API keys: Anthropic, OpenRouter, Gmail App Password (for email alerts)

### Backend

```bash
cd processai/backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Create .env (copy from .env.example and fill in values)
cp .env.example .env

uvicorn main:app --reload
# API running at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

### Frontend

```bash
cd processai/frontend
npm install
npm run dev
# Dashboard at http://localhost:5173
```

### Docker (full stack)

```bash
cd processai
docker compose up --build
# Frontend: http://localhost:5174
# Backend:  http://localhost:8000
```

---

## Environment Variables

Create `processai/backend/.env`:

```env
SECRET_KEY=your-secret-key
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your-16-char-app-password
ALERT_EMAIL=alerts@example.com
DATABASE_URL=sqlite:///./processai.db
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> Gmail SMTP requires a [Google App Password](https://myaccount.google.com/apppasswords) — not your regular password.

---

## Running Tests

```bash
cd processai/backend
pytest -v
```

Tests use an in-memory SQLite database (StaticPool) — no real DB touched.

---

## Demo

To flood the dashboard with anomalies for demo/testing:

```bash
cd processai
python stress_demo.py
```

Spawns 10 CPU-burning worker processes. Anomalies appear on the dashboard in ~10 seconds. Press Ctrl+C to stop all workers.

---

## Agent Pipeline Detail

```
POST /investigations/{anomaly_id}
        │
        ▼
  [Triage Agent]  ←── OpenRouter Llama 3.1 8B (free)
  timeout: 3s          Returns: {severity, summary, needs_deep_investigation}
  fallback: escalate   If timeout/error → always escalate
        │
        ▼
  [Investigator]  ←── Anthropic Claude Haiku
  MCP tools available: get_live_processes, get_active_anomalies, get_anomaly_detail
  Returns: {findings, recommendation, confidence}
        │
        ▼
  [Tracer Hook]   ←── Logs tool call to ToolCallLog table
  agent, tool, args, result, duration_ms
        │
        ▼
  Investigation saved, anomaly status → "resolved"
```

---

## Project Structure

```
processai/
├── backend/
│   ├── agents/
│   │   ├── triage.py          # Llama triage via OpenRouter
│   │   ├── investigator.py    # Claude Haiku deep analysis
│   │   └── tracer.py          # Tool call hook/logger
│   ├── mcp_server/
│   │   └── server.py          # FastMCP server (3 tools)
│   ├── routers/
│   │   ├── auth.py            # Register / login
│   │   ├── processes.py       # GET /processes
│   │   └── investigations.py  # POST /investigations/{id}
│   ├── monitor.py             # Background psutil sampling thread
│   ├── mailer.py              # Gmail SMTP email alerts
│   ├── models.py              # SQLAlchemy models
│   ├── main.py                # FastAPI app + CORS
│   └── tests/                 # pytest suite
├── frontend/
│   └── src/
│       ├── Dashboard.jsx      # Main layout + polling
│       ├── CpuChart.jsx       # recharts live CPU graph
│       ├── AnomalyFeed.jsx    # Severity-grouped anomalies
│       ├── ProcessTable.jsx   # Category-grouped process table
│       └── LoginView.jsx      # Auth form
├── stress_demo.py             # CPU stress test for demo
├── docker-compose.yml
└── prompts.md                 # AI interaction log
```
