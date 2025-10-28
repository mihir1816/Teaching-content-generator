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
    video: str,
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

    # 4) Create namespace for this video
    namespace = f"video:{video_id}"
    print(f">>> Using namespace: {namespace}")

   
    print(">>> Ensuring Pinecone index & upserting ...")
    ensure_index()
    count = upsert_chunks(
        namespace=namespace,
        embedded_chunks=embedded,
        batch_size=100
    )
    print(f"    upserted: {count} vectors into namespace: {namespace}")


    out_dir = Path(cfg.DATA_PATH) / "outputs"

    # 6) Generate retrieval queries from your plan string (Gemini)
    print(">>> Generating retrieval queries from plan (Gemini) ...")
    queries = generate_queries_from_plan(plan_text, n=8)
    print(f"    queries: {queries}")
    _save_json({"plan": plan_text, "queries": queries, "level": level, "style": style},
               out_dir / f"{video_id}_plan_queries.json")

    # 8) Generate Notes → Summary → MCQs (Gemini, no citations)
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
    p.add_argument("--final-k", type=int, default=8)
    p.add_argument("--mcq-count", type=int, default=8)
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_pipeline(
        video=args.video,
        plan_text=args.plan,
        topics=args.topics,
        level=args.level,
        style=args.style,
    )