# prompts.md — ProcessAI
**AI Interaction Log · Phase 3 Build · Arbisoft Internship 2026**
Tool: Claude Code (Anthropic) + Claude (Cowork)
Project: ProcessAI — Agentic Process Monitor

---

## Phase 3 · Week 5 (Scaffold & Architecture)

### Prompt 1 — Project Scaffold
**Prompt:**
```
Scaffold a full-stack AI-powered process monitoring system called ProcessAI.
Backend: FastAPI + SQLAlchemy + SQLite. Frontend: React + Vite.
The system should use psutil to monitor running OS processes in a background thread,
flag anomalies when CPU > 60% or memory > 80% sustained for 10 consecutive samples,
and expose REST endpoints for processes and anomalies. Include JWT auth.
```
**Result:** Generated full project structure with `backend/` (main.py, models.py, schemas.py, database.py, auth.py, monitor.py, constants.py) and `frontend/src/` (App.jsx, Dashboard.jsx, api.js). Background monitor thread with 2-second sampling interval created.

**Correction applied:** Initial scaffold used `asyncio` for the monitor loop which conflicted with FastAPI's event loop. Switched to `threading.Thread(daemon=True)` for the background monitor.

---

### Prompt 2 — Database Models
**Prompt:**
```
Define SQLAlchemy models for ProcessAI:
- Process: name, pid, cpu_pct, mem_pct, username, sampled_at
- Anomaly: process_name, pid, anomaly_type, cpu_pct, mem_pct, consecutive_count, status, detected_at
- Investigation: anomaly_id (FK), findings, recommendation, confidence, model_used, created_at
- ToolCallLog: agent, tool, args_json, result_json, duration_ms, called_at
Use SQLite with check_same_thread=False.
```
**Result:** All four models generated with correct relationships and `Base.metadata.create_all()` on startup.

---

### Prompt 3 — Process Monitor Logic
**Prompt:**
```
Write a monitor.py that runs in a daemon thread, samples all running processes every 2 seconds
using psutil, upserts them to the Process table, and qualifies anomalies when CPU > 60% or
memory > 80% is sustained for QUALIFICATION_COUNT consecutive samples. Use constants from
constants.py. The anomaly upsert should be idempotent — update consecutive_count if already active.
```
**Result:** `_sample_processes()` and `_upsert_anomaly()` implemented. Monitors all PIDs, writes to DB, qualification logic tracks consecutive count per (name, pid) key.

**Correction applied:** Initial version opened a new DB session per sample but never closed it, leaking connections. Fixed by using `with SessionLocal() as db:` context manager.

---

## Phase 3 · Week 5–6 (Core AI Features)

### Prompt 4 — Triage Agent (OpenRouter / Llama)
**Prompt:**
```
Write a triage agent in backend/agents/triage.py using OpenRouter's free Llama 3.1 8B model.
It receives an anomaly object and returns JSON: {severity, summary, needs_deep_investigation}.
Use requests.post with a 3-second timeout. If it fails for any reason, return a fallback dict
with severity=high and needs_deep_investigation=True so the deep agent always runs on failure.
```
**Result:** `triage()` function with `try/except Exception` fallback. Model: `meta-llama/llama-3.1-8b-instruct:free` via `https://openrouter.ai/api/v1/chat/completions`.

**Correction applied:** Initial timeout was 30s — far too slow for a triage step. Reduced to 3s after testing showed OpenRouter free tier is unreliable. Also reduced max_tokens from 256 to 150 since JSON output is short.

---

### Prompt 5 — Investigator Agent (Claude Haiku)
**Prompt:**
```
Write backend/agents/investigator.py using the Anthropic Python SDK with claude-haiku-4-5-20251001.
The investigate() function receives an anomaly, builds a detailed prompt with process name, PID,
CPU%, memory%, duration, and a severity note for >80% CPU sustained >60s.
Return JSON: {findings, recommendation, confidence}. confidence between 0.0 and 1.0.
System prompt should instruct the model to be direct about high-risk findings, not soften them.
```
**Result:** `investigate()` implemented with `client.messages.create()`, max_tokens=512, system prompt enforcing direct risk assessment. JSON parsed with fallback for malformed output.

---

### Prompt 6 — Tool Call Tracer (Hook)
**Prompt:**
```
Implement a hook in backend/agents/tracer.py that logs every agent tool call to the ToolCallLog
database table. Function signature: log_tool_call(agent, tool, args, result, duration_ms).
Opens its own DB session so it doesn't interfere with the main request session.
```
**Result:** `log_tool_call()` writes to ToolCallLog. Called after every `investigate()` and `triage()` call in the investigation router with elapsed time in milliseconds.

