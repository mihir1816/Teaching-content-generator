"""
Controller for article-based teaching content generation pipeline.
"""
from flask import jsonify, request
from app.main.main_article import run_pipeline
import logging

logger = logging.getLogger(__name__)

def run_pipeline_controller():
    """
    HTTP endpoint to run article pipeline.
    
    Expected JSON body:
    {
        "url": "https://example.com/article",
        "subject": "Physics",
        "grade_level": "10th Grade",
        "learning_outcomes": ["Understand Newton's laws", "Apply force calculations"],
        "content_types": ["notes", "summary", "mcqs"]  # optional
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        url = data.get("url")
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        subject = data.get("subject")
        grade_level = data.get("grade_level")
        learning_outcomes = data.get("learning_outcomes", [])
        
        if not subject or not grade_level:
            return jsonify({"error": "subject and grade_level are required"}), 400
        
        # Build plan (similar to YouTube plan structure)
        plan = {
            "subject": subject,
            "grade_level": grade_level,
            "learning_outcomes": learning_outcomes,
            "content_types": data.get("content_types", ["notes", "summary", "mcqs"])
        }
        
        # Run pipeline
        logger.info(f"Starting article pipeline for URL: {url}")
        result = run_pipeline(url, plan)
        
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
