"""
Main orchestrator for file upload-based teaching content generation pipeline.
"""
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

from app.services.file_extractor import process_file_storage
from app.services.chunker import make_chunks
from app.services.embeddings import embed_chunks
from app.services.pinecone_index import ensure_index, upsert_chunks
from app.services.generate_queries import generate_queries_from_plan
from app.services.retriever import retrieve_from_queries
from app.services.generator import generate_all
from app.services.ppt_builder import build_ppt_from_result

import app.config as cfg
import logging

logger = logging.getLogger(__name__)


def _ensure_dirs():
    Path(cfg.DATA_PATH).mkdir(parents=True, exist_ok=True)
    (Path(cfg.DATA_PATH) / "outputs").mkdir(parents=True, exist_ok=True)


def _save_json(obj: Dict[str, Any], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def run_pipeline(
    file_storage,
    plan_text: str,
    topics: List[str],
    level: str,
    style: str,
):
    print(">>> Loading .env and prepping folders ...")
    load_dotenv()
    _ensure_dirs()

    # Determine final_k based on style
    if style == "concise":
        final_k = 3
    elif style == "detailed":
        final_k = 8
    elif style == "exam-prep":
        final_k = 5
    else:
        final_k = 8  # default

    # 1) Extract text from uploaded file
    print(">>> Extracting text from file ...")
    extraction_result = process_file_storage(file_storage)
    
    pages = extraction_result.get("pages", [])
    file_text = "\n\n".join([p.get("text", "") for p in pages if p.get("text")])
    
    metadata = extraction_result.get('metadata')
    filename = None

    if metadata and 'file_name' in metadata:
        filename = metadata['file_name']
    else:
        # Log a warning or set a default
        print("WARNING: 'file_name' was not found in extraction_result['metadata']")
        filename = 'unknown_file_from_fallback'

    # Now you can safely use the 'filename' variable
    file_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    namespace = f"file:{file_hash}:{timestamp}"
    
    print(f"    filename: {filename}")
    print(f"    chars: {len(file_text)}")
    print(f"    namespace: {namespace}")

    # 2) Chunk
    print(">>> Chunking file text ...")
    chunks = make_chunks(file_text)
    print(f"    chunks: {len(chunks)}")

    # 3) Embed (MiniLM local)
    print(">>> Embedding chunks (all-MiniLM-L6-v2) ...")
    embedded = embed_chunks(chunks)
    dim = len(embedded[0]["vector"]) if embedded else 0
    print(f"    embedded: {len(embedded)}, dim: {dim}")

    # 4) Ensure Pinecone index & upsert
    print(">>> Ensuring Pinecone index & upserting ...")
    ensure_index()
    count = upsert_chunks(
        namespace=namespace,
        embedded_chunks=embedded,
        batch_size=100
    )
    print(f"    upserted: {count} vectors into namespace: {namespace}")

    out_dir = Path(cfg.DATA_PATH) / "outputs"

    # 5) Generate retrieval queries from your plan string (Gemini)
    print(">>> Generating retrieval queries from plan (Gemini) ...")
    queries = generate_queries_from_plan(plan_text, n=8)
    print(f"    queries: {queries}")
    _save_json({"plan": plan_text, "queries": queries, "level": level, "style": style},
               out_dir / f"{file_hash}_plan_queries.json")

    # # 6) Retrieve (dense RAG)
    # print(">>> Retrieving top context (dense) ...")
    # hits = retrieve_from_queries(
    #     namespace=namespace,
    #     queries=queries,
    #     per_query_k=5,
    #     final_k=final_k,
    #     include_text=True,
    # )
    # print(f"    fused hits: {len(hits)}")

    # 7) Generate Notes → Summary → MCQs (Gemini, no citations)
    print(">>> Generating Notes, Summary, MCQs (Gemini) ...")
    result = generate_all(
        namespace=namespace,
        topic=topics,
        queries=queries,
        level=level,
        style=style,
        final_k=final_k,
        max_context_chars=6000,
        model_name=getattr(cfg, "LLM_MODEL_NAME", "gemini-1.5-flash"),
    )
    
    print(">>> Building PPT...")
    try:
        ppt_path = build_ppt_from_result(result)
        print(f"    PPT saved -> {ppt_path}")
    except Exception as e:
        print(f"    PPT generation failed: {e}")
        ppt_path = None

    # Attach ppt path to the result so controllers can extract filename for download
    try:
        result["_ppt_path"] = str(ppt_path) if ppt_path is not None else None
    except Exception:
        pass

    _save_json(result, out_dir / f"{file_hash}_results.json")
    print(f"    results saved -> {out_dir / (file_hash + '_results.json')}")
    print(">>> Done.")

    # Return the result dict for controller to use
    return result