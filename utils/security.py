import os
from dotenv import load_dotenv
from utils.helpers import setup_logger

logger = setup_logger("Security")
load_dotenv()

# We strictly enforce that only the owner can interact with the bot
ALLOWED_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def validate_telegram_request(chat_id):
    """
    Zero Trust Principle: Drop anything that isn't explicitly allowed.
    """
    if not ALLOWED_CHAT_ID:
        logger.error("CRITICAL: TELEGRAM_CHAT_ID not set in environment.")
        return False
        
    # Strict string comparison
    if str(chat_id) != str(ALLOWED_CHAT_ID):
        logger.warning("SECURITY BREACH ATTEMPT: Unauthorized chat_id %s attempted access. Dropping silently." % chat_id)
        return False
        
    return True

def get_telegram_credentials():
    return TELEGRAM_BOT_TOKEN, ALLOWED_CHAT_ID
