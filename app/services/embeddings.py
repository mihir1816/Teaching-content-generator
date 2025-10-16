from __future__ import annotations
from typing import List, Dict, Any, Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

import app.config as cfg
from app.services.chunker import normalize_text

# Load the ST model once (free, local)
_model: SentenceTransformer | None = None

def _get_st_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(cfg.EMBEDDING_MODEL_NAME)
    return _model

def _batched(iterable: Iterable[Any], n: int) -> Iterable[List[Any]]:
    batch: List[Any] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= n:
            yield batch
            batch = []
    if batch:
        yield batch

def embed_texts(
    texts: List[str],
    batch_size: int = 64,
    normalize: bool = True,
) -> List[List[float]]:
    """
    Embed a list of strings locally using SentenceTransformers (all-MiniLM-L6-v2).
    Returns: list of vectors (one per input).
    """
    model = _get_st_model()

    vectors: List[List[float]] = []
    for batch in _batched(texts, n=batch_size):
        clean_batch = [normalize_text(t) if normalize else t for t in batch]
        emb = model.encode(clean_batch, convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=False)
        # emb is (batch, dim) float32 ndarray
        if isinstance(emb, np.ndarray):
            for row in emb:
                vectors.append(row.astype(float).tolist())
        else:
            # just in case encode returns list
            vectors.extend([[float(x) for x in row] for row in emb])
    return vectors

def embed_chunks(
    chunks: List[Dict[str, str]],
    batch_size: int = 64,
) -> List[Dict[str, Any]]:
    """
    Embed a list of chunk dicts: [{"id": "...", "text": "..."}].
    Returns: [{"id": "...", "text": "...", "vector": [...]}, ...]
    """
    if not chunks:
        return []
    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts, batch_size=batch_size)
    out: List[Dict[str, Any]] = []
    for c, v in zip(chunks, vectors):
        out.append({"id": c["id"], "text": c["text"], "vector": v})
    return out
