"""
Routes for file upload-based teaching content generation.
"""
from flask import Blueprint
from app.controllers.file_upload_controller import upload_files_controller

# Create blueprint
file_upload_bp = Blueprint('file_upload', __name__)

# Register routes
@file_upload_bp.route('/run_file_upload_pipeline', methods=['POST'])
def file_upload_pipeline_route():
    """
    POST /api/file_upload/pipeline
    Generate teaching content from an uploaded file.
    
    Expected form-data:
    - file: The uploaded file (PDF, DOCX, TXT, images, etc.)
    - subject: Subject/topic name
    - grade_level: Grade level
    - learning_outcomes: JSON array (optional)
    - content_types: JSON array (optional)
    """
    return upload_files_controller()
