"""
Main module for combined source teaching content generation pipeline.
"""
from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Dict, List, Any

from dotenv import load_dotenv

from app.services.youtube import get_transcript_text
from app.services.web_article import get_article_text
from app.services.file_extractor import process_file_storage
from app.services.chunker import make_chunks
from app.services.embeddings import embed_chunks
from app.services.pinecone_index import ensure_index, upsert_chunks
from app.services.generate_queries import generate_queries_from_plan
from app.services.retriever import retrieve_from_queries
from app.services.generator import generate_all
from app.services.ppt_builder import build_ppt_from_result

import app.config as cfg


def _ensure_dirs():
    Path(cfg.DATA_PATH).mkdir(parents=True, exist_ok=True)
    (Path(cfg.DATA_PATH) / "outputs").mkdir(parents=True, exist_ok=True)


def _save_json(obj: Dict[str, Any], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def run_pipeline(
    sources: Dict[str, List[str]],
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

    all_texts = []

    # 1) Process YouTube videos
    if videos := sources.get("videos", []):
        print(f">>> Processing {len(videos)} YouTube videos ...")
        for video in videos:
            try:
                t = get_transcript_text(video)
                all_texts.append(t["text"])
                print(f"    video: {t['video_id']}, chars: {len(t['text'])}")
            except Exception as e:
                print(f"    Error processing video {video}: {str(e)}")

    # 2) Process articles
    if articles := sources.get("articles", []):
        print(f">>> Processing {len(articles)} articles ...")
        for article in articles:
            try:
                a = get_article_text(article)
                all_texts.append(a["text"])
                print(f"    article: {a['title']}, chars: {len(a['text'])}")
            except Exception as e:
                print(f"    Error processing article {article}: {str(e)}")

    # 3) Process files
    if files := sources.get("files", []):
        print(f">>> Processing {len(files)} files ...")
        for file_storage in files:
            try:
                extraction = process_file_storage(file_storage)
                pages = extraction.get("pages", [])
                file_text = "\n\n".join([p.get("text", "") for p in pages if p.get("text")])
                all_texts.append(file_text)
                print(f"    file: {extraction['metadata']['file_name']}, chars: {len(file_text)}")
            except Exception as e:
                print(f"    Error processing file: {str(e)}")

    # Combine all texts
    combined_text = "\n\n".join(all_texts)
    print(f">>> Total combined chars: {len(combined_text)}")

    # 4) Chunk
    print(">>> Chunking combined content ...")
    chunks = make_chunks(combined_text)
    print(f"    chunks: {len(chunks)}")

    # 5) Embed (MiniLM local)
    print(">>> Embedding chunks (all-MiniLM-L6-v2) ...")
    embedded = embed_chunks(chunks)
    dim = len(embedded[0]["vector"]) if embedded else 0
    print(f"    embedded: {len(embedded)}, dim: {dim}")

    # 6) Create namespace
    namespace = f"combined_{Path(cfg.DATA_PATH).stem}"
    print(f">>> Using namespace: {namespace}")

    # 7) Ensure Pinecone index & upsert
    print(">>> Ensuring Pinecone index & upserting ...")
    ensure_index()
    count = upsert_chunks(
        namespace=namespace,
        embedded_chunks=embedded,
        batch_size=100
    )
    print(f"    upserted: {count} vectors into namespace: {namespace}")

    out_dir = Path(cfg.DATA_PATH) / "outputs"

    # 8) Generate retrieval queries from your plan string (Gemini)
    print(">>> Generating retrieval queries from plan (Gemini) ...")
    queries = generate_queries_from_plan(plan_text, n=8)
    print(f"    queries: {queries}")
    _save_json({"plan": plan_text, "queries": queries, "level": level, "style": style},
               out_dir / "combined_plan_queries.json")

    # 9) Retrieve (dense RAG)
    print(">>> Retrieving top context (dense) ...")
    hits = retrieve_from_queries(
        namespace=namespace,
        queries=queries,
        per_query_k=5,
        final_k=final_k,
        include_text=True,
    )
    print(f"    fused hits: {len(hits)}")

    # 10) Generate Notes → Summary → MCQs (Gemini, no citations)
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
    
    ppt_path = build_ppt_from_result(result)

    _save_json(result, out_dir / "combined_results.json")
    print(f"    results saved -> {out_dir / 'combined_results.json'}")
    print(">>> Done.")