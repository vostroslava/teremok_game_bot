import os
import logging

# -----------------------------
# LOGGING CONFIGURATION
# -----------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# -----------------------------
# BOT CONFIGURATION
# -----------------------------
# In a real production env, this should be loaded from env vars
# e.g., os.getenv("TELEGRAM_TOKEN")
TELEGRAM_TOKEN = "8200223342:AAHbh2Poc73PA65-HN9zrDGwmnESU5kw-ac"
