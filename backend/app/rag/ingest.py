from __future__ import annotations
import os, json, glob
from typing import Iterable
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

from app.rag.chunkers import chunks

#Config
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DOCS_DIR = "docs"
OUT_DIR = "data"

os.makedirs(OUT_DIR, exist_ok=True)

#file access
def read_md(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
    
def read_pdf(path: str) -> str:
    reader = PdfReader(path)

    return "\n".join((page.extract_text() or "") for page in reader.pages)

def load_text(path: str) -> str:
    ext = path.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return read_pdf(path)
    return read_md(path)

def iter_files(root: str) -> Iterable[str]:
    pats = ("**/*.md", "**/*.pdf")
    for pat in pats:
        for p in glob.glob(os.path.join(root, pat), recursive=True):
            yield p

# Main pipeline
def main(docs_dir: str = DOCS_DIR,
         max_tokens: int = 300,
         overlap: int = 40) -> None:
    files = [f for f in iter_files(docs_dir)]
    if not files:
        print(f"[ingest] No .md or .pdf found under '{docs_dir}'.")
        return

    print(f"[ingest] Found {len(files)} files. Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    meta: list[dict] = []
    embs_list: list[np.ndarray] = []
    next_id = 0

    for path in sorted(files):
        try:
            text = load_text(path)
        except Exception as e:
            print(f"[ingest] Skipping {path}: {e}")
            continue

        #Chunk by tokens
        for i, chunk in enumerate(chunks(text, max_tokens=max_tokens, overlap=overlap)):
            #encode each chunk to an embedding; normalize for cosine via inner product
            emb = model.encode(chunk, normalize_embeddings=True)
            embs_list.append(np.asarray(emb, dtype="float32"))

            meta.append({
                "id": next_id,
                "source": path,
                "chunk_idx": i,
                #keep text short_ish in metadata for quick previews
                "text": chunk[:800]
            })
            next_id += 1
    
    if not embs_list:
        print("[ingest] No chunks produced. Check your docs or chunk settings.") 
        return
    
    embs = np.vstack(embs_list).astype("float32")
    dim = embs.shape[1]
    print(f"[ingest] Built {len(meta)} chunks; embedding dim={dim}")

    index = faiss.IndexFlatIP(dim)
    index.add(embs)

    #Persist artifacts
    faiss.write_index(index, os.path.join(OUT_DIR, "index.faiss"))
    np.save(os.path.join(OUT_DIR, "embeddings.npy"), embs)

    with open(os.path.join(OUT_DIR, "meta.jsonl"), "w", encoding="utf-8") as f:
        for m in meta:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    
    print(f"[ingest] Saved to '{OUT_DIR}': index.faiss, embeddings.npy, meta.jsonl")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else DOCS_DIR)