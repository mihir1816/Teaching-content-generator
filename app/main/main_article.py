"""
Main orchestrator for article-based teaching content generation pipeline.
"""
import os
import json
from datetime import datetime
from app.config import cfg
from app.services.web_article import get_article_text
from app.services.chunker import make_chunks
from app.services.embeddings import embed_chunks
from app.services.pinecone_index import ensure_index, upsert_chunks
from app.services.generate_queries import generate_queries_from_plan
from app.services.retriever import retrieve_from_queries
from app.services.generator import generate_all
import logging

logger = logging.getLogger(__name__)

def run_pipeline(url: str, plan: dict) -> dict:
    """
    Run complete article → teaching content pipeline.
    
    Args:
        url: Web article URL
        plan: dict with subject, grade_level, learning_outcomes, content_types
        
    Returns:
        dict with generated teaching materials
    """
    try:
        # 1. Fetch article content
        logger.info(f"Fetching article from: {url}")
        article = get_article_text(url)
        logger.info(f"Article fetched: {article['title']}")
        
        # Validate article text
        if not article.get("text"):
            raise ValueError("No text content extracted from article")
        
        # 2. Chunk the text
        logger.info("Chunking article text...")
        chunks = make_chunks(article["text"])
        
        # Validate chunks
        if not chunks or not isinstance(chunks, list):
            raise ValueError(f"Invalid chunks returned: {type(chunks)}")
        
        logger.info(f"Created {len(chunks)} chunks")
        
        # 3. Generate embeddings
        logger.info("Generating embeddings...")
        vectors = embed_chunks(chunks)
        
        # Validate vectors
        if not vectors or not isinstance(vectors, list):
            raise ValueError(f"Invalid vectors returned: {type(vectors)}")
        
        logger.info(f"Generated {len(vectors)} embeddings")
        
        # 4. Ensure Pinecone index exists
        logger.info(f"Ensuring Pinecone index exists: {cfg.PINECONE_INDEX}")
        index = ensure_index()
        
        # 5. Create namespace for this article (use domain + hash of URL)
        from urllib.parse import urlparse
        import hashlib
        domain = urlparse(url).netloc.replace("www.", "")
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        namespace = f"article:{domain}:{url_hash}"
        
        # 6. Upsert to Pinecone
        logger.info(f"Upserting to Pinecone namespace: {namespace}")
        upsert_chunks(index, vectors, namespace=namespace)
        
        # 7. Generate diverse queries from plan
        logger.info("Generating RAG queries...")
        # Convert plan dict to a formatted string for query generation
        plan_str = json.dumps(plan, indent=2)
        queries = generate_queries_from_plan(plan_str)
        logger.info(f"Generated {len(queries)} queries")
        
        # 8. Retrieve relevant contexts
        logger.info("Retrieving contexts from Pinecone...")
        contexts = retrieve_from_queries(index, queries)
        logger.info(f"Retrieved {len(contexts)} context chunks")
        
        # 9. Generate teaching materials - FIX: Pass as positional arguments only
        logger.info("Generating teaching materials with Gemini...")
        article_meta = {
            "title": article["title"],
            "url": url,
            "source": "web_article"
        }
        
        # generate_all expects positional arguments: (plan, contexts, video_meta)
        outputs = generate_all(plan, contexts, article_meta)
        
        # 10. Save outputs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(cfg.DATA_PATH, "article_outputs")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"article_{url_hash}_{timestamp}.json")
        
        # Prepare final output structure
        final_output = {
            "article": article_meta,
            "plan": plan,
            "outputs": outputs,
            "chunks_processed": len(chunks),
            "timestamp": timestamp
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Pipeline complete. Output saved to: {output_file}")
        
        return {
            "article": article_meta,
            "plan": plan,
            "outputs": outputs,
            "output_file": output_file,
            "chunks_processed": len(chunks)
        }
        
    except Exception as e:
        logger.error(f"Article pipeline failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise