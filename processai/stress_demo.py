"""
Demo stress script — spawns CPU-burning worker processes to flood the
ProcessAI anomaly feed. Run from the processai/ directory:

    python stress_demo.py

Workers run until you press Ctrl+C.
"""
import subprocess
import sys
import time

WORKERS = 10

def _burn():
    while True:
        x = 0
        for i in range(10 ** 7):
            x += i * i

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--worker":
        _burn()

    procs = []
    print(f"Starting {WORKERS} CPU-burn workers...")
    for i in range(WORKERS):
        p = subprocess.Popen([sys.executable, __file__, "--worker"])
        procs.append(p)
        print(f"  Worker {i + 1:>2}  PID {p.pid}")

    print(f"\n{WORKERS} workers running. Anomalies appear in ~10s.")
    print("Press Ctrl+C to kill all workers.\n")

    try:
        while True:
            alive = sum(1 for p in procs if p.poll() is None)
            print(f"\r  {alive}/{WORKERS} workers alive", end="", flush=True)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        for p in procs:
            p.terminate()
        for p in procs:
            p.wait()
        print("All workers stopped.")
