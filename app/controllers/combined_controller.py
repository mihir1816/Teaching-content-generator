"""
Controller for combined sources (YouTube + Articles + Files) teaching content generation.
"""
from flask import request, jsonify
import logging
import json
from app.main.main_combined import run_pipeline

logger = logging.getLogger(__name__)

def run_pipeline_controller():
    """
    Handle POST request for combined pipeline.
    Accepts multipart/form-data with:
    - videos: JSON array of YouTube URLs (form field)
    - articles: JSON array of article URLs (form field)
    - files: Multiple file uploads (form field, can be multiple)
    - plan_text: Learning plan text (form field)
    - topics: JSON array of topics (form field)
    - level: Learning level (form field, default: beginner)
    - style: Content style (form field, default: concise)
    """
    try:
        # Get form fields
        videos_str = request.form.get('videos', '[]')
        articles_str = request.form.get('articles', '[]')
        plan_text = request.form.get('plan_text')
        topics_str = request.form.get('topics')
        level = request.form.get('level', 'beginner')
        style = request.form.get('style', 'concise')
        
        # Get uploaded files
        uploaded_files = request.files.getlist('files')
        
        # Validate at least one source is provided
        if not videos_str.strip() and not articles_str.strip() and not uploaded_files:
            return jsonify({
                "status": "error",
                "message": "At least one source (videos, articles, or files) must be provided"
            }), 400
        
        # Parse JSON strings
        try:
            videos = json.loads(videos_str) if videos_str.strip() else []
            articles = json.loads(articles_str) if articles_str.strip() else []
            topics = json.loads(topics_str) if topics_str else []
        except json.JSONDecodeError as e:
            return jsonify({
                "status": "error",
                "message": f"Invalid JSON format: {str(e)}"
            }), 400
        
        # Validate required fields
        if not plan_text:
            return jsonify({
                "status": "error",
                "message": "Missing required field: plan_text"
            }), 400
        
        if not topics or not isinstance(topics, list):
            return jsonify({
                "status": "error",
                "message": "topics must be a non-empty list"
            }), 400
        
        # Validate list types
        if not isinstance(videos, list):
            return jsonify({
                "status": "error",
                "message": "videos must be a list"
            }), 400
        
        if not isinstance(articles, list):
            return jsonify({
                "status": "error",
                "message": "articles must be a list"
            }), 400
        
        logger.info(f"Processing combined sources:")
        logger.info(f"  Videos: {len(videos)}")
        logger.info(f"  Articles: {len(articles)}")
        logger.info(f"  Files: {len(uploaded_files)}")
        logger.info(f"Plan: {plan_text}")
        logger.info(f"Topics: {topics}")
        logger.info(f"Level: {level}, Style: {style}")
        
        # Build sources dictionary
        sources = {
            "videos": videos,
            "articles": articles,
            "files": uploaded_files  # Pass FileStorage objects directly
        }
        
        # Call the main pipeline function
        result = run_pipeline(
            sources=sources,
            plan_text=plan_text,
            topics=topics,
            level=level,
            style=style
        )
        
        return jsonify({
            "status": "success",
            "data": result
        }), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"Pipeline failed: {str(e)}"
        }), 500