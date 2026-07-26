import sys
import os
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE, ".env"))

sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "mcp_server"))
sys.path.insert(0, os.path.join(BASE, "agents"))

from data import INCIDENT
from supervisor import run_supervisor
from tracer import print_header


def main():
    print_header("INCIDENT INVESTIGATION — MULTI-AGENT SYSTEM")
    print(f"\nIncident : {INCIDENT['title']}")
    print(f"Severity : {INCIDENT['severity']}")
    print(f"Started  : {INCIDENT['started_at']}")

    report = run_supervisor(INCIDENT)

    print_header("FINAL INCIDENT REPORT")
    print(report)


if __name__ == "__main__":
    main()
