from flask import Flask, Blueprint, jsonify
import app.config as cfg

api_bp = Blueprint("api", __name__)

@api_bp.get("/health")
def health():
    return jsonify({
        "ok": True,
        "llm_provider": cfg.LLM_PROVIDER,
        "llm_model": cfg.LLM_MODEL_NAME,
        "embedding_model": cfg.EMBEDDING_MODEL_NAME,
        "vector_index": cfg.VECTOR_DB_NAME,
        "top_k": cfg.TOP_K,
        "chunk": {"size": cfg.CHUNK_SIZE, "overlap": cfg.CHUNK_OVERLAP},
    })

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.register_blueprint(api_bp, url_prefix="/api")
    return app
