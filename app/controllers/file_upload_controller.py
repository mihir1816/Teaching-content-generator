"""
Controller to handle file uploads for the File Upload flow.
Accepts multipart form-data with 'file' and plan data as form fields.
"""
from flask import request, jsonify
import logging
from app.main.main_file_upload import run_pipeline

logger = logging.getLogger(__name__)

def upload_files_controller():
    """
    Handle POST request with multipart/form-data.
    Expected fields:
    - file: The uploaded file (PDF, DOCX, TXT, PNG, JPG, TIFF)
    - plan_text: JSON string with plan details
    - topics: JSON array of topics
    - level: beginner/intermediate/advanced
    - style: concise/detailed/exam-prep
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No file part in request"
            }), 400
        
        file_storage = request.files['file']
        
        if file_storage.filename == '':
            return jsonify({
                "status": "error",
                "message": "No file selected"
            }), 400
        
        # Get form fields
        plan_text = request.form.get('plan_text')
        topics_str = request.form.get('topics')
        level = request.form.get('level', 'beginner')
        style = request.form.get('style', 'concise')
        
        # Validate required fields
        if not plan_text:
            return jsonify({
                "status": "error",
                "message": "Missing required field: plan_text"
            }), 400
        
        if not topics_str:
            return jsonify({
                "status": "error",
                "message": "Missing required field: topics"
            }), 400
        
        # Parse topics (expecting JSON array string)
        import json
        try:
            topics = json.loads(topics_str)
            if not isinstance(topics, list) or not topics:
                raise ValueError("topics must be a non-empty list")
        except (json.JSONDecodeError, ValueError) as e:
            return jsonify({
                "status": "error",
                "message": f"Invalid topics format: {str(e)}"
            }), 400
        
        logger.info(f"Processing file: {file_storage.filename}")
        logger.info(f"Plan: {plan_text}")
        logger.info(f"Topics: {topics}")
        logger.info(f"Level: {level}, Style: {style}")
        
        # Call the main pipeline function
        result = run_pipeline(
            file_storage=file_storage,
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