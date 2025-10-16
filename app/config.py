import os

# ==== API Keys ====
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")          # not used with youtube-transcript-api
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")            # for Gemini (generator step later)
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")        # for vector DB (later)

# ==== Models ====
# LLM (for generator step later; we’re just recording intent here)
LLM_PROVIDER = "google"
LLM_MODEL_NAME = "gemini-1.5-flash"

# Embeddings (local + free)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # SentenceTransformers

# ==== Paths ====
DATA_PATH = "data/"
TEMP_PATH = "temp/"
VECTOR_DB_NAME = "yt-notes-index"

# ==== Chunking ====
CHUNK_SIZE = 800
CHUNK_OVERLAP = 160  # 20%
CHUNK_MIN = 600
CHUNK_MAX = 1000
# Tokenizer used for chunk sizing (approx for Gemini; perfect for OpenAI)
TOKENIZER = "o200k_base"  # fallbacks to cl100k_base if unavailable

# ==== Retrieval ====
TOP_K = 8
USE_MMR = False
MMR_LAMBDA = 0.5

# ==== Translation (LibreTranslate) ====
LT_URL = os.environ.get("LT_URL", "https://libretranslate.com")
LT_API_KEY = os.environ.get("LT_API_KEY", "")
PREFERRED_LANGUAGE = "en"  # always prefer English

# Pinecone serverless location (edit if needed)
PINECONE_CLOUD = os.environ.get("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.environ.get("PINECONE_REGION", "us-east-1")
PINECONE_METRIC = "cosine"  # already used; keep as-is

