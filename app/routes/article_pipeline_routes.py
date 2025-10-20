"""
Routes for article-based teaching content generation.
"""
from flask import Blueprint
from app.controllers.article_pipeline_controller import run_pipeline_controller

# Create blueprint
article_pipeline = Blueprint('article_pipeline', __name__, url_prefix='/api/article')

# Register routes
@article_pipeline.route('/run_artical_pipeline', methods=['POST'])
def article_pipeline_route():
    """
    POST /api/article/pipeline
    Generate teaching content from a web article URL.
    """
    return run_pipeline_controller()
