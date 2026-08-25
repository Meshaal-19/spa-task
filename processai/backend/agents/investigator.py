import json
import time
from anthropic import Anthropic
from constants import ANTHROPIC_API_KEY, MODEL
from agents.tracer import log_tool_call

# Import MCP tool implementations directly — same functions the MCP server exposes
from mcp_server.server import get_live_processes, get_active_anomalies, get_anomaly_detail

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Anthropic tool definitions matching the MCP server tools
TOOLS = [
    {
        "name": "get_live_processes",
        "description": "Get the top 20 processes by CPU usage, sampled live from the OS right now.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_active_anomalies",
        "description": "Get all anomalies currently marked active in the database.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_anomaly_detail",
        "description": "Get full detail for one anomaly by its database ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "anomaly_id": {"type": "integer", "description": "The anomaly ID to look up."}
            },
            "required": ["anomaly_id"],
        },
    },
]

def _dispatch(name: str, inputs: dict):
    if name == "get_live_processes":
        return get_live_processes()
    if name == "get_active_anomalies":
        return get_active_anomalies()
    if name == "get_anomaly_detail":
        return get_anomaly_detail(inputs["anomaly_id"])
    return {"error": f"Unknown tool: {name}"}

_SYSTEM = (
    "You are a process security analyst. Use the available tools to cross-reference the "
    "anomaly with live system state before writing your analysis. Be direct: name the likely "
    "cause, state the risk level, and give a concrete immediate action. When CPU is above 80% "
    "sustained beyond 60 seconds, classify as HIGH risk — do not soften with 'monitor and review'."
)

def investigate(anomaly) -> dict:
    duration_s = anomaly.consecutive_count * 2

    user_msg = (
        f"Analyze this process anomaly. Use the tools to check live system state first.\n\n"
        f"Process: {anomaly.process_name} (PID {anomaly.pid})\n"
        f"Anomaly type: {anomaly.anomaly_type}\n"
        f"CPU usage: {anomaly.cpu_pct:.1f}%\n"
        f"Memory usage: {anomaly.mem_pct:.2f}%\n"
        f"Duration flagged: {duration_s} seconds\n\n"
        f"After using tools, return ONLY valid JSON:\n"
        f'{{"findings": "string", "recommendation": "string", "confidence": 0.0}}\n'
        f"confidence must be between 0.0 and 1.0."
    )

    messages = [{"role": "user", "content": user_msg}]

    # Agentic loop — up to 5 rounds of tool calls
    for _ in range(5):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=_SYSTEM,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    raw = block.text.strip()
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError:
                        return {"findings": raw, "recommendation": "Manual review required.", "confidence": 0.5}
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    t0 = time.monotonic()
                    result = _dispatch(block.name, block.input)
                    latency = int((time.monotonic() - t0) * 1000)
                    log_tool_call("investigator", block.name, block.input, json.dumps(result), latency)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return {"findings": "Investigation did not complete.", "recommendation": "Manual review required.", "confidence": 0.3}
