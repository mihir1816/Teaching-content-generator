from flask import request, jsonify
from app.main.main_topic_name import generate_content_from_plan
import json

def run_pipeline_controller():
    try:
        data = request.get_json()
        plan_text = data.get("plan_text")
        level = data.get("level", "beginner")
        style = data.get("style", "concise")


        # Validate required field
        if not plan_text:
            return jsonify({"error": "Missing required field: plan_text"}), 400

        # Parse JSON string into Python dict
        try:
            plan_dict = json.loads(plan_text)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON in plan_text"}), 400

        # Call main function with plan dict
        result = generate_content_from_plan(plan=plan_dict , level=level, style=style)

        return jsonify({
            "message": "Pipeline executed successfully!",
            "result": result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500