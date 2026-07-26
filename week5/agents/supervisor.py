import json
import time
from anthropic import Anthropic
from worker import Worker
from tracer import log_tool_call, print_header
from data import LOGS, METRICS
from constants import MODEL, SUPERVISOR_MAX_TOKENS

client = Anthropic()

_LOG_TOOLS = [
    {
        "name": "query_logs",
        "description": "Query incident logs filtered by severity (info, warning, error).",
        "input_schema": {
            "type": "object",
            "properties": {
                "severity": {
                    "type": "string",
                    "description": "Severity level: info, warning, or error",
                    "enum": ["info", "warning", "error"],
                }
            },
            "required": ["severity"],
        },
    }
]


def _log_executor(name: str, args: dict) -> str:
    if name == "query_logs":
        severity = args.get("severity", "error").lower()
        filtered = [e for e in LOGS if e["severity"] == severity]
        return json.dumps(filtered, indent=2)
    return f"Unknown tool: {name}"


log_worker = Worker(
    name="LogInvestigator",
    specialty="log analysis",
    tools=_LOG_TOOLS,
    tool_executor=_log_executor,
)

_METRIC_TOOLS = [
    {
        "name": "get_metrics",
        "description": "Retrieve time-series metrics for the incident window.",
        "input_schema": {
            "type": "object",
            "properties": {
                "metric_name": {
                    "type": "string",
                    "description": "Metric: error_rate, latency_p99_ms, or pod_count",
                    "enum": ["error_rate", "latency_p99_ms", "pod_count"],
                }
            },
            "required": ["metric_name"],
        },
    }
]


def _metrics_executor(name: str, args: dict) -> str:
    if name == "get_metrics":
        metric = args.get("metric_name")
        data = METRICS.get(metric)
        if data is None:
            return f"Unknown metric: {metric}"
        return json.dumps({"metric": metric, "data": data}, indent=2)
    return f"Unknown tool: {name}"


metrics_worker = Worker(
    name="MetricsInvestigator",
    specialty="metrics analysis",
    tools=_METRIC_TOOLS,
    tool_executor=_metrics_executor,
)

_SUPERVISOR_TOOLS = [
    {
        "name": "investigate_logs",
        "description": "Dispatch the Log Investigator worker to query and analyze incident logs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Investigation task description for the log worker",
                }
            },
            "required": ["task"],
        },
    },
    {
        "name": "investigate_metrics",
        "description": "Dispatch the Metrics Investigator worker to analyze incident metrics.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Investigation task description for the metrics worker",
                }
            },
            "required": ["task"],
        },
    },
]


def _dispatch(tool_name: str, args: dict) -> str:
    if tool_name == "investigate_logs":
        return log_worker.run(args["task"])
    if tool_name == "investigate_metrics":
        return metrics_worker.run(args["task"])
    return f"Unknown worker: {tool_name}"


def run_supervisor(incident: dict) -> str:
    incident_text = json.dumps(incident, indent=2)
    system = (
        "You are an incident commander. Dispatch your specialist workers to investigate "
        "this production incident, then synthesize a final report covering: root cause, "
        "timeline, and recommended action."
    )
    messages = [
        {
            "role": "user",
            "content": f"Investigate this production incident:\n\n{incident_text}",
        }
    ]

    print_header("SUPERVISOR: Starting investigation")

    for _ in range(6):
        response = client.messages.create(
            model=MODEL,
            max_tokens=SUPERVISOR_MAX_TOKENS,
            system=system,
            tools=_SUPERVISOR_TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print_header(f"SUPERVISOR: Dispatching {block.name}")
                    start = time.time()
                    result = _dispatch(block.name, block.input)
                    latency_ms = int((time.time() - start) * 1000)
                    log_tool_call("Supervisor", block.name, block.input, result, latency_ms)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return ""
