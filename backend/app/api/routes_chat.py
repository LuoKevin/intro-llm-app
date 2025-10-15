from __future__ import annotations
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
import asyncio
from pydantic import BaseModel
from app.llm.generate import answer_question, stream_answer

router = APIRouter()

class ChatResponse(BaseModel):
    answer: str
    citations: list[dict]

@router.get("/chat", response_model=ChatResponse)
def chat(msg: str = Query(...,min_length=1), top_k: int = 5):
    result = answer_question(msg, top_k=top_k)
    return ChatResponse(**result)

@router.get("/chat/stream")
def chat_stream(msg: str = Query(..., min_length=1), top_k: int = 5):
    return StreamingResponse(
        stream_answer(msg, top_k=top_k),
        media_type="text/event-stream",
        headers={
            "Cache-control": "no-cache",
            "X-Accel-Buffering": "no", #disables proxy buffering
        }
    )

@router.get("/debug/stream")
def debug_stream():
    async def gen():
        for i in range(10):
            yield f"data: tick {i}\n\n"
            await asyncio.sleep(0.2)
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})