from flask import Flask
from app.routes.plan_routes import plan_bp
from app.routes.yt_pipeline_routes import yt_pipeline
from flask_cors import CORS
from dotenv import load_dotenv
from app.routes.article_pipeline_routes import article_pipeline
from app.routes.topic_name_routes import topic_name_pipeline
load_dotenv()

app = Flask(__name__)
CORS(app) 

# Register blueprints (routes)
app.register_blueprint(plan_bp, url_prefix="/api/plan")
app.register_blueprint(yt_pipeline, url_prefix="/api/yt_pipeline")
app.register_blueprint(article_pipeline, url_prefix="/api/article_pipeline")
app.register_blueprint(topic_name_pipeline, url_prefix="/api/topic_pipeline")


@app.route("/", methods=["GET"])
def home():
    return {"message": "🚀 Teaching Content Generator API Running"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    
    