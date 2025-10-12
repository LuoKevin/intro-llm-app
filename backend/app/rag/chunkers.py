from __future__ import annotations
import tiktoken

#OpenAI compatible tokenizer
enc = tiktoken.get_encoding("cl100k_base")

def to_tokens(text: str) -> list[int]:
    return enc.encode(text)

#splits text into overlapping token windows and decode back into strings
def chunks(text: str, max_tokens: int = 300, overlap: int = 40) -> list[str]:
    toks = to_tokens(text)
    out: list[str] = []
    i = 0

    while i < len(toks):
        window = toks[i : i + max_tokens]
        if not window:
            break
        out.append(enc.decode(window))
        i += max_tokens - overlap

    return [s for s in out if s.strip()]