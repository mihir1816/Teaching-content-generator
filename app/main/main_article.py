"""
Main orchestrator for article-based teaching content generation pipeline.
"""
import os
import json
import time
from datetime import datetime
from app.config import cfg
from app.services.web_article import get_article_text
from app.services.chunker import make_chunks
from app.services.embeddings import embed_chunks
from app.services.generate_queries import generate_queries_from_plan
from app.services.generator import generate_all
from app.services.pinecone_index import upsert_chunks
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
        logger.info(f"Article text length: {len(article['text'])} characters")
        
        if not article.get("text"):
            raise ValueError("No text content extracted from article")
        
        # 2. Chunk the text
        logger.info("Chunking article text...")
        chunks = make_chunks(article["text"])
        
        if not chunks or not isinstance(chunks, list):
            raise ValueError(f"Invalid chunks returned: {type(chunks)}")
        
        logger.info(f"Created {len(chunks)} chunks")
        
        # 3. Generate embeddings
        logger.info("Generating embeddings...")
        vectors = embed_chunks(chunks)
        
        if not vectors or not isinstance(vectors, list):
            raise ValueError(f"Invalid vectors returned: {type(vectors)}")
        
        logger.info(f"Generated {len(vectors)} embeddings")
        
        # 4. Initialize Pinecone using the generalized approach
        logger.info(f"Initializing Pinecone...")
        from app.services.pinecone_index import ensure_index
        
        # Ensure index exists (creates if needed)
        ensure_index()
        logger.info(f"Pinecone index ready")
        
        # 5. Create namespace for this article
        from urllib.parse import urlparse
        import hashlib
        domain = urlparse(url).netloc.replace("www.", "")
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        namespace = f"article:{domain}:{url_hash}"
        
        logger.info(f"Using namespace: {namespace}")
        
        # 6. Upsert to Pinecone using generalized approach
        logger.info(f"Upserting {len(vectors)} vectors to Pinecone namespace '{namespace}'...")
        
        # Prepare embedded chunks for the generalized upsert function
        embedded_chunks = []
        for i, vec in enumerate(vectors):
            try:
                if isinstance(vec, dict):
                    vector_values = vec.get('vector', vec.get('values', []))
                    chunk_text = vec.get('text', str(chunks[i]) if i < len(chunks) else "")
                    
                elif hasattr(vec, 'values') and hasattr(vec, 'id'):
                    vector_values = vec.values() if callable(vec.values) else vec.values
                    chunk_text = str(chunks[i]) if i < len(chunks) else ""
                    
                else:
                    vector_values = vec
                    chunk_text = str(chunks[i]) if i < len(chunks) else ""
                
                import numpy as np
                if isinstance(vector_values, np.ndarray):
                    vector_values = vector_values.tolist()
                elif not isinstance(vector_values, list):
                    vector_values = list(vector_values)
                
                if not vector_values:
                    raise ValueError(f"vector_values is empty for vector {i}")
                
                if not isinstance(vector_values[0], (int, float)):
                    raise ValueError(f"vector_values contains non-numeric data: {type(vector_values[0])}")
                
                embedded_chunks.append({
                    "id": f"{namespace}_{i}",
                    "text": chunk_text,
                    "vector": vector_values
                })
                
            except Exception as e:
                logger.error(f"Failed to process vector {i}: {e}")
                logger.error(f"Vector type: {type(vec)}")
                if isinstance(vec, dict):
                    logger.error(f"Vector keys: {list(vec.keys())}")
                raise
        
        # Use the generalized upsert function
        upserted_count = upsert_chunks(
            namespace=namespace,
            embedded_chunks=embedded_chunks,
            batch_size=100,
            store_text_metadata=True
        )
        
        logger.info(f"Upsert completed successfully: {upserted_count} vectors")
        
        # Wait for Pinecone to index
        logger.info("Waiting for Pinecone indexing...")
        time.sleep(5)
        
        # 7. Generate queries
        logger.info("Generating RAG queries...")
        plan_str = json.dumps(plan, indent=2)
        queries = generate_queries_from_plan(plan_str)
        logger.info(f"Generated {len(queries)} queries")
        
        # 8. Generate teaching materials using the generalized generator
        logger.info("Generating teaching materials with generalized generator...")
        
        # Extract plan parameters
        subject = plan.get('subject', 'General Topic')
        learning_outcomes = plan.get('learning_outcomes', [])
        
        # Create focused 1-sentence topic
        if learning_outcomes:
            topic_statement = f"{subject}: {learning_outcomes[0]}"
        else:
            topic_statement = subject
        
        # Extract level and normalize it
        grade_level = plan.get('grade_level', 'beginner')
        level_map = {
            '9th grade': 'beginner',
            '10th grade': 'beginner', 
            '11th grade': 'intermediate',
            '12th grade': 'intermediate',
            'high school': 'intermediate',
            'college': 'advanced',
            'university': 'advanced'
        }
        level = level_map.get(grade_level.lower(), 'beginner')
        
        logger.info(f"Topic: {topic_statement}")
        logger.info(f"Level: {level}")
        logger.info(f"Queries: {len(queries)}")
        
        # Use the generalized generator with the new approach
        outputs = generate_all(
            namespace=namespace,
            topic=topic_statement,
            queries=queries,
            level=level,
            style="detailed",
            language="en",
            final_k=8,
            max_context_chars=6000,
            mcq_count=10
        )
        
        # Check output quality
        summary_text = outputs.get('summary', {}).get('summary', '')
        mcq_count = len(outputs.get('mcqs', {}).get('questions', []))
        
        if summary_text and summary_text != "insufficient information":
            logger.info(f"Generated summary ({len(summary_text)} chars) and {mcq_count} MCQs")
        else:
            logger.error("Failed to generate content")
        
        # 9. Save outputs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(cfg.DATA_PATH, "article_outputs")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"article_{url_hash}_{timestamp}.json")
        
        # Create article metadata
        article_meta = {
            "title": article["title"],
            "url": url,
            "source": "web_article"
        }
        
        final_output = {
            "article": article_meta,
            "plan": plan,
            "outputs": outputs,
            "chunks_processed": len(chunks),
            "queries_generated": len(queries),
            "namespace": namespace,
            "timestamp": timestamp
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Pipeline complete. Saved to: {output_file}")
        
        return {
            "article": article_meta,
            "plan": plan,
            "outputs": outputs,
            "output_file": output_file,
            "chunks_processed": len(chunks),
            "queries_generated": len(queries),
            "namespace": namespace
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    
    
    