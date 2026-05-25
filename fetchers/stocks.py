import requests
import json
import time
from config import NSE_BASE_URL, NSE_INDEX_API, NSE_MARQUEE_API, NSE_CACHE_TTL
from config import NSE_MOST_ACTIVE_API, NSE_GAINERS_API, NSE_LOSERS_API
from config import NSE_INDICES_CONFIG
from utils.helpers import setup_logger, is_nse_market_open
from database.db import update_market_data, update_nse_cache, get_nse_cache, update_marquee_stocks
from database.db import update_analysis_data

logger = setup_logger("StocksFetcher")

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.nseindia.com/"
}
session.headers.update(headers)


def _ensure_nse_session():
    if not session.cookies:
        try:
            logger.info("Initializing NSE Session Cookies...")
            session.get(NSE_BASE_URL, timeout=10)
        except Exception as e:
            logger.error("Failed to initialize NSE session: %s" % e)


def _fetch_with_cache(url, cache_key):
    cached = get_nse_cache(cache_key)
    now = int(time.time())

    if cached and (now - cached['updated_at']) < NSE_CACHE_TTL:
        logger.info("Using cached %s (age: %ds)" % (cache_key, now - cached['updated_at']))
        try:
            return json.loads(cached['data'])
        except (ValueError, TypeError):
            logger.warning("Cache corrupted for %s, re-fetching" % cache_key)

    _ensure_nse_session()
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        update_nse_cache(cache_key, json.dumps(data))
        logger.info("Fetched and cached %s" % cache_key)
        return data
    except requests.exceptions.RequestException as e:
        logger.error("HTTP error fetching %s: %s" % (cache_key, e))
        if cached:
            logger.info("Returning stale cache for %s" % cache_key)
            try:
                return json.loads(cached['data'])
            except (ValueError, TypeError):
                pass
    except Exception as e:
        logger.error("Error fetching %s: %s" % (cache_key, e))
    return None


def fetch_nse_indices():
    raw = _fetch_with_cache(NSE_INDEX_API, "nse_indices")
    if not raw:
        logger.warning("No index data received")
        return

    index_data_list = raw.get("data", [])
    if not index_data_list:
        logger.warning("No data array in getIndexData response")
        return

    for config in NSE_INDICES_CONFIG:
        target_name = config['name']
        display_symbol = config['symbol']

        matched = None
        for item in index_data_list:
            if item.get("indexName") == target_name:
                matched = item
                break

        if matched:
            price = matched.get("last", 0)
            change_pct = matched.get("percChange", 0)
            update_market_data(display_symbol, price, change_pct)
            logger.info("Updated %s: %.2f (%.2f%%)" % (display_symbol, price, change_pct))
        else:
            logger.warning("Index '%s' not found in API response" % target_name)


def fetch_marquee_data():
    raw = _fetch_with_cache(NSE_MARQUEE_API, "nse_marquee")
    if not raw:
        logger.warning("No marquee data received")
        return

    items = raw.get("data", [])
    if not items:
        logger.warning("No data array in getMarqueData response")
        return

    logger.info("Marquee data fetched: %d stocks" % len(items))
    # Store all marquee stocks for display rotation
    update_marquee_stocks(items)
    # Update first marquee item in market_data for backward compatibility
    if len(items) > 0:
        top = items[0]
        sym = top.get("symbol", "MARQ")
        price = top.get("lastTradedPrice", 0)
        chg = top.get("perChange", 0)
        update_market_data(sym, price, chg)
        logger.info("Top marquee: %s %.2f (%.2f%%)" % (sym, price, chg))


def fetch_stock_prices():
    if is_nse_market_open():
        logger.info("NSE market is OPEN - fetching live data")
    else:
        logger.info("NSE market CLOSED - fetching anyway (cached data may serve)")

    fetch_nse_indices()
    fetch_marquee_data()


def _fetch_and_store_analysis(url, cache_key, category):
    raw = _fetch_with_cache(url, cache_key)
    if raw is None:
        logger.warning("No data received for %s", category)
        return []
    items = raw.get("data", [])
    if not items:
        logger.warning("Empty data array for %s", category)
        return []
    import json
    update_analysis_data(category, json.dumps(items))
    logger.info("Stored %d items for %s", len(items), category)
    return items


def fetch_analysis_data():
    if not is_nse_market_open():
        logger.info("Market closed - skipping analysis data fetch")
        return

    logger.info("Fetching market analysis data (most active, gainers, losers)...")
    _fetch_and_store_analysis(NSE_MOST_ACTIVE_API, "nse_most_active", "most_active")
    _fetch_and_store_analysis(NSE_GAINERS_API, "nse_gainers", "gainers")
    _fetch_and_store_analysis(NSE_LOSERS_API, "nse_losers", "losers")
