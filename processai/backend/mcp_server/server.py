import sys
from pathlib import Path
from dotenv import load_dotenv

_BACKEND = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND / ".env")
sys.path.insert(0, str(_BACKEND))

import psutil
from mcp.server.fastmcp import FastMCP
from database import SessionLocal
from models import Anomaly, Investigation

mcp = FastMCP("ProcessAI Monitor")

@mcp.tool()
def get_live_processes() -> list[dict]:
    """Top 20 processes by CPU usage, sampled live from psutil."""
    procs = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            if info["pid"] == 0:
                continue
            procs.append({
                "pid": info["pid"],
                "name": info["name"] or "",
                "cpu_pct": round(info["cpu_percent"] or 0.0, 2),
                "mem_pct": round(info["memory_percent"] or 0.0, 4),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda p: p["cpu_pct"], reverse=True)
    return procs[:20]

@mcp.tool()
def get_active_anomalies() -> list[dict]:
    """All anomalies currently marked active in the database."""
    db = SessionLocal()
    try:
        rows = db.query(Anomaly).filter(Anomaly.status == "active").all()
        return [
            {
                "id": r.id,
                "pid": r.pid,
                "name": r.process_name,
                "anomaly_type": r.anomaly_type,
                "cpu_pct": r.cpu_pct,
                "mem_pct": r.mem_pct,
                "consecutive_count": r.consecutive_count,
            }
            for r in rows
        ]
    finally:
        db.close()

@mcp.tool()
def get_anomaly_detail(anomaly_id: int) -> dict:
    """Full detail for one anomaly including its latest investigation result if any."""
    db = SessionLocal()
    try:
        anomaly = db.get(Anomaly, anomaly_id)
        if not anomaly:
            return {"error": f"Anomaly {anomaly_id} not found"}
        inv = (
            db.query(Investigation)
            .filter(Investigation.anomaly_id == anomaly_id)
            .order_by(Investigation.id.desc())
            .first()
        )
        result = {
            "id": anomaly.id,
            "pid": anomaly.pid,
            "process_name": anomaly.process_name,
            "anomaly_type": anomaly.anomaly_type,
            "cpu_pct": anomaly.cpu_pct,
            "mem_pct": anomaly.mem_pct,
            "consecutive_count": anomaly.consecutive_count,
            "status": anomaly.status,
            "first_seen": anomaly.first_seen.isoformat() if anomaly.first_seen else None,
            "last_seen": anomaly.last_seen.isoformat() if anomaly.last_seen else None,
            "investigation": None,
        }
        if inv:
            result["investigation"] = {
                "id": inv.id,
                "findings": inv.findings,
                "recommendation": inv.recommendation,
                "confidence": inv.confidence,
                "model_used": inv.model_used,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
            }
        return result
    finally:
        db.close()
