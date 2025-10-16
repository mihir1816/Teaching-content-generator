from __future__ import annotations
from typing import List, Dict, Any, Iterable, Optional

import app.config as cfg

# Pinecone v5 client (serverless)
try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError as e:
    raise ImportError(
        "Pinecone client v5 is required. Install it with:\n  pip install pinecone-client==5.0.1"
    ) from e


# --- Constants (MiniLM embedding dim = 384) ----------------------------------
EMBED_DIM = 384
DEFAULT_METRIC = "cosine"

# --- Client + Index helpers ---------------------------------------------------
def _get_pc() -> Pinecone:
    if not cfg.PINECONE_API_KEY:
        raise RuntimeError("Missing PINECONE_API_KEY in environment/.env")
    return Pinecone(api_key=cfg.PINECONE_API_KEY)

def _index_exists(pc: Pinecone, name: str) -> bool:
    return any(ix["name"] == name for ix in pc.list_indexes())

def ensure_index() -> None:
    """
    Create the Pinecone index if it doesn't exist.
    Uses serverless spec; cloud/region configurable via config/env.
    """
    pc = _get_pc()
    name = cfg.VECTOR_DB_NAME
    metric = getattr(cfg, "PINECONE_METRIC", DEFAULT_METRIC) or DEFAULT_METRIC
    cloud = getattr(cfg, "PINECONE_CLOUD", "aws")
    region = getattr(cfg, "PINECONE_REGION", "us-east-1")

    if _index_exists(pc, name):
        return  # already there

    pc.create_index(
        name=name,
        dimension=EMBED_DIM,
        metric=metric,
        spec=ServerlessSpec(cloud=cloud, region=region),
    )

def _get_index():
    pc = _get_pc()
    return pc.Index(cfg.VECTOR_DB_NAME)


# --- Upsert / Query / Delete --------------------------------------------------
def upsert_chunks(
    video_id: str,
    embedded_chunks: List[Dict[str, Any]],
    namespace: Optional[str] = None,
    batch_size: int = 100,
    store_text_metadata: bool = True,
) -> int:
    """
    Upsert vectors into Pinecone.
    - embedded_chunks: [{"id": "...", "text": "...", "vector": [...]}]
    - namespace defaults to per-video: f"video:{video_id}"
    Returns: number of vectors upserted
    """
    if not embedded_chunks:
        return 0

    # sanity: dimension check
    for c in embedded_chunks:
        vec = c.get("vector")
        if not isinstance(vec, (list, tuple)) or len(vec) != EMBED_DIM:
            raise ValueError(f"Vector dim mismatch (expected {EMBED_DIM}, got {len(vec) if vec is not None else 'None'})")

    ns = namespace or f"video:{video_id}"
    index = _get_index()

    # batch and upsert
    count = 0
    batch: List[Dict[str, Any]] = []
    for c in embedded_chunks:
        meta = {"text": c["text"]} if store_text_metadata else None
        batch.append({"id": c["id"], "values": c["vector"], "metadata": meta})
        if len(batch) >= batch_size:
            index.upsert(vectors=batch, namespace=ns)
            count += len(batch)
            batch = []
    if batch:
        index.upsert(vectors=batch, namespace=ns)
        count += len(batch)
    return count


def query(
    vector: List[float],
    namespace: str,
    top_k: int = cfg.TOP_K,
    include_metadata: bool = True,
) -> List[Dict[str, Any]]:
    """
    Dense similarity search within a namespace.
    Returns a simplified list:
      [{"id": "...", "score": 0.87, "text": "...(optional)..."}, ...]
    """
    if len(vector) != EMBED_DIM:
        raise ValueError(f"Query vector must be {EMBED_DIM}-dim")

    index = _get_index()
    res = index.query(
        vector=vector,
        top_k=top_k,
        include_values=False,
        include_metadata=include_metadata,
        namespace=namespace,
    )

    out: List[Dict[str, Any]] = []
    # Pinecone v5 returns res.matches (list-like)
    for match in getattr(res, "matches", []) or []:
        item = {"id": match["id"], "score": match["score"]}
        md = match.get("metadata") or {}
        if include_metadata and "text" in md:
            item["text"] = md["text"]
        out.append(item)
    return out


def delete_by_video(video_id: str) -> None:
    """
    Delete all vectors for a given video by wiping its namespace.
    """
    ns = f"video:{video_id}"
    index = _get_index()
    index.delete(delete_all=True, namespace=ns)
