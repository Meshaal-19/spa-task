import json
import time
from pathlib import Path

_LOG = Path(__file__).resolve().parent.parent / "trace.log"

def log_tool_call(agent: str, tool: str, args: dict, result: str, latency_ms: int):
    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "agent": agent,
        "tool": tool,
        "args": args,
        "result": result,
        "latency_ms": latency_ms,
    }
    with _LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
