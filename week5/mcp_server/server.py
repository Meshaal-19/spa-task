import json
import sys
import os
from mcp.server.fastmcp import FastMCP

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import INCIDENT, LOGS

mcp = FastMCP("incident-investigation")


@mcp.resource("incident://current")
def get_current_incident() -> str:
    """The active incident under investigation."""
    return json.dumps(INCIDENT, indent=2)


@mcp.tool()
def query_logs(severity: str) -> str:
    """
    Return incident log entries filtered by severity level.

    Args:
        severity: One of 'info', 'warning', or 'error'
    """
    filtered = [entry for entry in LOGS if entry["severity"] == severity.lower()]
    return json.dumps(filtered, indent=2)


if __name__ == "__main__":
    mcp.run()
