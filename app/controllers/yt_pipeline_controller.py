# app/controllers/pipeline_controller.py
from flask import request, jsonify
from app.main.main_youtube import run_pipeline

def run_pipeline_controller():
    try:
        data = request.get_json()
        video = data.get("video")
        plan_text = data.get("plan_text")
        level = data.get("level", "beginner")
        style = data.get("style", "concise")
        language = data.get("language", "en")
        reingest = data.get("reingest", True)
        final_k = data.get("final_k", 8)
        mcq_count = data.get("mcq_count", 8)

        # Call the main function
        run_pipeline(
            video=video,
            plan_text=plan_text,
            level=level,
            style=style,
            language=language,
            reingest=reingest,
            final_k=final_k,
            mcq_count=mcq_count,
        )

        return jsonify({"message": "Pipeline executed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
