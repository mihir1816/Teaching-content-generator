# app/routes/pipeline_routes.py
from flask import Blueprint, jsonify
from app.controllers.yt_pipeline_controller import run_pipeline_controller
from flask import send_from_directory, request
from pathlib import Path

yt_pipeline = Blueprint("yt_pipeline", __name__)

@yt_pipeline.route("/run_yt_pipeline", methods=["POST"])
def run_pipeline_route():
    return run_pipeline_controller()

@yt_pipeline.route("/download_ppt/<path:filename>", methods=["GET"])
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