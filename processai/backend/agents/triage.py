import json
import requests
from constants import OPENROUTER_API_KEY

TRIAGE_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
_URL = "https://openrouter.ai/api/v1/chat/completions"

def _strip_fences(text: str) -> str:
    return text.replace("```json", "").replace("```", "").strip()

def triage(anomaly) -> dict:
    duration_s = anomaly.consecutive_count * 2
    prompt = (
        f"You are a fast triage agent for process anomalies.\n\n"
        f"Process: {anomaly.process_name} (PID {anomaly.pid})\n"
        f"Anomaly type: {anomaly.anomaly_type}\n"
        f"CPU usage: {anomaly.cpu_pct:.1f}%\n"
        f"Memory usage: {anomaly.mem_pct:.2f}%\n"
        f"Duration flagged: {duration_s} seconds\n\n"
        f"Return ONLY valid JSON with this exact structure:\n"
        f'{{"severity": "low", "summary": "one sentence", "needs_deep_investigation": false}}\n\n'
        f'severity must be "low", "medium", or "high".\n'
        f"needs_deep_investigation should be true only for high severity or unusual patterns."
    )
    try:
        resp = requests.post(
            _URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": TRIAGE_MODEL,
                "max_tokens": 150,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=3,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip()
        return json.loads(_strip_fences(raw))
    except Exception:
        return {"severity": "high", "summary": "Triage unavailable; escalating to full investigation.", "needs_deep_investigation": True}
