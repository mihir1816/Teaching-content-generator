from flask import Blueprint
from app.controllers.topic_name_controller import run_pipeline_controller

topic_name_pipeline = Blueprint("topic_name_pipeline", __name__)

@topic_name_pipeline.route("/run_topic_name_pipeline", methods=["POST"])
def run_pipeline_route():
    return run_pipeline_controller()