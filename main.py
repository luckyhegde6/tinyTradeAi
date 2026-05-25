import threading
import time
import schedule

from config import CRYPTO_POLL_INTERVAL, STOCKS_POLL_INTERVAL, NEWS_POLL_INTERVAL, ANALYSIS_POLL_INTERVAL
from config import US_MARKET_POLL_INTERVAL, AI_SUGGESTION_INTERVAL
from config import API_HOST, API_PORT
from database.db import init_db
from utils.helpers import setup_logger, get_ip_address
from utils.config_manager import get as get_config
from fetchers.crypto import fetch_crypto_prices
from fetchers.stocks import fetch_stock_prices, fetch_analysis_data
from fetchers.us_markets import fetch_us_market_data
from fetchers.news import fetch_rss_headlines
from ai.sentiment import process_news_sentiment
from ai.anomaly import check_all_assets_for_anomalies
from ai.signals import generate_signals
from display.manager import init_displays, render_next_screen, show_boot_splash, check_display_health
from api.app import start_api, is_restart_requested
from api.telegram import poll_telegram

logger = setup_logger("TinyTrade_Main")

def main_loop():
    logger.info("Initializing TinyTrade AI...")

    # 1. Init Database
    init_db()

    # 2. Init Displays (auto-detect OLED and/or LCD)
    init_displays()

    # 2.5 Boot splash (welcome + IP on OLED)
    ip = get_ip_address()
    show_boot_splash(ip, duration=5)

    # 3. Initial Data Fetch
    logger.info("Performing initial data fetch...")
    fetch_crypto_prices()
    fetch_stock_prices()
    fetch_analysis_data()
    fetch_us_market_data()
    process_news_sentiment()
    generate_signals()

    # 4. Schedule Background Jobs
    schedule.every(CRYPTO_POLL_INTERVAL).seconds.do(fetch_crypto_prices)
    schedule.every(STOCKS_POLL_INTERVAL).seconds.do(fetch_stock_prices)
    schedule.every(ANALYSIS_POLL_INTERVAL).seconds.do(fetch_analysis_data)
    schedule.every(US_MARKET_POLL_INTERVAL).seconds.do(fetch_us_market_data)
    schedule.every(NEWS_POLL_INTERVAL).seconds.do(process_news_sentiment)
    schedule.every(AI_SUGGESTION_INTERVAL).seconds.do(generate_signals)

    # AI Tasks
    schedule.every(1).minutes.do(check_all_assets_for_anomalies)
    schedule.every(5).minutes.do(generate_signals)

    # Display health check
    schedule.every(1).minutes.do(check_display_health)

    # Display rendering
    schedule.every(5).seconds.do(render_next_screen)

    # 5. Start FastAPI in a background thread
    logger.info("Starting FastAPI Server...")
    api_thread = threading.Thread(target=start_api, args=(API_HOST, API_PORT))
    api_thread.daemon = True
    api_thread.start()

    # 6. Start Telegram Bot in a background thread
    logger.info("Starting Telegram Bot Polling...")
    telegram_thread = threading.Thread(target=poll_telegram)
    telegram_thread.daemon = True
    telegram_thread.start()

    # 7. Enter main scheduling loop
    logger.info("Entering main event loop.")
    try:
        while not is_restart_requested():
            schedule.run_pending()
            time.sleep(1)
        logger.info("Restart requested. Exiting main loop.")
    except KeyboardInterrupt:
        logger.info("TinyTrade AI shutting down.")

if __name__ == "__main__":
    main_loop()
