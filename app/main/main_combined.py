"""
Main module for combined source teaching content generation pipeline.
Supports YouTube videos, web articles, and file uploads.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Any
import hashlib
import json

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
import logging

logger = logging.getLogger(__name__)


def _ensure_dirs():
    """Ensure required directories exist."""
    Path(cfg.DATA_PATH).mkdir(parents=True, exist_ok=True)
    (Path(cfg.DATA_PATH) / "outputs").mkdir(parents=True, exist_ok=True)


def _save_json(obj: Dict[str, Any], path: Path):
    """Save JSON to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _extract_text_from_file_result(file_result: Dict[str, Any]) -> str:
    """
    Extract text from file_extractor result.
    
    file_result structure:
    {
        "metadata": {...},
        "extraction_method": "...",
        "pages": [
            {"page_number": 1, "text": "...", "success": True},
            ...
        ]
    }
    """
    if not isinstance(file_result, dict):
        # Fallback: if it's a string, return it directly
        return str(file_result) if file_result else ""
    
    pages = file_result.get("pages", [])
    if not pages:
        # Fallback: check if there's a direct "text" key
        return file_result.get("text", "")
    
    # Extract text from all successful pages
    texts = []
    for page in pages:
        if page.get("success", False):
            page_text = page.get("text", "").strip()
            if page_text:
                texts.append(page_text)
    
    return "\n\n".join(texts)


def run_pipeline(
    sources: Dict[str, Any],
    plan_text: str,
    topics: List[str],
    level: str,
    style: str,
):
    """
    Run combined pipeline with multiple source types.
    
    Args:
        sources: Dictionary containing:
            - videos: List of YouTube URLs
            - articles: List of web article URLs
            - files: List of FileStorage objects (from controller)
        plan_text: Learning plan description
        topics: List of topics to cover
        level: Learning level (beginner/intermediate/advanced)
        style: Content style (concise/detailed/exam-prep)
    """
    logger.info("Starting combined pipeline")
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
        final_k = 8

    # Extract sources (This matches your controller)
    video_urls = sources.get("videos", [])
    article_urls = sources.get("articles", [])
    file_storages = sources.get("files", [])
    
    logger.info(
        f"Processing {len(video_urls)} videos, {len(article_urls)} articles, "
        f"{len(file_storages)} files"
    )

    # Create a combined namespace
    source_hash = hashlib.md5(
        f"{','.join(video_urls)}{','.join(article_urls)}{len(file_storages)}".encode()
    ).hexdigest()[:8]
    namespace = f"combined:{source_hash}"
    logger.info(f"Namespace: {namespace}")

    all_chunks = []
    source_metadata = {
        "videos": [],
        "articles": [],
        "files": []
    }

    # Process YouTube videos
    for idx, video_url in enumerate(video_urls):
        try:
            logger.info(f"Processing video {idx + 1}/{len(video_urls)}: {video_url}")
            video_data = get_transcript_text(video_url)
            transcript = video_data.get("transcript", "")
            
            if transcript:
                chunks = make_chunks(transcript)
                all_chunks.extend(chunks)
                source_metadata["videos"].append({
                    "url": video_url,
                    "title": video_data.get("title", "Unknown"),
                    "chunks": len(chunks)
                })
                logger.info(f"  Added {len(chunks)} chunks from video")
        except Exception as e:
            # THIS IS LIKELY THE ISSUE: Check logs for this error
            logger.error(f"Failed to process video {video_url}: {e}")

    # Process web articles
    for idx, article_url in enumerate(article_urls):
        try:
            logger.info(f"Processing article {idx + 1}/{len(article_urls)}: {article_url}")
            article_data = get_article_text(article_url)
            article_text = article_data.get("text", "")
            
            if isinstance(article_text, list):
                article_text = "\n\n".join(article_text)
            
            if article_text:
                chunks = make_chunks(article_text)
                all_chunks.extend(chunks)
                source_metadata["articles"].append({
                    "url": article_url,
                    "title": article_data.get("title", "Unknown"),
                    "chunks": len(chunks)
                })
                logger.info(f"  Added {len(chunks)} chunks from article")
        except Exception as e:
            logger.error(f"Failed to process article {article_url}: {e}")

    # Process uploaded files
    for idx, file_storage in enumerate(file_storages):
        try:
            logger.info(f"Processing file {idx + 1}/{len(file_storages)}: {file_storage.filename}")
            # process_file_storage receives the FileStorage object directly
            file_result = process_file_storage(file_storage)
            
            file_text = _extract_text_from_file_result(file_result)
            
            if file_text:
                chunks = make_chunks(file_text)
                all_chunks.extend(chunks)
                
                if isinstance(file_result, dict):
                    file_metadata = file_result.get("metadata", {})
                    extraction_method = file_result.get("extraction_method", "unknown")
                    
                    source_metadata["files"].append({
                        "filename": file_storage.filename,
                        "chunks": len(chunks),
                        "extraction_method": extraction_method,
                        "file_size": file_metadata.get("file_size", 0),
                        "page_count": file_metadata.get("page_count", 0)
                    })
                else:
                    source_metadata["files"].append({
                        "filename": file_storage.filename,
                        "chunks": len(chunks)
                    })
                
                logger.info(f"  Added {len(chunks)} chunks from file")
            else:
                logger.warning(f"No text extracted from file {file_storage.filename}")
                
        except Exception as e:
            # THIS IS LIKELY THE OTHER ISSUE: Check logs for this error
            logger.error(f"Failed to process file {file_storage.filename}: {e}")
            import traceback
            logger.error(traceback.format_exc())

    if not all_chunks:
        # If all sources failed, this error will be raised.
        raise ValueError("No content could be extracted from any source. Check logs for errors.")

    logger.info(f"Total chunks collected: {len(all_chunks)}")

    # Embed all chunks
    logger.info("Embedding all chunks...")
    embedded = embed_chunks(all_chunks)
    logger.info(f"Embedded {len(embedded)} chunks")

    # Upsert to Pinecone
    logger.info("Upserting to Pinecone...")
    ensure_index()
    count = upsert_chunks(
        namespace=namespace,
        embedded_chunks=embedded,
        batch_size=100
    )
    logger.info(f"Upserted {count} vectors")

    # Generate retrieval queries
    logger.info("Generating retrieval queries...")
    queries = generate_queries_from_plan(plan_text, n=8)
    logger.info(f"Generated {len(queries)} queries")

    # Retrieve contexts
    logger.info("Retrieving contexts...")
    hits = retrieve_from_queries(
        namespace=namespace,
        queries=queries,
        per_query_k=5,
        final_k=final_k,
        include_text=True,
    )
    logger.info(f"Retrieved {len(hits)} context chunks")

    # Generate teaching materials
    logger.info("Generating teaching materials...")
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

    # Build PPT
    logger.info("Building PPT...")
    try:
        ppt_path = build_ppt_from_result(result)
        logger.info(f"  PPT saved -> {ppt_path}")
        result["_ppt_path"] = str(ppt_path)
    except Exception as e:
        logger.warning(f"  PPT generation failed: {e}")
        result["_ppt_path"] = None

    # Add source metadata to result
    result["source_metadata"] = source_metadata
    result["namespace"] = namespace
    
    # --- FIX: Removed the trailing underscore ---
    result["total_chunks"] = len(all_chunks)

    # Save results
    out_dir = Path(cfg.DATA_PATH) / "outputs"
    out_file = out_dir / f"combined_{source_hash}_results.json"
    _save_json(result, out_file)
    logger.info(f"Results saved to {out_file}")
    
    result["_output_path"] = str(out_file)

    return result