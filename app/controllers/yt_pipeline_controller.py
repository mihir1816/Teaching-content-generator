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
        topics = data.get("topics")

        # Call the main function
        run_pipeline(
            video=video,
            plan_text=plan_text,
            topics=topics,
            level=level,
            style=style,
        )

        return jsonify({"message": "Pipeline executed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
