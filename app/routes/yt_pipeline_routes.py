# app/routes/pipeline_routes.py
from flask import Blueprint
from app.controllers.yt_pipeline_controller import run_pipeline_controller

yt_pipeline = Blueprint("yt_pipeline", __name__)

@yt_pipeline.route("/run_yt_pipeline", methods=["POST"])
def run_pipeline_route():
    return run_pipeline_controller()
