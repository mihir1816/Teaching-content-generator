"""
Controller for combined source teaching content generation pipeline.
"""
from flask import jsonify, request
from app.main.main_combined import run_pipeline
import logging

logger = logging.getLogger(__name__)

def run_pipeline_controller():
    """
    HTTP endpoint to run combined sources pipeline.
    
    The endpoint accepts multiple content sources (videos, articles, files) and
    generates topic-specific content based on user preferences. Each topic can
    have an optional depth rating that controls how detailed the content should be.
    
    Expected JSON body:
    {
        "sources": {
            "videos": ["https://youtube.com/watch?v=..."],
            "articles": ["https://example.com/article1"],
            "files": ["file1.pdf", "file2.docx"]  # Base64 encoded or file paths
        },
        "topics": [
            {
                "name": "Newton's Laws",
                # Optional: depth/rating (1-5) to control content detail level
                # 1: Brief overview (~3 chunks)
                # 2: Basic understanding (~5 chunks)
                # 3: Intermediate detail (~8 chunks) [DEFAULT]
                # 4: In-depth (~12 chunks)
                # 5: Comprehensive (~15 chunks)
                "depth": 3
            }
        ],
        "config": {
            "language": "en",
            "style": "concise",
            "content_types": ["notes", "summary", "mcqs"],
            # Optional: Default depth for topics without specified depth
            "default_depth": 3  # Uses intermediate detail if not specified
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        sources = data.get("sources")
        if not sources or not any(sources.values()):
            return jsonify({"error": "At least one source (video, article, or file) is required"}), 400
        
        topics = data.get("topics")
        if not topics:
            return jsonify({"error": "At least one topic is required"}), 400
        
        config = data.get("config", {})
        
        # Get default depth setting from config (fallback to intermediate=3)
        default_depth = config.get("default_depth", 3)
        
        # Validate depth settings
        for topic in topics:
            if "depth" in topic:
                depth = topic["depth"]
                if not isinstance(depth, int) or depth < 1 or depth > 5:
                    return jsonify({
                        "error": f"Invalid depth for topic '{topic['name']}'. Must be integer 1-5"
                    }), 400
        
        # Run pipeline with depth configuration
        logger.info(f"Starting combined pipeline with {len(topics)} topics (default depth: {default_depth})")
        result = run_pipeline(
            sources=sources,
            topics=topics,
            language=config.get("language", "en"),
            style=config.get("style", "concise"),
            content_types=config.get("content_types", ["notes", "summary", "mcqs"]),
            default_depth=default_depth  # Pass default depth to pipeline
        )
        
        return jsonify({
            "status": "success",
            "data": result
        }), 200
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        return jsonify({"error": f"Pipeline failed: {str(e)}"}), 500
