import json
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Anomaly, Investigation, User
from schemas import InvestigationOut
from auth import get_current_user
from agents.investigator import investigate
from agents.tracer import log_tool_call
from constants import MODEL as DEEP_MODEL

router = APIRouter(prefix="/investigations", tags=["investigations"])

@router.post("/{anomaly_id}", response_model=InvestigationOut, status_code=status.HTTP_201_CREATED)
def trigger_investigation(
    anomaly_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    anomaly = db.get(Anomaly, anomaly_id)
    if not anomaly:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anomaly not found")
    if anomaly.status != "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Anomaly is {anomaly.status}")

    anomaly.status = "investigating"
    db.commit()

    deep_args = {"pid": anomaly.pid, "name": anomaly.process_name, "cpu_pct": anomaly.cpu_pct}
    t0 = time.monotonic()
    deep = investigate(anomaly)
    log_tool_call("investigator", "investigate", deep_args, json.dumps(deep), int((time.monotonic() - t0) * 1000))

    inv = Investigation(
        anomaly_id=anomaly.id,
        findings=deep.get("findings"),
        recommendation=deep.get("recommendation"),
        confidence=deep.get("confidence"),
        model_used=DEEP_MODEL,
    )

    db.add(inv)
    anomaly.status = "resolved"
    db.commit()
    db.refresh(inv)
    return inv

@router.get("/{anomaly_id}", response_model=InvestigationOut)
def get_investigation(anomaly_id: int, db: Session = Depends(get_db)):
    inv = (
        db.query(Investigation)
        .filter(Investigation.anomaly_id == anomaly_id)
        .order_by(Investigation.id.desc())
        .first()
    )
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No investigation found")
    return inv
