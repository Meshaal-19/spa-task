import threading
import time
import psutil
from collections import deque
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Anomaly
from constants import CPU_THRESHOLD, SAMPLE_INTERVAL, QUALIFICATION_COUNT
from mailer import send_alert

_HIGH_CPU_THRESHOLD = 80.0

_SKIP_NAMES = {"System Idle Process", "System"}
_cpu_counts: dict = {}
_mem_history: dict = {}

def _sample_once():
    db = SessionLocal()
    try:
        seen_pids = set()
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = proc.info
                pid = info["pid"]
                if pid == 0 or info["name"] in _SKIP_NAMES:
                    continue
                seen_pids.add(pid)
                _process_proc(db, info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        for pid in list(_cpu_counts):
            if pid not in seen_pids:
                del _cpu_counts[pid]
        for pid in list(_mem_history):
            if pid not in seen_pids:
                del _mem_history[pid]
        _cleanup_stale(db, seen_pids)
    finally:
        db.close()

def _process_proc(db: Session, info: dict):
    pid = info["pid"]
    name = info["name"] or ""
    cpu = info["cpu_percent"] or 0.0
    mem = info["memory_percent"] or 0.0
    _check_cpu(db, pid, name, cpu, mem)
    _check_memory(db, pid, name, cpu, mem)

def _check_cpu(db: Session, pid: int, name: str, cpu: float, mem: float):
    if cpu > CPU_THRESHOLD:
        _cpu_counts[pid] = _cpu_counts.get(pid, 0) + 1
        if _cpu_counts[pid] >= QUALIFICATION_COUNT:
            _upsert_anomaly(db, pid, name, "cpu", cpu, mem, _cpu_counts[pid])
    else:
        _cpu_counts.pop(pid, None)

def _check_memory(db: Session, pid: int, name: str, cpu: float, mem: float):
    if pid not in _mem_history:
        _mem_history[pid] = deque(maxlen=QUALIFICATION_COUNT)
    _mem_history[pid].append(mem)
    if len(_mem_history[pid]) == QUALIFICATION_COUNT:
        vals = list(_mem_history[pid])
        if all(vals[i] < vals[i + 1] for i in range(QUALIFICATION_COUNT - 1)):
            _upsert_anomaly(db, pid, name, "memory", cpu, mem, QUALIFICATION_COUNT)

def _upsert_anomaly(db: Session, pid: int, name: str, anomaly_type: str, cpu: float, mem: float, count: int):
    existing = (
        db.query(Anomaly)
        .filter(Anomaly.pid == pid, Anomaly.anomaly_type == anomaly_type, Anomaly.status == "active")
        .first()
    )
    now = datetime.utcnow()
    if existing:
        existing.last_seen = now
        existing.consecutive_count = count
        existing.cpu_pct = cpu
        existing.mem_pct = mem
    else:
        db.add(Anomaly(
            pid=pid,
            process_name=name,
            anomaly_type=anomaly_type,
            cpu_pct=cpu,
            mem_pct=mem,
            consecutive_count=count,
            first_seen=now,
            last_seen=now,
            status="active",
        ))
        if cpu >= _HIGH_CPU_THRESHOLD:
            duration = count * SAMPLE_INTERVAL
            threading.Thread(
                target=send_alert,
                args=(name, pid, cpu, mem, duration),
                daemon=True,
            ).start()
    db.commit()

def _cleanup_stale(db: Session, seen_pids: set):
    if not seen_pids:
        return
    stale = (
        db.query(Anomaly)
        .filter(Anomaly.status == "active", ~Anomaly.pid.in_(seen_pids))
        .all()
    )
    for anomaly in stale:
        anomaly.status = "resolved"
    if stale:
        db.commit()

def start_monitor():
    def loop():
        psutil.cpu_percent(interval=None)
        while True:
            _sample_once()
            time.sleep(SAMPLE_INTERVAL)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    return thread
