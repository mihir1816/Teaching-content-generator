"""
Main orchestrator for article-based teaching content generation pipeline.
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse
import hashlib

from dotenv import load_dotenv

from app.services.web_article import get_article_text
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
    url: str,
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

    # 1) Fetch article content
    print(">>> Fetching article ...")
    article = get_article_text(url)
    article_text = article["text"]
    article_title = article["title"]
    
    # Create namespace for this article
    domain = urlparse(url).netloc.replace("www.", "")
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    namespace = f"article:{domain}:{url_hash}"
    
    print(f"    title: {article_title}")
    print(f"    chars: {len(article_text)}")
    print(f"    namespace: {namespace}")

    # 2) Chunk
    print(">>> Chunking article ...")
    chunks = make_chunks(article_text)
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
               out_dir / f"{url_hash}_plan_queries.json")

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
        model_name=getattr(cfg, "LLM_MODEL_NAME", "gemini-2.5-flash"),
    )
    
    ppt_path = build_ppt_from_result(result)

    _save_json(result, out_dir / f"{url_hash}_results.json")
    print(f"    results saved -> {out_dir / (url_hash + '_results.json')}")
    print(">>> Done.")