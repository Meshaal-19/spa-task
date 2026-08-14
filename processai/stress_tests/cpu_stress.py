import ctypes
import sys
import time
import math

if sys.platform == "win32":
    ctypes.windll.kernel32.SetConsoleTitleW("[CPU-STRESS]")

DURATION = 300
REPORT_INTERVAL = 10

print(f"[cpu_stress] Starting CPU burn for {DURATION} seconds...")

start = time.time()
last_report = start
x = 0.0

while True:
    now = time.time()
    elapsed = now - start
    if elapsed >= DURATION:
        break
    if now - last_report >= REPORT_INTERVAL:
        print(f"[cpu_stress] {int(elapsed)}s elapsed...")
        last_report = now
    x = math.sqrt(x * x + 1.0001)

print("[cpu_stress] Done.")
