
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Railway Public URL

DASHBOARD_USER = os.getenv("DASHBOARD_USER", "admin")
DASHBOARD_PASS = os.getenv("DASHBOARD_PASS", "changeme")

FLASK_SECRET = os.getenv("FLASK_SECRET", "secret")
PORT = int(os.getenv("PORT", 8000))

DATA_DIR = os.path.join(os.getcwd(), "data")
TEMP_DIR = os.path.join(DATA_DIR, "temp")
DB_PATH = os.path.join(DATA_DIR, "bot_data.db")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
