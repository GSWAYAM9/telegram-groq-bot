
import logging

LOG = logging.getLogger("telegram_groq_bot")
LOG.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
))

LOG.addHandler(handler)
