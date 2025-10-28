"""
Main module for combined source teaching content generation pipeline.
"""
from __future__ import annotations
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any
import json

from dotenv import load_dotenv

from app.services.youtube import get_transcript_text
from app.services.web_article import get_article_text
from app.services.file_extractor import process_file_storage
from app.services.chunker import make_chunks
from app.services.embeddings import embed_chunks
from app.services.pinecone_index import ensure_index, upsert_chunks, delete_namespace
from app.services.retriever import retrieve_from_queries
from app.services.generator import generate_all
from app.services.ppt_builder import build_ppt_from_result
from app.services.notes_builder import build_notes_pdf

import app.config as cfg

def _ensure_dirs():
    Path(cfg.DATA_PATH).mkdir(parents=True, exist_ok=True)
    (Path(cfg.DATA_PATH) / "outputs").mkdir(parents=True, exist_ok=True)

def _save_json(obj: Dict[str, Any], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def process_youtube_sources(videos: List[str]) -> List[str]:
    """Process YouTube videos and return their transcripts."""
    texts = []
    for video in videos:
        try:
            transcript = get_transcript_text(video)
            if isinstance(transcript, dict) and "text" in transcript:
                texts.append(transcript["text"])
            else:
                print(f"Warning: Unexpected transcript format for video {video}")
        except Exception as e:
            print(f"Error processing video {video}: {str(e)}")
    return texts

def process_article_sources(articles: List[str]) -> List[str]:
    """Process web articles and return their content."""
    texts = []
    for article in articles:
        try:
            content = get_article_text(article)
            if isinstance(content, dict) and "text" in content:
                texts.append(content["text"])
            else:
                print(f"Warning: Unexpected content format for article {article}")
        except Exception as e:
            print(f"Error processing article {article}: {str(e)}")
    return texts

def process_file_sources(files: List[str]) -> List[str]:
    """Process uploaded files and return their content."""
    texts = []
    for file_path in files:
        # Create a file-like object that process_file_storage can handle
        class MockFileStorage:
            def __init__(self, path):
                self.filename = os.path.basename(path)
                self._path = path
            
            def save(self, dst_path):
                shutil.copy2(self._path, dst_path)
        
        # Process the file
        file_storage = MockFileStorage(file_path)
        result = process_file_storage(file_storage)
        
        # Combine all page texts
        if result and "pages" in result:
            content = "\n\n".join(
                page["text"] for page in result["pages"] 
                if page.get("success") and page.get("text")
            )
            texts.append(content)
    
    return texts

def get_chunks_per_depth(depth: int) -> int:
    """
    Convert depth/detail rating (1-5) to number of chunks to retrieve.
    
    The depth rating controls how much content is included for each topic:
    - 1 (Brief): Quick overview with core concepts (~3 chunks)
    - 2 (Basic): Key points and basic examples (~5 chunks)
    - 3 (Intermediate): Balanced detail with examples (~8 chunks) [DEFAULT]
    - 4 (In-depth): Detailed coverage with examples (~12 chunks)
    - 5 (Comprehensive): Exhaustive coverage (~15 chunks)
    
    Args:
        depth: Integer rating from 1-5
        
    Returns:
        Number of chunks to retrieve for content generation
    """
    depth_to_chunks = {
        1: 3,   # Brief overview
        2: 5,   # Basic understanding
        3: 8,   # Intermediate detail (DEFAULT)
        4: 12,  # In-depth coverage
        5: 15   # Comprehensive coverage
    }
    # Clamp input to valid range and default to intermediate (3)
    normalized_depth = max(1, min(5, depth if isinstance(depth, int) else 3))
    return depth_to_chunks[normalized_depth]

def run_pipeline(
    sources: Dict[str, List[str]],
    topics: List[Dict[str, Any]],
    language: str = "en",
    style: str = "concise",
    content_types: List[str] = ["notes", "summary", "mcqs"],
    default_depth: int = 3  # Default to intermediate detail level
) -> Dict[str, Any]:
    """
    Run the combined sources pipeline.
    
    Args:
        sources: Dictionary containing lists of video URLs, article URLs, and file paths
        topics: List of topics with name and depth
        language: Output language
        style: Content style (concise/detailed)
        content_types: List of content types to generate
    """
    print(">>> Loading .env and prepping folders ...")
    load_dotenv()
    _ensure_dirs()
    
    all_texts = []
    
    # 1. Process all sources
    if videos := sources.get("videos", []):
        all_texts.extend(process_youtube_sources(videos))
    
    if articles := sources.get("articles", []):
        all_texts.extend(process_article_sources(articles))
        
    if files := sources.get("files", []):
        all_texts.extend(process_file_sources(files))
    
    # 2. Chunk all content
    print(">>> Chunking all content ...")
    all_chunks = []
    for text in all_texts:
        chunks = make_chunks(text)
        all_chunks.extend(chunks)
    print(f"    Total chunks: {len(all_chunks)}")
    
    # 3. Embed chunks
    print(">>> Embedding chunks ...")
    embedded = embed_chunks(all_chunks)
    dim = len(embedded[0]["vector"]) if embedded else 0
    print(f"    Embedded: {len(embedded)}, dim: {dim}")
    
    # 4. Create namespace for this combined session
    namespace = f"combined_{Path(cfg.DATA_PATH).stem}"
    print(f">>> Using namespace: {namespace}")
    
    # 5. Index and upsert
    print(">>> Ensuring Pinecone index & upserting ...")
    ensure_index()
    
    # Try to clear previous data in this namespace
    try:
        delete_namespace(namespace)
        print(f"    Cleared existing data from namespace: {namespace}")
    except Exception as e:
        print(f"    No existing data to clear in namespace: {namespace}")
    
    # Upload new vectors
    count = upsert_chunks(
        namespace=namespace,
        embedded_chunks=embedded,
        batch_size=100
    )
    print(f"    Upserted: {count} vectors into namespace: {namespace}")
    
    # 6. Process each topic
    results = {}
    for topic in topics:
        topic_name = topic["name"]
        
        # Get topic depth - allows individual control per topic
        # - If topic has explicit depth, use it
        # - Otherwise fall back to default_depth parameter
        # - depth of 3 (intermediate) is the final fallback
        depth = topic.get("depth", default_depth)
        chunks_to_retrieve = get_chunks_per_depth(depth)
        
        print(f">>> Processing topic: {topic_name} (depth: {depth}, chunks: {chunks_to_retrieve})")
        
        # Retrieve relevant chunks for this topic based on depth setting
        # Retrieve relevant chunks using the topic name as a query
        hits = retrieve_from_queries(
            namespace=namespace,
            queries=[topic_name],  # Single query using the topic name
            per_query_k=chunks_to_retrieve,
            final_k=chunks_to_retrieve,
            include_text=True
        )
        
        # Generate content
        topic_result = generate_all(
            namespace=namespace,
            topic=topic_name,
            queries=[topic_name],  # Using topic name as the main query
            level="intermediate",  # Could be made configurable
            style=style,
            language=language,
            final_k=chunks_to_retrieve,
            max_context_chars=6000,
            model_name=getattr(cfg, "LLM_MODEL_NAME", "gemini-1.5-flash"),
            mcq_count=5  # Could be made configurable
        )
        
        results[topic_name] = topic_result
    
    # 7. Save results
    out_dir = Path(cfg.DATA_PATH) / "outputs"
    _save_json(results, out_dir / "combined_results.json")
    
    # 8. Generate PPT and PDF notes
    ppt_path = build_ppt_from_result({"results": results})
    pdf_path = build_notes_pdf(results)
    
    return {
        "results": results,
        "ppt_path": str(ppt_path),
        "pdf_path": str(pdf_path)
    }
