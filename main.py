import threading
import time
import schedule

from config import CRYPTO_POLL_INTERVAL, STOCKS_POLL_INTERVAL, NEWS_POLL_INTERVAL, API_HOST, API_PORT
from database.db import init_db
from utils.helpers import setup_logger
from fetchers.crypto import fetch_crypto_prices
from fetchers.stocks import fetch_stock_prices
from fetchers.news import fetch_rss_headlines
from ai.sentiment import process_news_sentiment
from ai.anomaly import check_all_assets_for_anomalies
from ai.signals import generate_signals
from oled.animations import render_next_screen
from api.app import start_flask
from api.telegram import poll_telegram

logger = setup_logger("TinyTrade_Main")

def main_loop():
    logger.info("Initializing TinyTrade AI...")
    
    # 1. Init Database
    init_db()
    
    # 2. Initial Data Fetch
    logger.info("Performing initial data fetch...")
    fetch_crypto_prices()
    fetch_stock_prices()
    process_news_sentiment()
    
    # 3. Schedule Background Jobs
    # Fetch data
    schedule.every(CRYPTO_POLL_INTERVAL).seconds.do(fetch_crypto_prices)
    schedule.every(STOCKS_POLL_INTERVAL).seconds.do(fetch_stock_prices)
    schedule.every(NEWS_POLL_INTERVAL).seconds.do(process_news_sentiment)
    
    # AI Tasks (Run frequently, they just process in-memory/DB data)
    schedule.every(1).minutes.do(check_all_assets_for_anomalies)
    schedule.every(5).minutes.do(generate_signals)
    
    # OLED Rendering
    # Rotate screens every 5 seconds
    schedule.every(5).seconds.do(render_next_screen)
    
    # 4. Start Flask in a background thread
    logger.info("Starting Flask API Server...")
    flask_thread = threading.Thread(target=start_flask, args=(API_HOST, API_PORT))
    flask_thread.daemon = True
    flask_thread.start()
    
    # 5. Start Telegram Bot in a background thread
    logger.info("Starting Telegram Bot Polling...")
    telegram_thread = threading.Thread(target=poll_telegram)
    telegram_thread.daemon = True
    telegram_thread.start()
    
    # 6. Enter main scheduling loop
    logger.info("Entering main event loop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("TinyTrade AI shutting down.")

if __name__ == "__main__":
    main_loop()
