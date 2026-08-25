from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProcessOut(BaseModel):
    pid: int
    name: str
    cpu_pct: float
    mem_pct: float

class AnomalyOut(BaseModel):
    id: int
    pid: int
    process_name: str
    anomaly_type: str
    cpu_pct: Optional[float]
    mem_pct: Optional[float]
    consecutive_count: int
    first_seen: datetime
    last_seen: datetime
    status: str

    model_config = {"from_attributes": True}

class InvestigationOut(BaseModel):
    id: int
    anomaly_id: int
    findings: Optional[str]
    recommendation: Optional[str]
    confidence: Optional[float]
    model_used: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
