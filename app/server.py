from flask import Flask
from routes.plan_routes import plan_bp
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # optional, but useful if frontend is separate

# Register blueprints (routes)
app.register_blueprint(plan_bp, url_prefix="/api/plan")

@app.route("/", methods=["GET"])
def home():
    return {"message": "🚀 Teaching Content Generator API Running"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    