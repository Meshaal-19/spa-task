from datetime import datetime

LOG_FILE = "agent_log.txt"


def _log(line: str) -> None:
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def before_tool_call(tool_name: str, input: dict) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    _log(f"[{ts}] BEFORE  {tool_name}  input={input}")


def after_tool_call(tool_name: str, output: str, duration_ms: int) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    short_output = output[:100].replace("\n", " ")
    _log(f"[{ts}] AFTER   {tool_name}  {duration_ms}ms  output={short_output!r}")
