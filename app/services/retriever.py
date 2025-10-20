from __future__ import annotations
from typing import List, Dict, Any
from collections import defaultdict

import app.config as cfg
from app.services.embeddings import embed_texts
from app.services.pinecone_index import query as pinecone_query

def _rrf_fuse(ranked_lists: List[List[Dict[str, Any]]], k: int = 60) -> List[Dict[str, Any]]:
    """
    Reciprocal Rank Fusion.
    ranked_lists: list of lists (each inner list is Pinecone results for one query)
    Each item must have {"id", "score", optional "text"}.
    Returns a fused, deduplicated list sorted by descending RRF score.
    """
    scores = defaultdict(float)
    keep_text = {}

    for ranked in ranked_lists:
        for rank, item in enumerate(ranked, start=1):
            cid = item["id"]
            scores[cid] += 1.0 / (k + rank)
            # keep one representative text for quick preview
            if cid not in keep_text and "text" in item:
                keep_text[cid] = item["text"]

    fused = [{"id": cid, "score": s, "text": keep_text.get(cid)} for cid, s in scores.items()]
    fused.sort(key=lambda x: x["score"], reverse=True)
    return fused

def retrieve_from_queries(
    namespace: str,
    queries: List[str],
    per_query_k: int = 5,
    final_k: int = 8,
    include_text: bool = True,
) -> List[Dict[str, Any]]:
    """
    Core entrypoint: take a list of teacher/LLM-generated queries,
    run dense retrieval per query, fuse with RRF, and return top 'final_k' chunks.
    
    Args:
        namespace: Pinecone namespace (e.g., "video:abc123" or "article:example:hash")
        queries: List of search queries
        per_query_k: Number of results to retrieve per query
        final_k: Final number of results to return after fusion
        include_text: Whether to include text metadata in results

    Returns: [{"id","score","text"(optional)}...]
    """
    if not queries:
        return []

    # 1) Embed queries locally (MiniLM; free)
    qvecs = embed_texts(queries)

    # 2) Search Pinecone in the provided namespace
    ranked_lists: List[List[Dict[str, Any]]] = []
    for qv in qvecs:
        hits = pinecone_query(
            vector=qv,
            namespace=namespace,
            top_k=per_query_k,
            include_metadata=include_text,
        )
        ranked_lists.append(hits)

    # 3) Fuse with RRF
    fused = _rrf_fuse(ranked_lists, k=60)

    # 4) Return the top final_k
    return fused[:final_k]