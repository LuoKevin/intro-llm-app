from fastapi import FastAPI
from app.core.config import settings

app = FastAPI()

@app.get("/healthz")
def health():
    return {"status": "ok", "env": settings.app_env}

@app.get("/chat")
def chat(msg: str):
    return {"response": f"Echo: {msg}"}
