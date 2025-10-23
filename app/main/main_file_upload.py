"""
Main orchestrator for file upload-based teaching content generation pipeline.
"""
import os
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import cfg
from app.services.file_extractor import process_file_storage
from app.services.chunker import make_chunks
from app.services.embeddings import embed_chunks
from app.services.generate_queries import generate_queries_from_plan
from app.services.generator import generate_all
from app.services.pinecone_index import ensure_index, upsert_chunks
import logging

logger = logging.getLogger(__name__)


def run_pipeline(file_storage, plan: dict) -> dict:
    """
    Run complete file upload → teaching content pipeline.
    
    Args:
        file_storage: Flask FileStorage object (uploaded file)
        plan: dict with subject, grade_level, learning_outcomes, content_types
        
    Returns:
        dict with generated teaching materials
    """
    try:
        # 1. Extract text from uploaded file
        logger.info(f"Extracting text from file: {file_storage.filename}")
        extraction_result = process_file_storage(file_storage)
        
        # Combine all pages' text
        pages = extraction_result.get("pages", [])
        if not pages:
            raise ValueError("No text content extracted from file")
        
        file_text = "\n\n".join([p.get("text", "") for p in pages if p.get("text")])
        
        if not file_text.strip():
            raise ValueError("No text content extracted from file")
        
        logger.info(f"File extracted: {extraction_result['metadata']['file_name']}")
        logger.info(f"Extraction method: {extraction_result['extraction_method']}")
        logger.info(f"File text length: {len(file_text)} characters")
        logger.info(f"Pages extracted: {len(pages)}")
        
        # 2. Chunk the text
        logger.info("Chunking file text...")
        chunks = make_chunks(file_text)
        
        if not chunks or not isinstance(chunks, list):
            raise ValueError(f"Invalid chunks returned: {type(chunks)}")
        
        logger.info(f"Created {len(chunks)} chunks")
        
        # 3. Generate embeddings
        logger.info("Generating embeddings...")
        vectors = embed_chunks(chunks)
        
        if not vectors or not isinstance(vectors, list):
            raise ValueError(f"Invalid vectors returned: {type(vectors)}")
        
        logger.info(f"Generated {len(vectors)} embeddings")
        
        # 4. Initialize Pinecone
        logger.info(f"Initializing Pinecone...")
        ensure_index()
        logger.info(f"Pinecone index ready")
        
        # 5. Create namespace for this file
        filename = extraction_result['metadata']['file_name']
        file_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        namespace = f"file:{file_hash}:{timestamp}"
        
        logger.info(f"Using namespace: {namespace}")
        
        # 6. Upsert to Pinecone
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
        
        # Use the generalized generator
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
        output_dir = os.path.join(cfg.DATA_PATH, "file_upload_outputs")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"file_{file_hash}_{timestamp}.json")
        
        # Create file metadata
        file_meta = {
            "file_name": filename,
            "file_size": extraction_result['metadata']['file_size'],
            "file_type": extraction_result['metadata']['file_type'],
            "page_count": extraction_result['metadata']['page_count'],
            "language": extraction_result['metadata']['language'],
            "extraction_method": extraction_result['extraction_method'],
            "extraction_timestamp": extraction_result['metadata']['extraction_timestamp'],
            "source": "file_upload"
        }
        
        final_output = {
            "file": file_meta,
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
            "file": file_meta,
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
