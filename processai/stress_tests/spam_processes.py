"""
ProcessAI — Process Spammer
Spawns multiple CPU-burning subprocesses to flood the dashboard
with anomalies for demo/video recording.
"""

import subprocess
import sys
import time
import math
import os

WORKER_COUNT = 8
DURATION = 300

WORKER_SCRIPT = """
import math, time, sys
duration = int(sys.argv[1])
deadline = time.time() + duration
while time.time() < deadline:
    math.sqrt(999999999 * 99999)
"""

def run_workers():
    procs = []
    print(f"Spawning {WORKER_COUNT} CPU worker processes...")

    for i in range(WORKER_COUNT):
        p = subprocess.Popen(
            [sys.executable, "-c", WORKER_SCRIPT, str(DURATION)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        procs.append(p)
        print(f"  Worker {i+1} started — PID {p.pid}")
        time.sleep(0.3)

    print(f"\nAll {WORKER_COUNT} workers running.")
    print("Open ProcessAI dashboard — anomalies will appear in ~20 seconds.")
    print(f"Running for {DURATION}s. Press Ctrl+C to stop early.\n")

    start = time.time()
    try:
        while True:
            elapsed = int(time.time() - start)
            alive = sum(1 for p in procs if p.poll() is None)
            print(f"[{elapsed:>4}s] {alive}/{WORKER_COUNT} workers alive", end="\r")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nStopping all workers...")

    for p in procs:
        try:
            p.terminate()
        except Exception:
            pass

    print("Done.")

if __name__ == "__main__":
    run_workers()
