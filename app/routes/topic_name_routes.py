from flask import Blueprint, send_from_directory, jsonify
from app.controllers.topic_name_controller import run_pipeline_controller
from pathlib import Path

topic_name_pipeline = Blueprint("topic_name_pipeline", __name__)

@topic_name_pipeline.route("/run_topic_name_pipeline", methods=["POST"])
def run_pipeline_route():
    return run_pipeline_controller()

@topic_name_pipeline.route("/download_ppt/<path:filename>", methods=["GET"])
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