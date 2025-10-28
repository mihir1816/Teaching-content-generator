from flask import jsonify, request
from app.services.generate_plan import generate_plan

def generate_plan_controller():
    try:
        data = request.get_json()
        
        level = data.get("level")
        style = data.get("style")
        topics = data.get("topics")
        description = data.get("description")
        language = data.get("language", "en")
        model_name = data.get("model_name")

        if not level or not style or not topics:
            return jsonify({
                "success": False,
                "message": "Missing required fields: level, style, topics"
            }), 400

        result = generate_plan(
            level=level,
            style=style,
            topics=topics,
            description=description,
            language=language,
            model_name=model_name
        )

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
        
        
