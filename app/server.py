from flask import Flask
from app.routes.plan_routes import plan_bp
from app.routes.yt_pipeline_routes import yt_pipeline
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # optional, but useful if frontend is separate

# Register blueprints (routes)
app.register_blueprint(plan_bp, url_prefix="/api/plan")
app.register_blueprint(yt_pipeline, url_prefix="/api/pipeline")

@app.route("/", methods=["GET"])
def home():
    return {"message": "🚀 Teaching Content Generator API Running"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    