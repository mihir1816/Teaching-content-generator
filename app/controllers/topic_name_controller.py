# app/controllers/pipeline_controller.py

from flask import request, jsonify
from app.main.main_topic_name import run_pipeline

def run_pipeline_controller():
    try:
        data = request.get_json()
        plan_text = data.get("plan_text")
        level = data.get("level", "beginner")
        style = data.get("style", "concise")
        final_k = data.get("final_k", 8)
        mcq_count = data.get("mcq_count", 8)

        # Validate required field
        if not plan_text:
            return jsonify({"error": "Missing required field: plan_text"}), 400

        # Call main function
        run_pipeline(
            plan_text=plan_text,
            level=level,
            style=style,
            final_k=final_k,
            mcq_count=mcq_count,
        )

        return jsonify({"message": "Pipeline executed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
