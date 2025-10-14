from fastapi import FastAPI
from app.api.routes_chat import router as chat_router
from app.core.config import settings

app = FastAPI()
app.include_router(chat_router)

@app.get("/healthz")
def health():
    return {"status": "ok", "env": settings.app_env}

@app.get("/chat")
def chat(msg: str):
    return {"response": f"Echo: {msg}"}
