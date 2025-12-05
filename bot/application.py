from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from bot.handlers import (
    start, help_cmd, ai_cmd, image_cmd, voice_handler,
    addtask_cmd, tasks_cmd, cleartasks_cmd,
    remember_cmd, callback_query_handler
)

from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL
from bot.logger import LOG


def start_application(port: int):
    """Start Telegram bot using webhook mode (Railway-compatible)."""

    if not WEBHOOK_URL:
        raise RuntimeError("❌ WEBHOOK_URL missing in .env")

    LOG.info(f"Webhook URL configured: {WEBHOOK_URL}")

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ai", ai_cmd))
    app.add_handler(CommandHandler("image", image_cmd))
    app.add_handler(CommandHandler("addtask", addtask_cmd))
    app.add_handler(CommandHandler("tasks", tasks_cmd))
    app.add_handler(CommandHandler("cleartasks", cleartasks_cmd))
    app.add_handler(CommandHandler("remember", remember_cmd))

    # Voice messages
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, voice_handler))

    # Inline button callback
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    LOG.info("Setting Telegram Webhook...")

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )

