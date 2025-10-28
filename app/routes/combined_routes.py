"""
Routes for combined source teaching content generation pipeline.
"""
from flask import Blueprint
from app.controllers.combined_controller import run_pipeline_controller

combined_pipeline = Blueprint('combined_pipeline', __name__)

@combined_pipeline.route('/api/combined/generate', methods=['POST'])
def run_pipeline():
    """
    Endpoint to run the combined sources pipeline.
    """
    return run_pipeline_controller()
