# app/controllers/pipeline_controller.py

from flask import request, jsonify
from app.main.main_topic_name import generate_content_from_plan

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
        generate_content_from_plan(
            plan_text=plan_text
        )

        return jsonify({"message": "Pipeline executed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500