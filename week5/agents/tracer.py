from datetime import datetime
from constants import SEPARATOR_WIDTH


def log_tool_call(
    agent_name: str,
    tool_name: str,
    args: dict,
    result: str,
    latency_ms: int,
) -> None:
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    preview = str(result)[:120].replace("\n", " ")
    print(
        f"[{ts}] AGENT={agent_name} TOOL={tool_name} "
        f"ARGS={args} RESULT_PREVIEW={preview!r} LATENCY={latency_ms}ms"
    )


def print_header(title: str) -> None:
    print(f"\n{'='*SEPARATOR_WIDTH}")
    print(title)
    print(f"{'='*SEPARATOR_WIDTH}")
