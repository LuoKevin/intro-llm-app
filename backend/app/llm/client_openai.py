from __future__ import annotations
from typing import Final
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