---

### Prompt 7 — MCP Server
**Prompt:**
```
Build a Model Context Protocol server in backend/mcp_server/server.py that exposes three tools:
1. get_live_processes — returns top 10 processes by CPU from the DB
2. get_active_anomalies — returns all anomalies with status=active
3. get_anomaly_detail — returns full detail for a given anomaly_id
Use FastMCP. Mount it on the FastAPI app at /mcp.
```
**Result:** MCP server created with all three tools. Investigator system prompt references these tools as available for cross-referencing live data, making the investigation context richer.

---

### Prompt 8 — JWT Authentication
**Prompt:**
```
Add JWT auth to the FastAPI backend. Endpoints: POST /auth/register and POST /auth/login.
Use bcrypt for password hashing via passlib. Return a JWT token on login.
Protect all process and investigation endpoints with a get_current_user dependency.
Token expiry from ACCESS_TOKEN_EXPIRE_MINUTES env var.
```
**Result:** `auth.py` with `hash_password`, `verify_password`, `create_access_token`, `get_current_user`. Router with register + login endpoints.

**Correction applied:** Docker build failed with `ValueError: password cannot be longer than 72 bytes` — passlib incompatibility with bcrypt 4.1+. Fixed by pinning `bcrypt==4.0.1` in requirements.txt.

---

### Prompt 9 — API Tests
**Prompt:**
```
Write pytest tests for ProcessAI in backend/tests/test_api.py using pytest-asyncio.
Use an in-memory SQLite database with StaticPool so tests don't touch the real DB.
Cover: register, login, get processes (authenticated), get anomalies, trigger investigation.
Include a conftest.py with the test client fixture.
```
**Result:** Tests generated covering auth flow, 401 on missing token, processes and anomaly endpoints. Used `override_get_db` to inject in-memory DB.

**Correction applied:** Initial tests used `asyncio_mode = "auto"` but the app uses sync routes. Switched conftest to use `TestClient` (sync) rather than `AsyncClient`.

---

## Phase 3 · Week 6 (Frontend)

### Prompt 10 — React Dashboard
**Prompt:**
```
Build a React dashboard in Dashboard.jsx that polls GET /processes and GET /anomalies every 2 seconds.
Show a process table and an anomaly feed side by side. Include a login gate — if not authenticated,
show the login form. Store JWT in memory (not localStorage). Use fetch with Authorization header.
```
**Result:** Dashboard with 2-second polling, process table, anomaly cards, JWT state in React useState. Login/register toggle form.

---

### Prompt 11 — Live CPU Chart
**Prompt:**
```
Add a live CPU chart to the dashboard using recharts LineChart. Track the top 8 processes by CPU
over a 30-sample rolling window. Each process gets its own color line. Y-axis 0-100%.
Update every 2 seconds in sync with the process poll. Show in a card above the main panels.
```
**Result:** `CpuChart.jsx` with ResponsiveContainer, LineChart, 5 distinct colors, Legend. `processHistory` state in Dashboard keyed by "name:pid", rolling 30-sample window.

**Correction applied (1):** Initial implementation used `{...prev, ...next}` spread which kept old process keys as processes rotated out of top 8. Fixed: rebuild fresh `const next = {}` each poll, only keeping current top 8.

**Correction applied (2):** psutil reports per-core CPU on multi-core machines so values exceeded 100%. Fixed: `Math.min(p.cpu_pct, 100)` before appending to history.

---

