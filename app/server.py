import os
import sys
# Add parent directory to path for imports to work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from app.routes.plan_routes import plan_bp
from app.routes.yt_pipeline_routes import yt_pipeline
from flask_cors import CORS
from dotenv import load_dotenv
from app.routes.article_pipeline_routes import article_pipeline
from app.routes.topic_name_routes import topic_name_pipeline
from app.routes.file_upload_routes import file_upload_bp
from app.routes.combined_routes import combined_pipeline
load_dotenv()

app = Flask(__name__)
CORS(app) 

# Register blueprints (routes)
app.register_blueprint(plan_bp, url_prefix="/api/plan")
app.register_blueprint(yt_pipeline, url_prefix="/api/yt_pipeline")
app.register_blueprint(article_pipeline, url_prefix="/api/article_pipeline")
app.register_blueprint(topic_name_pipeline, url_prefix="/api/topic_pipeline")
app.register_blueprint(file_upload_bp, url_prefix="/api/file_upload")
app.register_blueprint(combined_pipeline, url_prefix="/api/combined_pipeline")


@app.route("/", methods=["GET"])
def home():
    return {"message": "🚀 Teaching Content Generator API Running", "status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
    
# python -m flask --app app.server run --port 5000