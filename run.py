import os
from dotenv import load_dotenv
from app.api import create_app

load_dotenv()  # read .env if present

app = create_app()

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("APP_DEBUG", "true").lower() in ("1", "true", "yes", "y")
    app.run(host=host, port=port, debug=debug)
