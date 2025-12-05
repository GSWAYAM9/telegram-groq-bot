import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Optional APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENWEATHER_API = os.getenv("OPENWEATHER_API", "")
OMDB_API = os.getenv("OMDB_API", "")

# Dashboard Login
DASHBOARD_USER = os.getenv("DASHBOARD_USER", "admin")
DASHBOARD_PASS = os.getenv("DASHBOARD_PASS", "changeme")

# Flask Session Secret
FLASK_SECRET = os.getenv("FLASK_SECRET", "supersecret123")

# PORT Railway gives (mandatory)
PORT = int(os.getenv("PORT", 8080))

# DATA PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "bot_data.db")

# Webhook Public URL
# Railway automatically exposes: https://your-app-name.up.railway.app
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # MUST be set after deployment

# Vosk STT model path
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "vosk-model-small-en-us-0.15")
