"""
Routes for file upload extraction flow.
"""
from flask import Blueprint
from app.controllers.file_upload_controller import upload_files_controller

file_upload_bp = Blueprint('file_upload', __name__, url_prefix='/api/file_upload')


@file_upload_bp.route('/upload', methods=['POST'])
def upload_route():
    """POST /api/file_upload/upload
    Expects multipart/form-data with field name 'files' containing one or more files.
    """
    return upload_files_controller()
