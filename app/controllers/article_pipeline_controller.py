# """
# Controller for article-based teaching content generation pipeline.
# """
# from flask import jsonify, request
# from app.main.main_article import run_pipeline
# import logging

# logger = logging.getLogger(__name__)

# def run_pipeline_controller():
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "Request body is required"}), 400

#         # Required fields
#         url = data.get("url")
#         plan_text = data.get("plan_text")
#         topics = data.get("topics", [])
#         level = data.get("level", "undergraduate")
#         style = data.get("style", "detailed")

#         if not url or not plan_text or not topics:
#             return jsonify({"error": "url, plan_text, and topics are required"}), 400

#         logger.info(f"Starting article pipeline for URL: {url}")
#         result = run_pipeline(url, plan_text, topics, level, style)

#         return jsonify({
#             "status": "success",
#             "data": result
#         }), 200

#     except ValueError as ve:
#         logger.error(f"Validation error: {str(ve)}")
#         return jsonify({"error": str(ve)}), 400
#     except Exception as e:
#         logger.error(f"Pipeline error: {str(e)}")
#         return jsonify({"error": f"Pipeline failed: {str(e)}"}), 500

from flask import jsonify, request
from app.main.main_article import run_pipeline
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def run_pipeline_controller():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        url = data.get("url")
        plan_text = data.get("plan_text")
        topics = data.get("topics", [])
        level = data.get("level", "undergraduate")
        style = data.get("style", "detailed")

        if not url or not plan_text or not topics:
            return jsonify({"error": "url, plan_text, and topics are required"}), 400

        logger.info(f"Starting article pipeline for URL: {url}")
        result = run_pipeline(url, plan_text, topics, level, style)

        # --- Extract PPT path if present ---
        ppt_filename = None
        if result and isinstance(result, dict):
            full_ppt_path = result.get("_ppt_path") or result.get("ppt_path")
            if full_ppt_path:
                try:
                    ppt_filename = Path(full_ppt_path).name
                except Exception:
                    ppt_filename = str(full_ppt_path).split("/")[-1].split("\\")[-1]

        return jsonify({
            "status": "success",
            "data": result,
            "ppt_filename": ppt_filename,
        }), 200

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        return jsonify({"error": f"Pipeline failed: {str(e)}"}), 500
