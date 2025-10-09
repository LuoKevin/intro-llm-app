from fastapi import FastAPI

app = FastAPI()

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.get("/chat")
def chat(msg: str):
    return {"response": f"Echo: {msg}"}

