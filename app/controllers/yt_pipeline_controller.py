# # app/controllers/pipeline_controller.py
# from flask import request, jsonify
# from app.main.main_youtube import run_pipeline

# def run_pipeline_controller():
#     try:
#         data = request.get_json()
#         video = data.get("video")
#         plan_text = data.get("plan_text")
#         level = data.get("level", "beginner")
#         style = data.get("style", "concise")
#         topics = data.get("topics")

#         # Call the main function
#         run_pipeline(
#             video=video,
#             plan_text=plan_text,
#             topics=topics,
#             level=level,
#             style=style,
#         )

#         return jsonify({"message": "Pipeline executed successfully!"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

from flask import request, jsonify
from app.main.main_youtube import run_pipeline
from pathlib import Path

def run_pipeline_controller():
    try:
        data = request.get_json()
        video = data.get("video")
        plan_text = data.get("plan_text")
        level = data.get("level", "beginner")
        style = data.get("style", "concise")
        topics = data.get("topics")

        # Run main pipeline
        result = run_pipeline(
            video=video,
            plan_text=plan_text,
            topics=topics,
            level=level,
            style=style,
        )

        # Extract PPT path if present
        ppt_filename = None
        if result and isinstance(result, dict):
            full_ppt_path = result.get("_ppt_path") or result.get("ppt_path")
            if full_ppt_path:
                try:
                    ppt_filename = Path(full_ppt_path).name
                except Exception:
                    ppt_filename = str(full_ppt_path).split("/")[-1].split("\\")[-1]
        
        print(ppt_filename)
        response = {
            "message": "Pipeline executed successfully!",
            "result": result,
            "ppt_filename": ppt_filename,
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
