import psutil
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from models import Anomaly, User
from schemas import ProcessOut, AnomalyOut
from auth import get_current_user

router = APIRouter(tags=["processes"])

@router.get("/processes", response_model=list[ProcessOut])
def get_processes(_: User = Depends(get_current_user)):
    procs = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            if info["pid"] == 0:
                continue
            procs.append(ProcessOut(
                pid=info["pid"],
                name=info["name"] or "",
                cpu_pct=info["cpu_percent"] or 0.0,
                mem_pct=info["memory_percent"] or 0.0,
            ))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda p: p.cpu_pct, reverse=True)
    return procs[:30]

@router.get("/anomalies", response_model=list[AnomalyOut])
def get_anomalies(db: Session = Depends(get_db)):
    return (
        db.query(Anomaly)
        .filter(Anomaly.status == "active")
        .order_by(Anomaly.consecutive_count.desc())
        .limit(10)
        .all()
    )


@router.delete("/anomalies/clear", status_code=status.HTTP_200_OK)
def clear_anomalies(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    db.query(Anomaly).filter(Anomaly.status == "active").update({"status": "resolved"})
    db.commit()
    return {"cleared": True}
