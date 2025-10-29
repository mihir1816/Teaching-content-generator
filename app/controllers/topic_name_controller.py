from flask import request, jsonify
from app.main.main_topic_name import generate_content_from_plan
import json

def run_pipeline_controller():
    try:
        data = request.get_json()
        plan_text = data.get("plan_text")
        topics = data.get("topics", [])  # New: list of topics
        level = data.get("level", "beginner")
        style = data.get("style", "concise")

        # Validate that either plan_text or topics is provided
        if not plan_text and not topics:
            return jsonify({"error": "Missing required field: either 'plan_text' or 'topics' must be provided"}), 400

        # If plan_text is provided, parse it
        if plan_text:
            try:
                plan_dict = json.loads(plan_text)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON in plan_text"}), 400
        else:
            # If only topics provided, create a simple plan dict
            plan_dict = {
                "topics": topics,
                "topic": topics[0] if topics else "Untitled Topic"
            }

        # Call main function with plan dict
        result = generate_content_from_plan(plan=plan_dict, level=level, style=style)

        return jsonify({
            "message": "Pipeline executed successfully!",
            "result": result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500