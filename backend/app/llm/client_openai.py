from __future__ import annotations
from typing import Final, Iterator
from openai import OpenAI
from app.core.config import settings

_MODEL: Final[str] = "gpt-4o-mini" #change if preferred

_client = OpenAI(api_key=settings.openai_api_key)

def complete(prompt: str) -> str:
    #Minimal, non-streaming text completion via Chat Completions

    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    return resp.choices[0].message.content or ""

def stream_completion(prompt: str) -> Iterator[str]:
    #Yields small text deltas from OpenAI as they arrive

    stream = _client.chat.completions.create(
        stream=True,
        model=_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    for chunk in stream:
        try:
            delta = chunk.choices[0].delta
            piece = getattr(delta, "content", None)
            if piece:
                yield piece
        except Exception:
            pass

    