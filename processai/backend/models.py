from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Anomaly(Base):
    __tablename__ = "anomalies"
    id = Column(Integer, primary_key=True, index=True)
    pid = Column(Integer, nullable=False)
    process_name = Column(String, nullable=False)
    anomaly_type = Column(String, nullable=False)
    cpu_pct = Column(Float)
    mem_pct = Column(Float)
    consecutive_count = Column(Integer, default=0)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")

class Investigation(Base):
    __tablename__ = "investigations"
    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(Integer, ForeignKey("anomalies.id"), nullable=False)
    findings = Column(String)
    recommendation = Column(String)
    confidence = Column(Float)
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
