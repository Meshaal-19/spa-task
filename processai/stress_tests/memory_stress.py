import ctypes
import sys
import time

if sys.platform == "win32":
    ctypes.windll.kernel32.SetConsoleTitleW("[MEM-STRESS]")

DURATION = 300
CHUNK_MB = 50
INTERVAL = 2

print(f"[memory_stress] Starting memory growth for {DURATION} seconds (+{CHUNK_MB}MB every {INTERVAL}s)...")

chunks = []
start = time.time()

while time.time() - start < DURATION:
    chunks.append(b"x" * (CHUNK_MB * 1024 * 1024))
    total_mb = len(chunks) * CHUNK_MB
    print(f"[memory_stress] Allocated {total_mb}MB total")
    time.sleep(INTERVAL)

print("[memory_stress] Done.")
