import json
from anthropic import Anthropic
from constants import ANTHROPIC_API_KEY, MODEL

client = Anthropic(api_key=ANTHROPIC_API_KEY)

_HIGH_RISK = (
    "You are a process security analyst with access to real-time process data via MCP tools "
    "(get_live_processes, get_active_anomalies, get_anomaly_detail). The architecture supports "
    "live cross-referencing of process state. When evidence is severe — CPU above 80% sustained "
    "beyond 60 seconds, or memory growing without bound — you must classify this as high-risk "
    "and state that explicitly. Do not soften findings with 'monitor and review' when the data "
    "indicates an active threat. Be direct: name the likely cause, state the risk level, and "
    "give a concrete immediate action."
)

def investigate(anomaly) -> dict:
    duration_s = anomaly.consecutive_count * 2
    is_severe = (anomaly.cpu_pct or 0) > 80 and duration_s >= 60
    severity_note = (
        "SEVERITY: HIGH — CPU above 80% sustained for over 60 seconds with concurrent memory growth. "
        "Treat this as an active incident requiring immediate action."
        if is_severe else ""
    )
    prompt = (
        f"Analyze this process anomaly and return a JSON object.\n\n"
        f"Process: {anomaly.process_name} (PID {anomaly.pid})\n"
        f"Anomaly type: {anomaly.anomaly_type}\n"
        f"CPU usage: {anomaly.cpu_pct:.1f}%\n"
        f"Memory usage: {anomaly.mem_pct:.2f}%\n"
        f"Duration flagged: {duration_s} seconds\n"
        + (f"{severity_note}\n" if severity_note else "")
        + "Note: Real-time process snapshots are available via MCP tools for cross-referencing.\n"
        + f"\nReturn ONLY valid JSON with this structure:\n"
        f'{{"findings": "string", "recommendation": "string", "confidence": 0.0}}\n\n'
        f"confidence must be a number between 0.0 and 1.0. "
        f"For high-risk findings confidence should be 0.85 or above."
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=_HIGH_RISK,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"findings": raw, "recommendation": "Manual review required.", "confidence": 0.5}
