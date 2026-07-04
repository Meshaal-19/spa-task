from fastapi import FastAPI

from database import Base, engine
from routers import auth, notes, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notes.router)
