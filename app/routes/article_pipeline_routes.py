"""
Routes for article-based teaching content generation.
"""
from app.controllers.article_pipeline_controller import run_pipeline_controller
from flask import Blueprint, jsonify
from flask import send_from_directory, request
from pathlib import Path
# Create blueprint
article_pipeline = Blueprint('article_pipeline', __name__)

# Register routes
@article_pipeline.route('/run_article_pipeline', methods=['POST'])
def article_pipeline_route():
    """
    POST /api/article/pipeline
    Generate teaching content from a web article URL.
    """
    return run_pipeline_controller()

@article_pipeline.route("/download_ppt/<path:filename>", methods=["GET"])
def download_ppt(filename):
    # Securely serve files from the data/outputs directory
    outputs_dir = Path("data") / "outputs"
    outputs_dir = outputs_dir.resolve()
    
    try:
        # Prevent path traversal by resolving and checking parent
        target = (outputs_dir / filename).resolve()
        if not str(target).startswith(str(outputs_dir)):
            return jsonify({"error": "Invalid filename"}), 400

        if not target.exists():
            # Helpful debug: list available files
            try:
                available = [p.name for p in outputs_dir.iterdir() if p.is_file()]
            except Exception:
                available = []
            return jsonify({"error": "File not found", "requested": filename, "available": available}), 404

        # Use send_from_directory which handles file serving and headers
        return send_from_directory(directory=str(outputs_dir), path=filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
