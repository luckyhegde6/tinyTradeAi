import requests
import time
from utils.security import validate_telegram_request, get_telegram_credentials
from utils.helpers import setup_logger
from database.db import get_market_data, get_recent_sentiment

logger = setup_logger("TelegramBot")

class TinyTradeBot:
    def __init__(self):
        self.token, self.chat_id = get_telegram_credentials()
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.last_update_id = 0
        
    def send_message(self, text):
        if not self.token or not self.chat_id:
            return
            
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")

    def process_updates(self):
        if not self.token:
            return
            
        url = f"{self.api_url}/getUpdates?offset={self.last_update_id + 1}&timeout=5"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if data.get("ok"):
                for result in data["result"]:
                    self.last_update_id = result["update_id"]
                    msg = result.get("message")
                    
                    if not msg or "text" not in msg:
                        continue
                        
                    incoming_chat_id = msg["chat"]["id"]
                    
                    # ZERO TRUST CHECK
                    if not validate_telegram_request(incoming_chat_id):
                        continue # Drop silently
                        
                    text = msg["text"].strip()
                    self.handle_command(text)
                    
        except requests.exceptions.RequestException:
            pass # Ignore timeout/connection errors during polling
        except Exception as e:
            logger.error(f"Telegram polling error: {e}")

    def handle_command(self, text):
        if text == "/status":
            self.send_message("🟢 TinyTrade AI is running nominal.")
            
        elif text == "/prices":
            prices = get_market_data()
            if not prices:
                self.send_message("No price data available yet.")
                return
                
            msg = "<b>Live Prices:</b>\n"
            for p in prices:
                msg += f"{p['symbol']}: ${p['price']} ({p['change_24h']:.2f}%)\n"
            self.send_message(msg)
            
        elif text == "/sentiment":
            sents = get_recent_sentiment(3)
            if not sents:
                self.send_message("No sentiment data.")
                return
                
            msg = "<b>Latest Sentiment:</b>\n"
            for s in sents:
                msg += f"[{s['label']}] {s['headline'][:40]}...\n"
            self.send_message(msg)
            
        else:
            self.send_message("Commands: /status, /prices, /sentiment")

# Global instance for alerts
_bot_instance = None

def get_bot():
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = TinyTradeBot()
    return _bot_instance

def send_alert_to_telegram(message):
    """Called by anomaly detection to push critical alerts."""
    bot = get_bot()
    bot.send_message(f"🚨 <b>ALERT</b> 🚨\n{message}")

def poll_telegram():
    """Blocking polling loop to be run in a background thread."""
    bot = get_bot()
    if not bot.token:
        logger.warning("Telegram token missing. Bot disabled.")
        return
        
    logger.info("Starting Telegram polling thread...")
    while True:
        bot.process_updates()
        time.sleep(2) # Keep CPU usage extremely low
