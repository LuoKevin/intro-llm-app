from __future__ import annotations
from pathlib import Path
from typing import TypedDict, Iterator
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.rag.retrieve import search as retrieve
from app.llm.client_openai import complete, stream_completion

class RetrievedChunk(TypedDict):
    score: float
    source: str
    chunk_idx: int
    text: str

_env = Environment(
    loader=FileSystemLoader(str(Path(__file__).parent / "prompts")),
    autoescape=select_autoescape(disabled_extensions="jinja,"),
    trim_blocks=True,
    lstrip_blocks=True,
)

def build_prompt(question: str, contexts: list[RetrievedChunk]) -> str:
    tmpl = _env.get_template("answer.jinja")
    return tmpl.render(question=question, contexts=contexts)

def answer_question(question: str, top_k: int = 5) -> dict:
    ctx: list[RetrievedChunk] = retrieve(question, top_k=top_k)
    prompt: str = build_prompt(question, ctx)
    answer: str = complete(prompt)

    return {
        "answer": answer,
        "citations": [
            {"idx": i + 1, "source": c["source"], "chunk_idx": c["chunk_idx"]}
            for i, c in enumerate(ctx)
        ],
    }

def stream_answer(question: str, top_k: int = 5) -> Iterator[str]:
    #SSE generator: yields `data: <text>\n\n` frames as tokens arrive.
    #then a final JSON payload with citations, and a [DONE] marker

    ctx = retrieve(question, top_k=top_k)
    prompt = build_prompt(question, ctx)

    for delta in stream_completion(prompt):
        yield f"data: {delta}\n\n"
    
    import json
    citations = [
        {"idx": i + 1, "source": c["source"], "chunk_idx": c["chunk_idx"]}
        for i, c in enumerate(ctx)
    ]
    yield f"data: {json.dumps({'citations': citations})}\n\n"
    yield "data: [DONE]\n\n"