from __future__ import annotations
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

from app.services.youtube import get_transcript_text
from app.services.chunker import make_chunks
from app.services.embeddings import embed_chunks
from app.services.pinecone_index import ensure_index, upsert_chunks
from app.services.generate_queries import generate_queries_from_plan
from app.services.retriever import retrieve_from_queries
from app.services.generator import generate_all

import app.config as cfg


def _ensure_dirs():
    Path(cfg.DATA_PATH).mkdir(parents=True, exist_ok=True)
    (Path(cfg.DATA_PATH) / "outputs").mkdir(parents=True, exist_ok=True)


def _save_json(obj: Dict[str, Any], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _infer_topic_from_plan(plan_text: str, fallback: str = "Untitled Topic") -> str:
    """
    Try to infer a human-friendly topic label from the plan string.
    - Prefer first non-empty line (trimmed to ~80 chars)
    - Else use first 6–8 tokens
    """
    for line in plan_text.splitlines():
        ln = line.strip()
        if ln:
            return (ln[:80]).strip()
    # fallback: first few words
    words = plan_text.strip().split()
    if not words:
        return fallback
    return " ".join(words[:8])


def run_pipeline(
    video: str,
    plan_text: str,
    level: str,
    style: str,
    language: str = "en",
    reingest: bool = True,
    final_k: int = 8,
    mcq_count: int = 8,
):
    print(">>> Loading .env and prepping folders ...")
    load_dotenv()
    _ensure_dirs()

    # 1) Transcript (English-first; auto-translate if needed)
    print(">>> Fetching transcript ...")
    t = get_transcript_text(video)
    video_id = t["video_id"]
    transcript_text = t["text"]
    print(f"    video_id: {video_id}, lang: {t['language']}, chars: {len(transcript_text)}")

    # 2) Chunk
    print(">>> Chunking transcript ...")
    chunks = make_chunks(transcript_text)
    print(f"    chunks: {len(chunks)}")

    # 3) Embed (MiniLM local)
    print(">>> Embedding chunks (all-MiniLM-L6-v2) ...")
    embedded = embed_chunks(chunks)
    dim = len(embedded[0]["vector"]) if embedded else 0
    print(f"    embedded: {len(embedded)}, dim: {dim}")

    # 4) Index + upsert
    if reingest:
        print(">>> Ensuring Pinecone index & upserting ...")
        ensure_index()
        count = upsert_chunks(video_id=video_id, embedded_chunks=embedded, batch_size=100)
        print(f"    upserted: {count} into namespace: video:{video_id}")
    else:
        print(">>> Skipping re-ingest (reingest=False).")

    out_dir = Path(cfg.DATA_PATH) / "outputs"

    # 5) Generate retrieval queries from your plan string (Gemini)
    print(">>> Generating retrieval queries from plan (Gemini) ...")
    queries = generate_queries_from_plan(plan_text, n=8)
    _save_json({"plan": plan_text, "queries": queries, "level": level, "style": style, "language": language},
               out_dir / f"{video_id}_plan_queries.json")
    print(f"    queries: {queries}")

    # 6) Retrieve (dense RAG)
    print(">>> Retrieving top context (dense) ...")
    hits = retrieve_from_queries(
        video_id=video_id,
        queries=queries,
        per_query_k=5,
        final_k=final_k,
        include_text=True,
    )
    print(f"    fused hits: {len(hits)}")

    # 7) Generate Notes → Summary → MCQs (Gemini, no citations)
    topic_label = _infer_topic_from_plan(plan_text)
    print(">>> Generating Notes, Summary, MCQs (Gemini) ...")
    result = generate_all(
        video_id=video_id,
        topic=topic_label,
        queries=queries,
        level=level,
        style=style,
        language=language,
        final_k=final_k,
        max_context_chars=6000,
        model_name=getattr(cfg, "LLM_MODEL_NAME", "gemini-1.5-flash"),
        mcq_count=mcq_count,
    )

    _save_json(result, out_dir / f"{video_id}_results.json")
    print(f"    results saved -> {out_dir / (video_id + '_results.json')}")
    print(">>> Done.")


def _parse_args():
    p = argparse.ArgumentParser(description="YouTube RAG pipeline (Gemini) using a provided plan string.")
    p.add_argument("--video", required=True, help="YouTube URL or 11-char ID.")
    p.add_argument("--plan", required=True, help="Planning string (topic(s) + any notes).")
    p.add_argument("--level", choices=["beginner", "intermediate", "advanced"], default="beginner")
    p.add_argument("--style", choices=["concise", "detailed", "exam-prep"], default="concise")
    p.add_argument("--language", default="en")
    p.add_argument("--no-reingest", action="store_true")
    p.add_argument("--final-k", type=int, default=8)
    p.add_argument("--mcq-count", type=int, default=8)
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_pipeline(
        video=args.video,
        plan_text=args.plan,
        level=args.level,
        style=args.style,
        language=args.language,
        reingest=not args.no_reingest,
        final_k=args.final_k,
        mcq_count=args.mcq_count,
    )
