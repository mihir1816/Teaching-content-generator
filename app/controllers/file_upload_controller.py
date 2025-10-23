"""
Controller to handle file uploads for the File Upload flow.
Accepts multipart form-data with 'file' (single file) and plan data as form fields.
Calls the main_file_upload pipeline and returns teaching content.
"""
from flask import request, jsonify
import json
import logging
from app.main.main_file_upload import run_pipeline

logger = logging.getLogger(__name__)


def upload_files_controller():
    """
    HTTP endpoint to run file upload pipeline.
    
    Expected form-data:
    - file: The uploaded file (PDF, DOCX, TXT, images, etc.)
    - subject: Subject/topic name
    - grade_level: Grade level (e.g., "10th Grade", "beginner", "intermediate")
    - learning_outcomes: JSON array of learning outcomes (optional)
    - content_types: JSON array of content types (optional, defaults to ["notes", "summary", "mcqs"])
    """
    try:
        # Check for file
        if 'file' not in request.files:
            return jsonify({"error": "No file in the request. Use form field 'file'."}), 400

        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({"error": "No file selected."}), 400

        # Get plan data from form fields
        subject = request.form.get('subject')
        grade_level = request.form.get('grade_level')
        
        if not subject or not grade_level:
            return jsonify({"error": "subject and grade_level are required"}), 400
        
        # Parse learning_outcomes if provided
        learning_outcomes_str = request.form.get('learning_outcomes', '[]')
        try:
            learning_outcomes = json.loads(learning_outcomes_str)
        except json.JSONDecodeError:
            return jsonify({"error": "learning_outcomes must be a valid JSON array"}), 400
        
        # Parse content_types if provided
        content_types_str = request.form.get('content_types', '["notes", "summary", "mcqs"]')
        try:
            content_types = json.loads(content_types_str)
        except json.JSONDecodeError:
            return jsonify({"error": "content_types must be a valid JSON array"}), 400
        
        # Build plan
        plan = {
            "subject": subject,
            "grade_level": grade_level,
            "learning_outcomes": learning_outcomes,
            "content_types": content_types
        }
        
        # Run pipeline
        logger.info(f"Starting file upload pipeline for file: {file.filename}")
        logger.info(f"Plan: {json.dumps(plan, indent=2)}")
        
        result = run_pipeline(file, plan)
        
        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Pipeline failed: {str(e)}"}), 500
