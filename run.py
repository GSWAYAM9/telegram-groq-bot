import threading
import os
from flask import Flask
from dashboard.server import run_dashboard
from bot.handlers import build_application
from bot.utils import init_db
from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL, PORT
from bot.logger import LOG


def start_bot_webhook():
    """Start PTB v20 bot in webhook mode."""
    init_db()

    app = build_application()

    LOG.info("Starting bot in WEBHOOK mode...")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}",
    )


if __name__ == "__main__":
    # Run dashboard in background thread
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()

    # Run bot webhook in main thread
    start_bot_webhook()
