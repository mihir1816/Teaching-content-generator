"""
Controller to handle file uploads for the File Upload flow.
Accepts multipart form-data with one or more files under the field name 'files'.
Calls the file_extractor service and returns structured JSON.
"""
from flask import request, jsonify
from app.services.file_extractor import process_file_storage
import logging

logger = logging.getLogger(__name__)


def upload_files_controller():
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files part in the request. Use form field 'files'."}), 400

        files = request.files.getlist('files')
        if not files:
            return jsonify({"error": "No files uploaded."}), 400

        results = []
        errors = []
        for f in files:
            try:
                out = process_file_storage(f)
                results.append(out)
            except Exception as e:
                logger.exception("Extraction failed for %s: %s", f.filename, str(e))
                errors.append({"file_name": f.filename, "error": str(e)})

        response = {"status": "partial" if errors and results else ("error" if errors and not results else "success"),
                    "results": results,
                    "errors": errors}
        code = 207 if errors and results else (400 if errors and not results else 200)
        return jsonify(response), code

    except Exception as e:
        logger.exception("Unexpected error in upload_files_controller: %s", str(e))
        return jsonify({"error": str(e)}), 500
