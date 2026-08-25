import json
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Anomaly, Investigation, User
from schemas import InvestigationOut
from auth import get_current_user
from agents.triage import triage
from agents.investigator import investigate
from agents.tracer import log_tool_call
from constants import MODEL as DEEP_MODEL

TRIAGE_MODEL_NAME = "llama-3.1-8b (triage only)"

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

    # ── Step 1: Triage (Llama 3.1 8B via OpenRouter) ──────────────────────────
    t0 = time.monotonic()
    triage_result = triage(anomaly)
    log_tool_call(
        "triage", "classify",
        {"pid": anomaly.pid, "name": anomaly.process_name, "cpu_pct": anomaly.cpu_pct},
        json.dumps(triage_result),
        int((time.monotonic() - t0) * 1000),
    )

    needs_deep = triage_result.get("needs_deep_investigation", True)

    # ── Step 2: Deep investigation (Claude Haiku + MCP tools) — if warranted ──
    if needs_deep:
        t1 = time.monotonic()
        deep = investigate(anomaly)
        log_tool_call(
            "investigator", "investigate",
            {"pid": anomaly.pid, "name": anomaly.process_name, "cpu_pct": anomaly.cpu_pct},
            json.dumps(deep),
            int((time.monotonic() - t1) * 1000),
        )
        model_used = DEEP_MODEL
    else:
        # Triage decided this is low severity — no deep investigation needed
        deep = {
            "findings": f"[Triage only] {triage_result.get('summary', 'Low severity anomaly — no unusual patterns detected.')}",
            "recommendation": "No immediate action required. Continue monitoring.",
            "confidence": 0.6,
        }
        model_used = TRIAGE_MODEL_NAME

    inv = Investigation(
        anomaly_id=anomaly.id,
        findings=deep.get("findings"),
        recommendation=deep.get("recommendation"),
        confidence=deep.get("confidence"),
        model_used=model_used,
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