### Prompt 12 — Anomaly Severity Grouping
**Prompt:**
```
In AnomalyFeed.jsx, group anomalies into HIGH (cpu >= 80%), MEDIUM (cpu >= 70%), LOW (everything else).
Render them in three sections with colored severity labels. HIGH section appears first.
Skip rendering a section entirely if it has no anomalies.
```
**Result:** `getSeverity()` and `groupBySeverity()` functions, three sections rendered conditionally with appropriate color labels (#dc2626 HIGH, #d97706 MEDIUM, #64748b LOW).

---

### Prompt 13 — Process Category Grouping
**Prompt:**
```
In ProcessTable.jsx, group processes into three categories: SYSTEM (kernel, svchost, csrss, etc.),
BROWSER (chrome, firefox, msedge, etc.), USER APPS (everything else).
Show a bold category header row before each non-empty group. Use sets of known process names
for classification.
```
**Result:** `SYSTEM_PROCS` and `BROWSER_PROCS` sets, `getCategory()` function, group headers rendered with `.proc-category-header` class.

---

### Prompt 14 — Light Mode UI Redesign
**Prompt:**
```
Redesign App.css to a clean minimalist light mode. Requirements:
- Background: #f5f7fa (off-white)
- Panels: #ffffff with subtle border and box shadow
- Accent: teal #0d9488
- No dark backgrounds anywhere
- Login page: centered card 400px wide, labels above inputs, teal Sign In button
- Clean sans-serif typography
Remove all dark mode colors.
```
**Result:** Full CSS rewrite. `.login-card`, `.chart-panel`, `.proc-category-header`, `.btn-investigate`, severity label colors all updated to light mode palette.

---

## Phase 3 · Week 7 (Advanced Features)

### Prompt 15 — Email Alerts
**Prompt:**
```
Add email alerting to ProcessAI. When a new HIGH anomaly is detected (cpu >= 80%),
send an HTML alert email via Gmail SMTP (port 587, STARTTLS).
Create backend/mailer.py with send_alert(process_name, pid, cpu_pct, mem_pct, duration_secs).
Read SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL from environment. Never raise — catch all errors and log.
Call it from monitor.py in a daemon thread so it doesn't block sampling.
```
**Result:** `mailer.py` with HTML email template, SMTP guard for missing config, all errors caught and logged. Monitor spawns daemon thread for each HIGH anomaly creation.

**Correction applied:** Initial .env had SMTP_USER set to a short username instead of full Gmail address, and used the regular account password instead of a Google App Password. Fixed after generating a 16-char App Password from myaccount.google.com/apppasswords.

---

### Prompt 16 — Docker Containerization
**Prompt:**
```
Containerize ProcessAI with Docker. Create:
1. backend/Dockerfile: python:3.11-slim, install requirements, run uvicorn on 0.0.0.0:8000
2. frontend/Dockerfile: multi-stage — node:20-slim build stage, then nginx:alpine to serve dist/
3. frontend/nginx.conf: try_files for React Router, gzip for JS/CSS/JSON/SVG
4. docker-compose.yml: backend on 8000, frontend on 5174->80, shared bridge network,
   env_file for backend, named volume for processai.db
5. .dockerignore: exclude node_modules, __pycache__, .env, *.db, dist
```
**Result:** All five files generated. Docker Compose brings up both services with a single `docker compose up --build`.

**Correction applied:** After first `docker compose up`, "Failed to fetch" appeared on login — two backends running simultaneously (local uvicorn still on port 8000 AND Docker). Fixed by killing the local process: `taskkill /F /PID <pid>`.

---

### Prompt 17 — SQLite Concurrency Fix
**Prompt:**
```
The backend crashes with "database is locked" when many anomalies are written simultaneously
(8+ CPU-burning processes all qualifying at once). Fix the SQLite engine configuration to handle
concurrent writes gracefully without changing to PostgreSQL.
```
**Result:** Added `"timeout": 20` to `connect_args` in `database.py`. SQLite will now wait up to 20 seconds for a lock instead of failing immediately.

---

### Prompt 18 — Demo Stress Script
**Prompt:**
```
Write a stress script in stress_demo.py that spawns 10 CPU-burning worker subprocesses.
Each worker runs a tight math loop. Main process prints alive worker count every 2 seconds.
Ctrl+C cleanly terminates all workers. Anomalies should appear on the dashboard within ~10 seconds.
Also lower QUALIFICATION_COUNT from 10 to 5 in constants.py for faster demo qualification.
```
**Result:** `stress_demo.py` spawns workers using `subprocess.Popen([sys.executable, __file__, "--worker"])`. Self-referential entry point with `--worker` flag. `QUALIFICATION_COUNT = 5` in constants.py reduces qualification time to 10 seconds.

---

## AI Coding Ground Rules — Applied Throughout

- Every AI-generated plan was reviewed before implementation
- When AI output was wrong, the correction is documented above (see "Correction applied" notes)
- Small, verifiable steps preferred over large one-shot generations — each feature built and tested before moving to the next
- AI used for: scaffold generation, boilerplate, test writing, CSS, Docker config, debugging suggestions
- Developer verified: business logic correctness, API contract, security (JWT, bcrypt), data flow

---

## Model Usage Summary

| Agent | Model | Provider | Purpose |
|---|---|---|---|
| Triage | `meta-llama/llama-3.1-8b-instruct:free` | OpenRouter | Fast first-pass severity classification |
| Investigator | `claude-haiku-4-5-20251001` | Anthropic | Deep analysis, findings + recommendation |
| Code generation | Claude Code (claude-sonnet) | Anthropic | All scaffolding, refactoring, debugging |
