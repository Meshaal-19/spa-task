import sys
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE, ".env"))
sys.path.insert(0, BASE)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from monitor import start_monitor
from routers.auth import router as auth_router
from routers.processes import router as processes_router
from routers.investigations import router as investigations_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_monitor()
    yield

app = FastAPI(title="ProcessAI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(processes_router)
app.include_router(investigations_router)


@app.get("/health")
def health():
    return {"status": "ok"}
