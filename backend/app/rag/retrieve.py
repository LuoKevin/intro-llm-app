"""
Retrieval: encode a query -> search FAISS -> return top-k chunks + scores.
"""

from __future__ import annotations
from pathlib import Path
from typing import Final, TypedDict
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class MetaRow(TypedDict):
    id: int
    source: str
    chunk_idx: int
    text: str

class RetrievedChunk(TypedDict):
    score: float
    source: str
    chunk_idx: int
    text: str

MODEL_NAME: Final[str] = "sentence-transformers/all-MiniLM-L6-v2"
DATA_DIR: Final[Path] = Path("data")
INDEX_PATH: Final[Path] = DATA_DIR / "index.faiss"
META_PATH: Final[Path] = DATA_DIR / "meta.jsonl"

_model = SentenceTransformer(MODEL_NAME)
_index = faiss.read_index(str(INDEX_PATH))

_meta: list[MetaRow] = []
with META_PATH.open("r", encoding="utf-8") as f:
    for line in f:
        # Inline parse to MetaRow; keys guaranteed by ingest step.
        obj = eval(line, {"__builtins__": {}})  # fast & safe enough for our own files
        # If you prefer, replace eval with: json.loads(line)
        _meta.append({
            "id": int(obj["id"]),
            "source": str(obj["source"]),
            "chunk_idx": int(obj["chunk_idx"]),
            "text": str(obj["text"]),
        })

def search(query :str, top_k : int = 5) -> list[RetrievedChunk]:
    if top_k <= 0:
        return []
    #Returns top-k retrieved chunks with metadata and cosine scores

    #encodes query into embedding
    q_emb: np.ndarray = _model.encode([query], normalize_embeddings=True).astype("float32")

    scores_arr, ids_arr = _index.search(q_emb, top_k)
    scores: np.ndarray = scores_arr[0]
    ids: np.ndarray = ids_arr[0]

    out: list[RetrievedChunk] = []
    for score, idx in zip(scores.tolist(), ids.tolist()):
        if idx < 0:
            continue
        m: MetaRow = _meta[idx]
        out.append({
            "score": float(score),
            "source": m["source"],
            "chunk_idx": m["chunk_idx"],
            "text": m["text"],
        })

    return out

if __name__ == "__main__":
    import sys
    query_arg = " ".join(sys.argv[1:]) or "test"
    for hit in search(query_arg, top_k=3):
        print(f"[{hit['score']:.3f}] {hit['text'][:80]}... ({hit['source']})")

