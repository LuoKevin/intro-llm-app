from __future__ import annotations
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.llm.generate import answer_question

router = APIRouter()

class ChatResponse(BaseModel):
    answer: str
    citations: list[dict]

@router.get("/chat", response_model=ChatResponse)
def chat(msg: str = Query(...,min_length=1), top_k: int = 5):
    result = answer_question(msg, top_k=top_k)
    return ChatResponse(**result)