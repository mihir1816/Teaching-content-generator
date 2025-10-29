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
   
    return upload_files_controller()
