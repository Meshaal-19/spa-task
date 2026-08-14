import ctypes
import sys
import time
import math
import threading

if sys.platform == "win32":
    ctypes.windll.kernel32.SetConsoleTitleW("[COMBINED-STRESS]")

DURATION = 300
CHUNK_MB = 100
MEM_INTERVAL = 3
STATUS_INTERVAL = 30

print("[COMBINED-STRESS] Simulating catastrophic process behavior...")
print(f"[COMBINED-STRESS] Duration: {DURATION}s | +{CHUNK_MB}MB every {MEM_INTERVAL}s")

_allocated_mb = 0
_allocated_lock = threading.Lock()

def cpu_burn():
    x = 0.0
    end = time.time() + DURATION
    while time.time() < end:
        x = math.sqrt(x * x + 1.0001)

def memory_grow():
    global _allocated_mb
    chunks = []
    start = time.time()
    while time.time() - start < DURATION:
        chunks.append(b"x" * (CHUNK_MB * 1024 * 1024))
        with _allocated_lock:
            _allocated_mb = len(chunks) * CHUNK_MB
        print(f"[COMBINED-STRESS] Total allocated: {_allocated_mb} MB")
        time.sleep(MEM_INTERVAL)

def status_reporter():
    start = time.time()
    next_report = STATUS_INTERVAL
    while True:
        elapsed = time.time() - start
        if elapsed >= DURATION:
            break
        if elapsed >= next_report:
            with _allocated_lock:
                mb = _allocated_mb
            print(f"[COMBINED-STRESS] Still running — {int(elapsed)}s elapsed, {mb} MB allocated")
            next_report += STATUS_INTERVAL
        time.sleep(1)

t_mem = threading.Thread(target=memory_grow, daemon=True)
t_status = threading.Thread(target=status_reporter, daemon=True)

t_mem.start()
t_status.start()

cpu_burn()

t_mem.join()
t_status.join()

print("[COMBINED-STRESS] Done.")
